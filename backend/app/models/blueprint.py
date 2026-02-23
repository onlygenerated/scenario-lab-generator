"""
ScenarioBlueprint — the core contract between AI generator, Docker orchestrator, and validator.

This Pydantic model is passed directly to `client.messages.parse(output_format=ScenarioBlueprint)`.
Claude fills it in, Pydantic validates it.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

# Strict identifier pattern: lowercase alpha start, then alphanumeric/underscores, max 63 chars
_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]{0,62}$")

# SQL keywords that must never appear as table/column identifiers
_SQL_KEYWORDS = frozenset({
    "select", "insert", "update", "delete", "drop", "alter", "create",
    "grant", "revoke", "truncate", "execute", "merge", "replace",
    "union", "intersect", "except", "from", "where", "join", "table",
    "index", "view", "trigger", "procedure", "function", "database",
    "schema", "cascade", "restrict", "references", "foreign", "primary",
    "key", "constraint", "check", "default", "null", "not", "and", "or",
})


def _validate_identifier(value: str, field_label: str) -> str:
    """Validate a SQL identifier is safe: matches pattern and is not a SQL keyword."""
    if not _IDENTIFIER_RE.match(value):
        raise ValueError(
            f"{field_label} '{value}' must match ^[a-z][a-z0-9_]{{0,62}}$"
        )
    if value in _SQL_KEYWORDS:
        raise ValueError(
            f"{field_label} '{value}' is a reserved SQL keyword and cannot be used as an identifier"
        )
    return value


class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class ColumnDataType(str, Enum):
    """Constrained set of Postgres data types for generated columns."""
    integer = "INTEGER"
    bigint = "BIGINT"
    serial = "SERIAL"
    text = "TEXT"
    varchar = "VARCHAR(255)"
    boolean = "BOOLEAN"
    date = "DATE"
    timestamp = "TIMESTAMP"
    numeric = "NUMERIC(12,2)"
    json = "JSON"


class ColumnDefinition(BaseModel):
    """A single column in a source or target table."""
    name: str = Field(..., description="Column name (lowercase, no SQL keywords)")
    data_type: ColumnDataType = Field(..., description="Postgres data type")
    nullable: bool = Field(default=True, description="Whether the column allows NULLs")
    is_primary_key: bool = Field(default=False, description="Whether this is a primary key")
    description: str = Field(default="", description="Brief description of what this column represents")

    @field_validator("name")
    @classmethod
    def validate_column_name(cls, v: str) -> str:
        return _validate_identifier(v, "Column name")


class SourceTable(BaseModel):
    """A source table with schema and sample data for the lab."""
    table_name: str = Field(..., description="Table name (lowercase, no SQL keywords)")
    description: str = Field(..., description="What this table represents in the business context")
    columns: list[ColumnDefinition] = Field(
        ..., min_length=1, max_length=20,
        description="Column definitions for this table"
    )
    sample_data: list[dict[str, str | int | float | bool | None]] = Field(
        ..., min_length=3, max_length=20,
        description="Sample data rows (3-20 rows). Keys must match column names."
    )

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        return _validate_identifier(v, "Table name")


class TargetTable(BaseModel):
    """A target table the learner must populate — schema only, no data."""
    table_name: str = Field(..., description="Table name (lowercase, no SQL keywords)")
    description: str = Field(..., description="What this table should contain after the ETL")
    columns: list[ColumnDefinition] = Field(
        ..., min_length=1, max_length=20,
        description="Column definitions for the target table"
    )

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        return _validate_identifier(v, "Table name")


class TransformationStep(BaseModel):
    """A numbered step in the ETL transformation the learner must perform."""
    step_number: int = Field(..., ge=1, le=20, description="Step order (1-based)")
    title: str = Field(..., max_length=200, description="Short title for this step")
    description: str = Field(..., description="Detailed description of what to do")
    hint: str = Field(default="", description="Optional hint if the learner is stuck")
    solution_code: str = Field(default="", description="Working Python code for this step (for self-test)")
    skill_tags: list[str] = Field(
        default_factory=list, max_length=5,
        description="Skills practiced in this step (e.g., 'JOIN', 'AGGREGATION', 'WINDOW_FUNCTION')"
    )


class ValidationQuery(BaseModel):
    """A SQL query used to automatically validate the learner's work."""
    query_name: str = Field(..., max_length=200, description="Human-readable name for this check")
    sql: str = Field(..., description="SELECT query to run against the target database")
    expected_row_count: int = Field(..., ge=0, description="Expected number of rows returned")
    expected_columns: list[str] = Field(
        ..., min_length=1,
        description="Column names expected in the result set"
    )
    description: str = Field(default="", description="What this validation checks")

    @field_validator("sql")
    @classmethod
    def validate_sql_is_select_only(cls, v: str) -> str:
        """Ensure validation queries are SELECT-only — no DML/DDL."""
        normalized = v.strip().upper()
        if not normalized.startswith("SELECT"):
            raise ValueError("Validation queries must start with SELECT")

        dangerous_keywords = {
            "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
            "GRANT", "REVOKE", "TRUNCATE", "EXECUTE", "MERGE",
            "INTO",  # catches SELECT INTO
        }
        # Tokenize: split on whitespace and common delimiters to find keywords
        tokens = set(re.findall(r"[A-Z_]+", normalized))
        found_dangerous = tokens & dangerous_keywords
        if found_dangerous:
            raise ValueError(
                f"Validation queries must be SELECT-only. "
                f"Found forbidden keywords: {found_dangerous}"
            )
        return v


class ScenarioBlueprint(BaseModel):
    """
    The complete blueprint for a scenario-based lab.

    This is THE core contract — the AI generator produces it,
    the orchestrator provisions containers from it,
    and the validator grades learner work against it.
    """
    # Scenario metadata
    title: str = Field(..., max_length=200, description="Scenario title")
    description: str = Field(..., description="Brief scenario description (2-3 sentences)")
    difficulty: Difficulty = Field(..., description="Difficulty level")
    estimated_minutes: int = Field(..., ge=10, le=180, description="Estimated completion time")
    learning_objectives: list[str] = Field(
        ..., min_length=1, max_length=5,
        description="What the learner will practice/demonstrate"
    )
    business_context: str = Field(
        ...,
        description="A realistic business scenario that motivates the ETL task"
    )

    # Data architecture
    source_tables: list[SourceTable] = Field(
        ..., min_length=1, max_length=5,
        description="Source tables with sample data"
    )
    target_tables: list[TargetTable] = Field(
        ..., min_length=1, max_length=5,
        description="Target tables the learner must populate"
    )

    # Transformation guide
    transformation_steps: list[TransformationStep] = Field(
        ..., min_length=1, max_length=20,
        description="Ordered steps to transform source data into target schema"
    )

    # Automated validation
    validation_queries: list[ValidationQuery] = Field(
        ..., min_length=1, max_length=10,
        description="SELECT queries to verify the learner's work"
    )

    # Lab instructions (Markdown)
    lab_instructions: str = Field(
        ...,
        description="Full Markdown lab instructions for the learner"
    )
