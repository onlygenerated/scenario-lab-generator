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


# --- Demo endpoints ---

@router.get("/demos/blueprint", response_model=GenerateResponse)
async def get_demo_blueprint() -> GenerateResponse:
    """Return the handcrafted demo blueprint for testing without AI."""
    if not DEMO_BLUEPRINT_PATH.exists():
        raise HTTPException(status_code=404, detail="Demo blueprint not found")
    raw = json.loads(DEMO_BLUEPRINT_PATH.read_text(encoding="utf-8"))
    blueprint = ScenarioBlueprint.model_validate(raw)
    return GenerateResponse(blueprint=blueprint)


# --- Scenario generation ---

@router.post("/scenarios/generate", response_model=GenerateResponse)
async def generate_scenario(request: GenerateRequest) -> GenerateResponse:
    """Generate a new scenario blueprint via Claude AI."""
    from ..config import settings

    if settings.demo_mode:
        return await get_demo_blueprint()

    from ..services.generator import generate_blueprint

    try:
        blueprint = generate_blueprint(request)
        return GenerateResponse(blueprint=blueprint)
    except RuntimeError as e:
        status = 429 if "Rate limit" in str(e) else 500
        raise HTTPException(status_code=status, detail=str(e)) from e
    except Exception as e:
        logger.exception("Scenario generation failed")
        raise HTTPException(status_code=500, detail="Internal error during generation") from e


# --- Lab lifecycle ---

@router.post("/labs/launch", response_model=LaunchResponse)
async def launch_lab_endpoint(request: LaunchRequest) -> LaunchResponse:
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
async def validate_lab(lab_id: str) -> ValidateResponse:
    """Validate the learner's work in a lab."""
    session = _lab_sessions.get(lab_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found")
    if session.status != LabStatus.running:
        raise HTTPException(status_code=400, detail="Lab is not running")

    # Phase 3 will implement the actual validation
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
async def stop_lab_endpoint(lab_id: str) -> StopResponse:
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
