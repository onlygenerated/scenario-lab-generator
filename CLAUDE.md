# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Labwright — AI-powered scenario-based lab training for data pipeline / ETL skills. PoC demonstrating: parameter selection → AI blueprint generation → Docker lab provisioning → JupyterLab workspace → automated validation.

## Tech Stack

- **Backend**: FastAPI (Python 3.13), Pydantic v2, python-on-whales, Jinja2
- **AI**: Anthropic Claude API (Sonnet 4.5) with tool-based structured outputs
- **Frontend**: React + TypeScript + Vite + Tailwind CSS v4, react-markdown with rehype-sanitize
- **Lab Env**: PostgreSQL 16 (Docker), JupyterLab (Docker), per-lab isolated compose networks

## Commands

```bash
# Backend
cd /c/claudeprojects/ScenarioLabGenerator
source .venv/Scripts/activate
uvicorn backend.app.main:app --reload --reload-dir backend  # Start dev server on :8000
pip-audit                                       # Security audit Python deps

# Frontend
cd frontend
npm run dev                                     # Start dev server on :5173
npm run build                                   # Production build
npx tsc --noEmit                               # Type check

# Full stack (Docker)
docker compose up --build
```

## Architecture

- `backend/app/models/blueprint.py` — THE core schema (ScenarioBlueprint Pydantic model). Contract between generator, orchestrator, and validator.
- `backend/app/services/generator.py` — Claude API structured output generation
- `backend/app/services/orchestrator.py` — Docker Compose lifecycle (launch, stop, cleanup)
- `backend/app/services/seed_generator.py` — Blueprint → SQL conversion
- `backend/app/services/validator.py` — SELECT-only query execution via docker compose exec
- `backend/app/api/routes.py` — All HTTP endpoints, in-memory session store
- `frontend/src/pages/Dashboard.tsx` — Single-page state machine orchestrating the workflow
- `templates/` — Jinja2 compose template, Jupyter Dockerfile, starter notebook
- `demo/sample_blueprint.json` — Handcrafted demo blueprint for testing without AI

## Key Design Decisions

- AI output is **untrusted** — all table/column names validated against `^[a-z][a-z0-9_]{0,62}$` and SQL keyword blocklist
- Validation queries are SELECT-only (Pydantic + runtime double-check) and run as read-only `validator` Postgres role with 5s timeout
- Seed SQL uses escaped string values (not f-string interpolation) for all data
- Lab containers have resource limits, no privileged mode, no Docker socket access
- Demo mode (DEMO_MODE=true) bypasses AI for cost-free testing
