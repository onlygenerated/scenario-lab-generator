"""
Completion validation — checks learner work by running queries against target-db.

Runs validation queries via `docker compose exec` into the target database.
Uses a read-only Postgres role with a query timeout for safety.

Security:
  - Only SELECT queries allowed (enforced by blueprint schema + runtime check)
  - Queries run as read-only 'validator' role
  - 5-second statement timeout prevents resource exhaustion
  - Raw Postgres errors are sanitized before API response
"""

from __future__ import annotations

import logging
import re

from ..models.blueprint import ValidationQuery
from ..models.lab import LabSession, ValidationResult
from .orchestrator import get_lab_docker_client

logger = logging.getLogger(__name__)

# Maximum allowed query length
_MAX_QUERY_LENGTH = 4096

# Forbidden SQL keywords (runtime double-check beyond Pydantic validation)
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|GRANT|REVOKE|TRUNCATE|EXECUTE|MERGE|INTO)\b",
    re.IGNORECASE,
)


def _sanitize_error(error: str) -> str:
    """Remove potentially sensitive details from Postgres error messages."""
    # Strip file paths and line numbers
    sanitized = re.sub(r"(?:DETAIL|HINT|CONTEXT):.*", "", error)
    # Strip internal Postgres references
    sanitized = re.sub(r"(?:LINE \d+|POSITION \d+):.*", "", sanitized)
    # Truncate to reasonable length
    return sanitized.strip()[:500] if sanitized.strip() else "Query execution failed"


def _validate_query_safety(query: str) -> str | None:
    """
    Runtime safety check on a validation query.
    Returns an error message if unsafe, None if safe.
    """
    if len(query) > _MAX_QUERY_LENGTH:
        return f"Query exceeds maximum length of {_MAX_QUERY_LENGTH} characters"

    stripped = query.strip()
    if not stripped.upper().startswith("SELECT"):
        return "Query must start with SELECT"

    if _FORBIDDEN_KEYWORDS.search(stripped):
        return "Query contains forbidden SQL keywords"

    return None


def _run_validation_query(
    docker_client,
    query: ValidationQuery,
) -> ValidationResult:
    """Run a single validation query against the target DB via docker compose exec."""

    # Runtime safety check
    safety_error = _validate_query_safety(query.sql)
    if safety_error:
        return ValidationResult(
            query_name=query.query_name,
            passed=False,
            expected_row_count=query.expected_row_count,
            expected_columns=query.expected_columns,
            error=safety_error,
        )

    try:
        # Wrap query with statement timeout and run as validator role
        wrapped_sql = f"SET statement_timeout = '5s'; {query.sql}"

        # Execute via docker compose exec into target-db
        result = docker_client.compose.execute(
            "target-db",
            ["psql", "-U", "validator", "-d", "target_db", "-t", "-A", "-F", "|", "-c", wrapped_sql],
            tty=False,
        )

        output = result.strip() if result else ""

        # Parse psql output (pipe-delimited, no headers due to -t flag)
        # Filter out "SET" lines from SET statement_timeout command output
        rows = [
            line for line in output.split("\n")
            if line.strip() and line.strip() != "SET"
        ]

        actual_row_count = len(rows)

        # Parse column names from first row if available
        actual_columns: list[str] | None = None
        if rows:
            # Run a separate query to get column names
            col_query = f"SET statement_timeout = '5s'; SELECT * FROM ({query.sql}) AS _q LIMIT 0"
            col_result = docker_client.compose.execute(
                "target-db",
                ["psql", "-U", "validator", "-d", "target_db", "-A", "-F", "|", "-c", col_query],
                tty=False,
            )
            col_output = col_result.strip() if col_result else ""
            # Filter out "SET" responses and "(0 rows)" footer to find the header line
            col_lines = [
                line for line in col_output.split("\n")
                if line.strip()
                and line.strip() != "SET"
                and not line.startswith("(")
            ]
            if col_lines:
                actual_columns = col_lines[0].split("|")

        # Check pass/fail
        row_count_ok = actual_row_count == query.expected_row_count
        columns_ok = True
        if actual_columns:
            columns_ok = set(query.expected_columns) <= set(actual_columns)

        passed = row_count_ok and columns_ok

        return ValidationResult(
            query_name=query.query_name,
            passed=passed,
            expected_row_count=query.expected_row_count,
            actual_row_count=actual_row_count,
            expected_columns=query.expected_columns,
            actual_columns=actual_columns,
            error=None if passed else (
                f"Expected {query.expected_row_count} rows, got {actual_row_count}"
                if not row_count_ok
                else f"Missing columns: {set(query.expected_columns) - set(actual_columns or [])}"
            ),
        )

    except Exception as e:
        logger.warning("Validation query failed: %s", e)
        return ValidationResult(
            query_name=query.query_name,
            passed=False,
            expected_row_count=query.expected_row_count,
            expected_columns=query.expected_columns,
            error=_sanitize_error(str(e)),
        )


def validate_lab(session: LabSession) -> list[ValidationResult]:
    """Run all validation queries for a lab session."""
    docker = get_lab_docker_client(session)
    if not docker:
        raise RuntimeError("Cannot connect to lab Docker environment")

    results = []
    for query in session.blueprint.validation_queries:
        result = _run_validation_query(docker, query)
        results.append(result)

    return results
