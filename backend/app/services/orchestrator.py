"""
Docker Compose lifecycle manager.

Uses python-on-whales to wrap `docker compose` CLI directly.
Each lab gets a unique Compose project name and dynamically assigned port.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader
from python_on_whales import DockerClient

from ..config import settings
from ..models.blueprint import ScenarioBlueprint
from ..models.lab import LabSession, LabStatus
from .notebook_generator import generate_incorrect_notebook, generate_instructions_md, generate_notebook, generate_solution_notebook
from .seed_generator import generate_source_sql, generate_target_sql

# Track allocated ports to avoid collisions
_allocated_ports: set[int] = set()

# Template directory
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "templates"


def _find_available_port() -> int:
    """Find the next available port in the configured range."""
    for port in range(settings.lab_port_range_start, settings.lab_port_range_end + 1):
        if port not in _allocated_ports:
            _allocated_ports.add(port)
            return port
    raise RuntimeError("No available ports in the configured range")


def _release_port(port: int) -> None:
    """Release a port back to the pool."""
    _allocated_ports.discard(port)


def _prepare_lab_directory(lab_id: str, blueprint: ScenarioBlueprint, jupyter_port: int, include_solutions: bool = True) -> Path:
    """
    Create the lab workspace directory with all generated files:
    - docker-compose.yml (from Jinja2 template)
    - seed_source.sql
    - seed_target.sql
    - jupyter/ (Dockerfile)
    - workspace/ (starter notebook + instructions)
    """
    lab_dir = Path(settings.lab_base_dir) / f"lab-{lab_id}"
    lab_dir.mkdir(parents=True, exist_ok=True)

    # Render docker-compose.yml from template
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("docker-compose.lab.yml.j2")
    compose_content = template.render(lab_id=lab_id, jupyter_port=jupyter_port)
    (lab_dir / "docker-compose.yml").write_text(compose_content, encoding="utf-8")

    # Generate seed SQL files
    source_sql = generate_source_sql(blueprint)
    (lab_dir / "seed_source.sql").write_text(source_sql, encoding="utf-8")

    target_sql = generate_target_sql(blueprint)
    (lab_dir / "seed_target.sql").write_text(target_sql, encoding="utf-8")

    # Copy Jupyter Dockerfile
    jupyter_dir = lab_dir / "jupyter"
    jupyter_dir.mkdir(exist_ok=True)
    shutil.copy2(_TEMPLATES_DIR / "jupyter" / "Dockerfile", jupyter_dir / "Dockerfile")

    # Generate workspace: dynamic notebook from blueprint + instructions
    # Numbered prefixes control file listing order in JupyterLab's sidebar.
    # Dotfile prefix hides internal notebooks from the student.
    workspace_dir = lab_dir / "workspace"
    workspace_dir.mkdir(exist_ok=True)

    instructions_md = generate_instructions_md(blueprint)
    (workspace_dir / "1_INSTRUCTIONS.md").write_text(instructions_md, encoding="utf-8")

    notebook_json = generate_notebook(blueprint)
    (workspace_dir / "2_getting_started.ipynb").write_text(notebook_json, encoding="utf-8")

    if include_solutions:
        solution_json = generate_solution_notebook(blueprint)
        (workspace_dir / "3_solution.ipynb").write_text(solution_json, encoding="utf-8")

        incorrect_json = generate_incorrect_notebook(blueprint)
        (workspace_dir / "4_incorrect_solution.ipynb").write_text(incorrect_json, encoding="utf-8")

    return lab_dir


def launch_lab(blueprint: ScenarioBlueprint, include_solutions: bool = True) -> LabSession:
    """
    Launch a new lab environment from a blueprint.

    1. Allocate a port
    2. Generate all files in a lab directory
    3. docker compose up -d
    4. Return the LabSession with JupyterLab URL
    """
    lab_id = str(uuid4())[:8]
    jupyter_port = _find_available_port()

    session = LabSession(
        lab_id=lab_id,
        blueprint=blueprint,
        jupyter_port=jupyter_port,
        compose_project_name=f"lab-{lab_id}",
        status=LabStatus.starting,
    )

    try:
        lab_dir = _prepare_lab_directory(lab_id, blueprint, jupyter_port, include_solutions)
        session.lab_dir = str(lab_dir)

        # Create Docker client for this specific compose project
        docker = DockerClient(
            compose_files=[str(lab_dir / "docker-compose.yml")],
            compose_project_name=f"lab-{lab_id}",
        )

        # Build and start all services
        docker.compose.up(detach=True, build=True)

        session.status = LabStatus.running
        session.jupyter_url = f"http://localhost:{jupyter_port}/lab/tree/1_INSTRUCTIONS.md?token=labtoken"

    except Exception as e:
        session.status = LabStatus.error
        session.error_message = str(e)
        _release_port(jupyter_port)

    return session


def stop_lab(session: LabSession) -> LabSession:
    """Stop and clean up a lab environment."""
    if not session.lab_dir or not session.compose_project_name:
        session.status = LabStatus.error
        session.error_message = "Lab directory or project name missing"
        return session

    session.status = LabStatus.stopping

    try:
        lab_dir = Path(session.lab_dir)
        compose_file = lab_dir / "docker-compose.yml"

        if compose_file.exists():
            docker = DockerClient(
                compose_files=[str(compose_file)],
                compose_project_name=session.compose_project_name,
            )
            docker.compose.down(volumes=True)

        # Clean up the lab directory
        if lab_dir.exists():
            shutil.rmtree(lab_dir, ignore_errors=True)

        session.status = LabStatus.stopped

    except Exception as e:
        session.status = LabStatus.error
        session.error_message = str(e)

    finally:
        if session.jupyter_port:
            _release_port(session.jupyter_port)

    return session


def get_lab_docker_client(session: LabSession) -> DockerClient | None:
    """Get a DockerClient for a running lab (used by validator)."""
    if not session.lab_dir or not session.compose_project_name:
        return None

    lab_dir = Path(session.lab_dir)
    compose_file = lab_dir / "docker-compose.yml"

    if not compose_file.exists():
        return None

    return DockerClient(
        compose_files=[str(compose_file)],
        compose_project_name=session.compose_project_name,
    )


def cleanup_orphaned_labs() -> int:
    """
    Clean up any orphaned lab containers on startup.
    Returns the number of labs cleaned up.
    """
    base = Path(settings.lab_base_dir)
    if not base.exists():
        return 0

    cleaned = 0
    for lab_dir in base.iterdir():
        if not lab_dir.is_dir() or not lab_dir.name.startswith("lab-"):
            continue

        compose_file = lab_dir / "docker-compose.yml"
        if compose_file.exists():
            try:
                docker = DockerClient(
                    compose_files=[str(compose_file)],
                    compose_project_name=lab_dir.name,
                )
                docker.compose.down(volumes=True)
            except Exception:
                pass  # Best effort cleanup

        shutil.rmtree(lab_dir, ignore_errors=True)
        cleaned += 1

    return cleaned
