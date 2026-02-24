"""API routes for ScenarioLabGenerator."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..models.api_models import (
    GenerateRequest,
    GenerateResponse,
    LabListResponse,
    LabStatusResponse,
    LaunchRequest,
    LaunchResponse,
    SelfTestRequest,
    SelfTestResponse,
    StopResponse,
    ValidateResponse,
)
from ..models.blueprint import ScenarioBlueprint
from ..models.lab import LabSession, LabStatus
from ..services import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory lab session store (sufficient for PoC)
_lab_sessions: dict[str, LabSession] = {}

DEMO_BLUEPRINT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "demo" / "sample_blueprint.json"


def get_lab_sessions() -> dict[str, LabSession]:
    """Expose sessions dict for use by other modules (e.g. validator)."""
    return _lab_sessions


def _load_demo_blueprint() -> GenerateResponse:
    """Load the handcrafted demo blueprint from disk (sync helper)."""
    if not DEMO_BLUEPRINT_PATH.exists():
        raise HTTPException(status_code=404, detail="Demo blueprint not found")
    raw = json.loads(DEMO_BLUEPRINT_PATH.read_text(encoding="utf-8"))
    blueprint = ScenarioBlueprint.model_validate(raw)
    return GenerateResponse(blueprint=blueprint)


# --- Demo endpoints ---

@router.get("/demos/blueprint", response_model=GenerateResponse)
async def get_demo_blueprint() -> GenerateResponse:
    """Return the handcrafted demo blueprint for testing without AI."""
    return _load_demo_blueprint()


# --- Scenario generation ---
# NOTE: def (not async def) — generate_blueprint() is a blocking Claude API call.
# FastAPI runs sync endpoints in a threadpool, keeping the event loop responsive.

@router.post("/scenarios/generate", response_model=GenerateResponse)
def generate_scenario(request: GenerateRequest) -> GenerateResponse:
    """Generate a new scenario blueprint via Claude AI."""
    from ..config import settings

    logger.info(
        "Generate request: difficulty=%s, tables=%d, skills=%s, industry=%s",
        request.difficulty, request.num_source_tables, request.focus_skills, request.industry,
    )

    if settings.demo_mode:
        logger.info("Demo mode — returning sample blueprint")
        return _load_demo_blueprint()

    from ..services.generator import generate_blueprint

    try:
        blueprint = generate_blueprint(request)
        logger.info("Generation complete: '%s' (%d source tables)", blueprint.title, len(blueprint.source_tables))
        return GenerateResponse(blueprint=blueprint)
    except RuntimeError as e:
        status = 429 if "Rate limit" in str(e) else 500
        raise HTTPException(status_code=status, detail=str(e)) from e
    except Exception as e:
        logger.exception("Scenario generation failed")
        raise HTTPException(status_code=500, detail="Internal error during generation") from e


# --- Self-test ---
# NOTE: def (not async def) — run_self_test() blocks for 30-120s (Docker launch,
# DB wait, script exec, validation). Must run in threadpool to avoid freezing the event loop.

@router.post("/scenarios/self-test", response_model=SelfTestResponse)
def self_test_scenario(request: SelfTestRequest) -> SelfTestResponse:
    """Self-test a blueprint: launch lab, run solution, validate, keep or teardown."""
    from ..services.self_test import run_self_test

    try:
        passed, session, results, error = run_self_test(request.blueprint)

        if passed and session:
            # Register the session so existing /labs/{id}/* endpoints work on it
            _lab_sessions[session.lab_id] = session
            return SelfTestResponse(
                passed=True,
                lab_id=session.lab_id,
                jupyter_url=session.jupyter_url,
                validation_results=results,
            )

        return SelfTestResponse(
            passed=False,
            validation_results=results,
            error=error,
        )

    except Exception as e:
        logger.exception("Self-test failed")
        raise HTTPException(status_code=500, detail=f"Self-test error: {str(e)}") from e


# --- Lab lifecycle ---
# NOTE: def (not async def) — Docker CLI calls block.

@router.post("/labs/launch", response_model=LaunchResponse)
def launch_lab_endpoint(request: LaunchRequest) -> LaunchResponse:
    """Launch a lab environment from a blueprint."""
    try:
        session = orchestrator.launch_lab(request.blueprint)
        _lab_sessions[session.lab_id] = session

        if session.status == LabStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to launch lab: {session.error_message}",
            )

        return LaunchResponse(
            lab_id=session.lab_id,
            status=session.status,
            jupyter_url=session.jupyter_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error launching lab")
        raise HTTPException(status_code=500, detail="Internal error launching lab") from e


@router.get("/labs", response_model=LabListResponse)
async def list_labs() -> LabListResponse:
    """List all lab sessions."""
    labs = [
        LabStatusResponse(
            lab_id=session.lab_id,
            status=session.status,
            jupyter_url=session.jupyter_url,
            error_message=session.error_message,
        )
        for session in _lab_sessions.values()
    ]
    return LabListResponse(labs=labs)


@router.get("/labs/{lab_id}", response_model=LabStatusResponse)
async def get_lab_status(lab_id: str) -> LabStatusResponse:
    """Get the status of a specific lab session."""
    session = _lab_sessions.get(lab_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found")
    return LabStatusResponse(
        lab_id=session.lab_id,
        status=session.status,
        jupyter_url=session.jupyter_url,
        error_message=session.error_message,
    )


@router.post("/labs/{lab_id}/validate", response_model=ValidateResponse)
def validate_lab(lab_id: str) -> ValidateResponse:
    """Validate the learner's work in a lab."""
    session = _lab_sessions.get(lab_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found")
    if session.status != LabStatus.running:
        raise HTTPException(status_code=400, detail="Lab is not running")

    from ..services import validator as validator_svc

    try:
        results = validator_svc.validate_lab(session)
        session.validation_results = results
        all_passed = all(r.passed for r in results)

        return ValidateResponse(
            lab_id=lab_id,
            all_passed=all_passed,
            results=results,
        )
    except Exception as e:
        logger.exception("Validation error")
        raise HTTPException(status_code=500, detail="Internal error during validation") from e


@router.post("/labs/{lab_id}/stop", response_model=StopResponse)
def stop_lab_endpoint(lab_id: str) -> StopResponse:
    """Stop and clean up a lab environment."""
    session = _lab_sessions.get(lab_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found")

    try:
        session = orchestrator.stop_lab(session)
        _lab_sessions[lab_id] = session

        return StopResponse(lab_id=lab_id, status=session.status)
    except Exception as e:
        logger.exception("Error stopping lab")
        raise HTTPException(status_code=500, detail="Internal error stopping lab") from e
