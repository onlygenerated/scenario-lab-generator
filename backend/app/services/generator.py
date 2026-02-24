"""
AI scenario generator using Anthropic Claude API with structured outputs.

Uses `client.messages.create()` with a tool-based approach to guarantee
the response conforms to the ScenarioBlueprint Pydantic model.
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque

import anthropic
import httpx

from ..config import settings
from ..models.api_models import GenerateRequest
from ..models.blueprint import ScenarioBlueprint
from ..prompts.data_pipeline import (
    REPAIR_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_repair_prompt,
    build_user_prompt,
)

logger = logging.getLogger(__name__)

# Simple in-memory rate limiter
_request_timestamps: deque[float] = deque()


def _check_rate_limit() -> None:
    """Enforce rate limiting on the generate endpoint."""
    now = time.time()
    window = 60.0  # 1 minute window

    # Remove timestamps older than the window
    while _request_timestamps and _request_timestamps[0] < now - window:
        _request_timestamps.popleft()

    if len(_request_timestamps) >= settings.generate_rate_limit_per_minute:
        raise RuntimeError(
            f"Rate limit exceeded: max {settings.generate_rate_limit_per_minute} "
            f"requests per minute"
        )

    _request_timestamps.append(now)


def _validate_blueprint_security(blueprint: ScenarioBlueprint) -> None:
    """
    Additional security validation on AI-generated blueprints.

    Catches issues that Pydantic field validators might not:
    - Excessively large data (resource exhaustion)
    - Suspicious patterns in sample data values
    """
    # Check total data volume
    total_rows = sum(len(t.sample_data) for t in blueprint.source_tables)
    if total_rows > 100:
        raise ValueError(f"Blueprint has {total_rows} total sample rows (max 100)")

    total_columns = sum(len(t.columns) for t in blueprint.source_tables)
    total_columns += sum(len(t.columns) for t in blueprint.target_tables)
    if total_columns > 50:
        raise ValueError(f"Blueprint has {total_columns} total columns (max 50)")

    # Check sample data values for suspicious content
    for table in blueprint.source_tables:
        for row in table.sample_data:
            for key, value in row.items():
                if isinstance(value, str) and len(value) > 1000:
                    raise ValueError(
                        f"Sample data value in {table.table_name}.{key} "
                        f"exceeds 1000 characters"
                    )

    # Validation queries are already checked by Pydantic validators
    # but double-check count
    if len(blueprint.validation_queries) > 10:
        raise ValueError("Too many validation queries (max 10)")


def generate_blueprint(request: GenerateRequest) -> ScenarioBlueprint:
    """
    Generate a ScenarioBlueprint using Claude API with structured outputs.
    """
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    _check_rate_limit()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    user_prompt = build_user_prompt(
        difficulty=request.difficulty.value,
        num_source_tables=request.num_source_tables,
        focus_skills=request.focus_skills,
        industry=request.industry,
    )

    # Get the JSON schema from the Pydantic model
    schema = ScenarioBlueprint.model_json_schema()

    logger.info("Generating scenario: difficulty=%s, industry=%s", request.difficulty, request.industry)

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[
            {
                "name": "create_scenario_blueprint",
                "description": "Create a complete scenario blueprint for a data pipeline lab",
                "input_schema": schema,
            }
        ],
        tool_choice={"type": "tool", "name": "create_scenario_blueprint"},
        timeout=httpx.Timeout(600.0, connect=10.0),
    )

    # Detect truncated output before attempting to parse
    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            "Blueprint generation was truncated (hit max_tokens). "
            "Try reducing the number of source tables or focus skills."
        )

    # Extract the tool use result
    for block in response.content:
        if block.type == "tool_use" and block.name == "create_scenario_blueprint":
            # Validate through Pydantic
            blueprint = ScenarioBlueprint.model_validate(block.input)

            # Additional security checks
            _validate_blueprint_security(blueprint)

            logger.info("Generated scenario: %s", blueprint.title)
            return blueprint

    raise RuntimeError("Claude did not return a tool use response")


def repair_blueprint(
    blueprint: ScenarioBlueprint,
    failures: list[dict[str, object]],
) -> ScenarioBlueprint:
    """
    Ask Claude to fix a blueprint whose validation queries returned wrong row counts.

    Takes the original blueprint + list of failures (query_name, expected, actual, sql)
    and returns a corrected blueprint through the same validation pipeline.
    """
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    _check_rate_limit()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    user_prompt = build_repair_prompt(blueprint, failures)
    schema = ScenarioBlueprint.model_json_schema()

    logger.info("Repairing blueprint: %d failure(s)", len(failures))

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        system=REPAIR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[
            {
                "name": "create_scenario_blueprint",
                "description": "Return the corrected scenario blueprint",
                "input_schema": schema,
            }
        ],
        tool_choice={"type": "tool", "name": "create_scenario_blueprint"},
        timeout=httpx.Timeout(600.0, connect=10.0),
    )

    if response.stop_reason == "max_tokens":
        raise RuntimeError("Blueprint repair was truncated (hit max_tokens)")

    for block in response.content:
        if block.type == "tool_use" and block.name == "create_scenario_blueprint":
            repaired = ScenarioBlueprint.model_validate(block.input)
            _validate_blueprint_security(repaired)
            logger.info("Blueprint repaired successfully")
            return repaired

    raise RuntimeError("Claude did not return a tool use response for repair")
