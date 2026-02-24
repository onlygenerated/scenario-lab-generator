"""Lab session state — tracks a running lab environment."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from .blueprint import ScenarioBlueprint


class LabStatus(str, Enum):
    pending = "pending"
    starting = "starting"
    running = "running"
    stopping = "stopping"
    stopped = "stopped"
    error = "error"


class FeedbackItem(BaseModel):
    """AI-generated feedback for a single failed validation check."""
    query_name: str
    diagnosis: str    # What went wrong (2-3 sentences)
    suggestion: str   # How to fix it without giving code


class ValidationResult(BaseModel):
    """Result of a single validation query."""
    query_name: str
    passed: bool
    expected_row_count: int
    actual_row_count: int | None = None
    expected_columns: list[str]
    actual_columns: list[str] | None = None
    error: str | None = None
    feedback: FeedbackItem | None = None


class LabSession(BaseModel):
    """Represents a running (or stopped) lab environment."""
    lab_id: str = Field(default_factory=lambda: str(uuid4()))
    status: LabStatus = Field(default=LabStatus.pending)
    blueprint: ScenarioBlueprint
    jupyter_port: int | None = None
    jupyter_url: str | None = None
    compose_project_name: str | None = None
    lab_dir: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    validation_results: list[ValidationResult] | None = None
    error_message: str | None = None
