"""
Self-test orchestrator — launches a headless lab, runs the solution, validates, and keeps or tears down.

Workflow:
  1. launch_lab() — full Docker stack
  2. Wait for databases to be ready (pg_isready)
  3. Wait briefly for Jupyter container
  4. Generate and execute solution script
  5. Run validation queries
  6. If all pass: wipe target tables, return session for reuse
  7. If any fail: stop_lab(), return failure details
"""

from __future__ import annotations

import logging
import time

from python_on_whales import DockerClient

from ..models.blueprint import ScenarioBlueprint
from ..models.lab import LabSession, LabStatus, ValidationResult
from . import orchestrator, validator
from .generator import repair_blueprint
from .solution_runner import (
    execute_solution_in_lab,
    generate_solution_script,
    wipe_target_tables,
)

logger = logging.getLogger(__name__)

# Timeouts
_DB_READY_TIMEOUT_S = 120
_DB_POLL_INTERVAL_S = 2
_JUPYTER_SETTLE_S = 5


def _wait_for_db(docker: DockerClient, service: str, db_name: str, timeout: int = _DB_READY_TIMEOUT_S) -> bool:
    """Poll pg_isready until the database is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            result = docker.compose.execute(
                service,
                ["pg_isready", "-U", "labuser", "-d", db_name],
                tty=False,
            )
            if result and "accepting connections" in result:
                return True
        except Exception:
            pass
        time.sleep(_DB_POLL_INTERVAL_S)
    return False


def _collect_row_count_failures(
    results: list[ValidationResult],
    blueprint: ScenarioBlueprint,
) -> list[dict[str, object]]:
    """Extract row-count failures with query SQL for the repair prompt."""
    failures = []
    query_by_name = {q.query_name: q for q in blueprint.validation_queries}
    for r in results:
        if not r.passed and r.actual_row_count is not None:
            query = query_by_name.get(r.query_name)
            failures.append({
                "query_name": r.query_name,
                "expected": r.expected_row_count,
                "actual": r.actual_row_count,
                "sql": query.sql[:200] if query else None,
            })
    return failures


def run_self_test(
    blueprint: ScenarioBlueprint,
    max_retries: int = 1,
) -> tuple[bool, LabSession | None, list[ValidationResult], str | None]:
    """
    Self-test a blueprint by launching a lab, solving it, and validating.

    If validation fails due to wrong expected_row_count values, attempts to
    repair the blueprint via a second AI call and re-test (up to max_retries).

    Returns:
        (passed, session_or_none, validation_results, error_message_or_none)

    If passed is True, session is a running lab with target tables wiped (ready for reuse).
    If passed is False, session is torn down and returned as None.
    """
    current_blueprint = blueprint
    attempt = 0

    while attempt <= max_retries:
        session: LabSession | None = None
        attempt += 1

        try:
            # 1. Launch the full Docker stack
            logger.info("Self-test (attempt %d/%d): launching lab...", attempt, max_retries + 1)
            session = orchestrator.launch_lab(current_blueprint)

            if session.status == LabStatus.error:
                return False, None, [], f"Lab launch failed: {session.error_message}"

            docker = orchestrator.get_lab_docker_client(session)
            if not docker:
                orchestrator.stop_lab(session)
                return False, None, [], "Could not get Docker client for lab"

            # 2. Wait for both databases to be ready
            logger.info("Self-test: waiting for databases...")
            if not _wait_for_db(docker, "source-db", "source_db"):
                orchestrator.stop_lab(session)
                return False, None, [], "Source database did not become ready in time"

            if not _wait_for_db(docker, "target-db", "target_db"):
                orchestrator.stop_lab(session)
                return False, None, [], "Target database did not become ready in time"

            # 3. Brief delay for Jupyter container to finish startup
            logger.info("Self-test: waiting for Jupyter container...")
            time.sleep(_JUPYTER_SETTLE_S)

            # 4. Generate and execute the solution
            logger.info("Self-test: running solution script...")
            script = generate_solution_script(current_blueprint)
            success, output = execute_solution_in_lab(session, docker, script)

            if not success:
                logger.warning("Self-test: solution execution failed. Output: %s", output[:2000])
                orchestrator.stop_lab(session)
                return False, None, [], f"Solution script failed: {output[:2000]}"

            # 5. Run validation queries
            logger.info("Self-test: running validation queries...")
            results = validator.validate_lab(session)
            all_passed = all(r.passed for r in results)

            if all_passed:
                # 6. All passed! Wipe target tables so student starts fresh
                logger.info("Self-test: wiping target tables for student...")
                wipe_target_tables(current_blueprint, docker)
                logger.info("Self-test: PASSED. Lab %s ready for reuse.", session.lab_id)
                return True, session, results, None

            # Validation failed — try repair if retries remain
            failed = [r for r in results if not r.passed]
            details = "; ".join(
                f"{r.query_name}: {r.error or 'failed'}" for r in failed
            )
            logger.warning("Self-test: validation failed: %s", details)
            orchestrator.stop_lab(session)
            session = None

            if attempt <= max_retries:
                row_failures = _collect_row_count_failures(results, current_blueprint)
                if not row_failures:
                    # Non-row-count failures can't be repaired this way
                    return False, None, results, f"Validation failed: {details}"

                logger.info(
                    "Self-test: attempting repair (%d row-count failure(s))...",
                    len(row_failures),
                )
                try:
                    current_blueprint = repair_blueprint(current_blueprint, row_failures)
                except Exception as repair_err:
                    logger.warning("Self-test: repair failed: %s", repair_err)
                    return False, None, results, f"Validation failed: {details}"
            else:
                return False, None, results, f"Validation failed: {details}"

        except Exception as e:
            logger.exception("Self-test: unexpected error")
            if session and session.status == LabStatus.running:
                try:
                    orchestrator.stop_lab(session)
                except Exception:
                    pass
            return False, None, [], f"Unexpected error: {str(e)}"

    # Should not reach here, but just in case
    return False, None, [], "Self-test exhausted all retries"
