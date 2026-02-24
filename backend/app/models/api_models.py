"""Request and response models for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .blueprint import Difficulty, ScenarioBlueprint
from .lab import FeedbackItem, LabSession, LabStatus, ValidationResult


# --- Scenario generation ---

class GenerateRequest(BaseModel):
    """Parameters for generating a new scenario blueprint."""
    difficulty: Difficulty = Field(default=Difficulty.intermediate)
    num_source_tables: int = Field(default=2, ge=1, le=5)
    focus_skills: list[str] = Field(
        default_factory=lambda: ["JOIN", "AGGREGATION"],
        max_length=10,
        description="Skills to emphasize (e.g., JOIN, WINDOW_FUNCTION, PIVOT, CLEANING)"
    )
    industry: str = Field(
        default="retail",
        max_length=100,
        description="Business domain for the scenario (e.g., retail, healthcare, finance)"
    )


class GenerateResponse(BaseModel):
    """Response after scenario generation."""
    blueprint: ScenarioBlueprint


# --- Lab lifecycle ---

class LaunchRequest(BaseModel):
    """Request to launch a lab from a blueprint."""
    blueprint: ScenarioBlueprint


class LaunchResponse(BaseModel):
    """Response after lab launch."""
    lab_id: str
    status: LabStatus
    jupyter_url: str | None = None


class LabStatusResponse(BaseModel):
    """Current status of a lab session."""
    lab_id: str
    status: LabStatus
    jupyter_url: str | None = None
    error_message: str | None = None


# --- Validation ---

class ValidateResponse(BaseModel):
    """Results of validating learner work."""
    lab_id: str
    all_passed: bool
    results: list[ValidationResult]


# --- Feedback ---

class FeedbackResponse(BaseModel):
    """AI-generated feedback for failed validation checks."""
    lab_id: str
    feedback: list[FeedbackItem]


# --- Self-test ---

class SelfTestRequest(BaseModel):
    """Request to self-test a blueprint."""
    blueprint: ScenarioBlueprint


class SelfTestResponse(BaseModel):
    """Response after self-testing a blueprint."""
    passed: bool
    lab_id: str | None = None
    jupyter_url: str | None = None
    validation_results: list[ValidationResult] = Field(default_factory=list)
    error: str | None = None


# --- Lab management ---

class StopResponse(BaseModel):
    """Response after stopping a lab."""
    lab_id: str
    status: LabStatus


class LabListResponse(BaseModel):
    """List of all lab sessions."""
    labs: list[LabStatusResponse]
