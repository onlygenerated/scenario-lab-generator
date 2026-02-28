# Labwright

AI-powered scenario-based lab training for data pipeline / ETL skills.

A proof-of-concept demonstrating: user selects parameters, AI generates a structured lab blueprint, Docker provisions a working environment, the learner completes the ETL task in JupyterLab, and the system validates their work automatically.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard (Vite)                     │
│  Configure → Generate → Review → Launch → Lab → Validate     │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                             │
│  ┌────────────┐ ┌──────────────┐ ┌─────────────┐            │
│  │  Generator  │ │ Orchestrator │ │  Validator   │            │
│  │ (Claude AI) │ │(Docker Comp.)│ │(SQL Checks)  │            │
│  └────────────┘ └──────────────┘ └─────────────┘            │
└──────────────────────────┬──────────────────────────────────┘
                           │ docker compose
┌──────────────────────────▼──────────────────────────────────┐
│              Per-Lab Docker Network                           │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐          │
│  │ source-db│  │ target-db│  │   JupyterLab      │          │
│  │(Postgres)│  │(Postgres)│  │ (sqlalchemy+pandas)│          │
│  └──────────┘  └──────────┘  └───────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY for AI generation, or leave DEMO_MODE=true

# 2. Backend
cd backend
python -m venv ../.venv
source ../.venv/Scripts/activate  # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend
cd ../frontend
npm install

# 4. Run (two terminals)
# Terminal 1 — Backend:
uvicorn backend.app.main:app --reload

# Terminal 2 — Frontend:
cd frontend && npm run dev
```

Open http://localhost:5173 in your browser.

### Demo Mode

With `DEMO_MODE=true` (default), the app uses a handcrafted sample blueprint instead of calling the Claude API. This is useful for:
- Testing without an API key
- Demonstrating the Docker orchestration independently
- Cost-free demos

### Docker Compose (Full Stack)

```bash
cp .env.example .env
docker compose up --build
```

## Project Structure

```
Labwright/
├── backend/               # FastAPI + Python
│   ├── app/
│   │   ├── main.py        # App entry point
│   │   ├── config.py      # Environment config
│   │   ├── models/        # Pydantic schemas
│   │   ├── services/      # Generator, Orchestrator, Validator
│   │   ├── prompts/       # AI prompt templates
│   │   └── api/           # HTTP routes
│   └── requirements.txt
├── frontend/              # React + Vite + Tailwind
│   └── src/
│       ├── components/    # UI components
│       ├── pages/         # Dashboard
│       └── api/           # API client
├── templates/             # Docker/Jupyter templates
│   ├── docker-compose.lab.yml.j2
│   ├── jupyter/Dockerfile
│   └── workspace/getting_started.ipynb
├── demo/                  # Demo mode blueprint
└── docker-compose.yml     # Dev stack
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/demos/blueprint` | Get demo blueprint |
| POST | `/api/scenarios/generate` | AI-generate a blueprint |
| POST | `/api/labs/launch` | Launch lab from blueprint |
| GET | `/api/labs/{id}` | Get lab status |
| POST | `/api/labs/{id}/validate` | Validate learner's work |
| POST | `/api/labs/{id}/stop` | Stop and cleanup lab |
| GET | `/health` | Health check |

## Security

See [SECURITY.md](SECURITY.md) for trust boundaries, audit process, and known limitations.

## Tech Stack

- **Backend**: FastAPI, Pydantic, python-on-whales
- **AI**: Anthropic Claude API (Sonnet) with structured outputs
- **Frontend**: React, Vite, Tailwind CSS, react-markdown
- **Lab**: PostgreSQL 16, JupyterLab (Docker)
