"""
Solution runner — generates and executes a self-test Python script in the lab container.

Three functions:
  1. generate_solution_script() — builds a .py file from blueprint solution_code or heuristics
  2. execute_solution_in_lab() — runs the script inside the Jupyter container
  3. wipe_target_tables() — TRUNCATEs target tables so the student starts fresh
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from python_on_whales import DockerClient

from ..models.blueprint import ScenarioBlueprint
from ..models.lab import LabSession
from .notebook_generator import generate_solution_notebook

logger = logging.getLogger(__name__)

# Marker printed by the script on success
_SUCCESS_MARKER = "===SELF_TEST_SOLUTION_OK==="


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
    Write the script to the lab workspace and execute it inside the Jupyter container.

    Returns (success, output).
    """
    if not session.lab_dir:
        return False, "Lab directory not set"

    script_filename = "_self_test_runner.py"
    workspace_dir = Path(session.lab_dir) / "workspace"
    script_path = workspace_dir / script_filename

    try:
        # Write script to workspace (mounted into container at /home/jovyan/work/)
        script_path.write_text(script, encoding="utf-8")

        # Execute inside the Jupyter container
        container_path = f"/home/jovyan/work/{script_filename}"
        result = docker.compose.execute(
            "jupyter",
            ["python", container_path],
            tty=False,
        )

        output = result.strip() if result else ""
        success = _SUCCESS_MARKER in output
        return success, output

    except Exception as e:
        logger.warning("Solution execution failed: %s", e)
        return False, str(e)

    finally:
        # Clean up the script file
        if script_path.exists():
            script_path.unlink(missing_ok=True)


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
