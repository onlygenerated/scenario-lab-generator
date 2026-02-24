"""
Solution runner — generates and executes a self-test Python script in the lab container.

Three functions:
  1. generate_solution_script() — builds a .py file from blueprint solution_code or heuristics
  2. execute_solution_in_lab() — runs the script inside the Jupyter container via stdin
  3. wipe_target_tables() — TRUNCATEs target tables so the student starts fresh
"""

from __future__ import annotations

import json
import logging
import re as _re
import subprocess
from pathlib import Path

from python_on_whales import DockerClient

from ..models.blueprint import ScenarioBlueprint
from ..models.lab import LabSession
from .notebook_generator import generate_solution_notebook

logger = logging.getLogger(__name__)

# Marker printed by the script on success
_SUCCESS_MARKER = "===SELF_TEST_SOLUTION_OK==="

# Modules that AI-generated solution code should never import.
# Not bulletproof, but catches the obvious cases before container execution.
_BLOCKED_IMPORTS = ["os", "subprocess", "socket", "shutil", "sys"]

# Dangerous builtins to reject (matched with word-boundary regex)
_BLOCKED_CALLS = ["open", "exec", "eval", "__import__"]


def _check_solution_safety(script: str) -> str | None:
    """Return an error message if the solution script contains blocked patterns, else None."""
    for mod in _BLOCKED_IMPORTS:
        if f"import {mod}" in script or f"from {mod} " in script:
            return f"Solution code contains blocked import: '{mod}'"

    for func in _BLOCKED_CALLS:
        # Match "open(" but not "if_exists=" or "execute" — require word boundary before
        if _re.search(rf"(?<![a-zA-Z_.]){_re.escape(func)}\s*\(", script):
            return f"Solution code contains blocked call: '{func}('"

    return None


def generate_solution_script(blueprint: ScenarioBlueprint) -> str:
    """
    Produce a self-contained Python script that solves the lab.

    If any transformation step has solution_code, uses those directly.
    Otherwise, extracts code cells from the heuristic solution notebook.
    """
    has_solution_code = any(
        step.solution_code.strip() for step in blueprint.transformation_steps
    )

    if has_solution_code:
        return _script_from_solution_code(blueprint)
    return _script_from_notebook(blueprint)


def _script_from_solution_code(blueprint: ScenarioBlueprint) -> str:
    """Build script from explicit solution_code fields on each step."""
    lines = [
        "import pandas as pd",
        "from sqlalchemy import create_engine",
        "",
        "source_engine = create_engine('postgresql://labuser:labpass@source-db:5432/source_db')",
        "target_engine = create_engine('postgresql://labuser:labpass@target-db:5432/target_db')",
        "",
    ]

    for step in blueprint.transformation_steps:
        code = step.solution_code.strip()
        if not code:
            continue
        lines.append(f"# Step {step.step_number}: {step.title}")
        lines.append(code)
        lines.append("")

    lines.append(f"print('{_SUCCESS_MARKER}')")
    return "\n".join(lines)


def _script_from_notebook(blueprint: ScenarioBlueprint) -> str:
    """Extract code cells from the heuristic solution notebook."""
    notebook_json = generate_solution_notebook(blueprint)
    notebook = json.loads(notebook_json)

    lines = []
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        # cell["source"] is a list of lines (with newlines)
        source = "".join(cell["source"])
        lines.append(source)
        lines.append("")

    lines.append(f"print('{_SUCCESS_MARKER}')")
    return "\n".join(lines)


def execute_solution_in_lab(
    session: LabSession,
    docker: DockerClient,
    script: str,
) -> tuple[bool, str]:
    """
    Pipe the solution script via stdin into `python -` inside the Jupyter container.

    Uses subprocess directly (instead of writing a .py file to the mounted workspace)
    to avoid triggering uvicorn's file watcher during --reload.

    Returns (success, output).
    """
    if not session.lab_dir:
        return False, "Lab directory not set"

    safety_error = _check_solution_safety(script)
    if safety_error:
        logger.warning("Solution safety check failed: %s", safety_error)
        return False, safety_error

    try:
        compose_file = str(Path(session.lab_dir) / "docker-compose.yml")
        project_name = session.compose_project_name or ""

        cmd = [
            str(docker.client_config.docker_cmd[0]),
            "compose",
            "--file", compose_file,
            "--project-name", project_name,
            "exec", "-T",
            "jupyter",
            "python", "-",
        ]

        completed = subprocess.run(
            cmd,
            input=script.encode("utf-8"),
            capture_output=True,
            timeout=120,
        )

        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()

        if completed.returncode != 0:
            logger.warning("Solution execution failed (rc=%d): %s", completed.returncode, stderr[:2000])
            return False, stderr[:2000] if stderr else f"Exit code {completed.returncode}"

        success = _SUCCESS_MARKER in stdout
        return success, stdout

    except subprocess.TimeoutExpired:
        logger.warning("Solution execution timed out")
        return False, "Solution script timed out after 120s"
    except Exception as e:
        logger.warning("Solution execution failed: %s", e)
        return False, str(e)


def wipe_target_tables(
    blueprint: ScenarioBlueprint,
    docker: DockerClient,
) -> None:
    """TRUNCATE each target table so the student starts with empty tables."""
    for table in blueprint.target_tables:
        table_name = table.table_name
        try:
            docker.compose.execute(
                "target-db",
                [
                    "psql", "-U", "labuser", "-d", "target_db",
                    "-c", f'TRUNCATE TABLE "{table_name}" CASCADE;',
                ],
                tty=False,
            )
        except Exception as e:
            logger.warning("Failed to truncate %s: %s", table_name, e)
