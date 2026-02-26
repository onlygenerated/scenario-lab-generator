# Testing the ScenarioLabGenerator App

## Prerequisites

- **Python 3.13+** (verify: `python --version`)
- **Node.js 18+** with npm (verify: `node --version`)
- **Docker Desktop for Windows** (running)
- **PowerShell** (default Windows terminal)

---

## 1. Environment Setup

Copy the environment template and configure it:

```powershell
cd C:\claudeprojects\ScenarioLabGenerator
Copy-Item .env.example .env
```

Edit `.env` as needed (open in any text editor, or `notepad .env`):

| Variable | Default | Notes |
|----------|---------|-------|
| `DEMO_MODE` | `true` | Use `true` to test without an API key (loads a sample blueprint) |
| `ANTHROPIC_API_KEY` | — | Required only when `DEMO_MODE=false` |
| `API_PORT` | `8000` | Backend port |
| `LAB_PORT_RANGE_START` | `8888` | First port available for Jupyter labs |

For quick testing, leave `DEMO_MODE=true` so no API key is needed.

---

## 2. Starting the Backend

```powershell
cd C:\claudeprojects\ScenarioLabGenerator
.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --reload-dir backend
```

> **Note:** If you get an execution policy error when activating the venv, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try `.venv\Scripts\Activate.ps1` again.

The backend starts on **http://localhost:8000**.

Verify it's running:

```powershell
Invoke-RestMethod http://localhost:8000/health
# Expected: status = ok
```

---

## 3. Starting the Frontend

Open a **second PowerShell window**:

```powershell
cd C:\claudeprojects\ScenarioLabGenerator\frontend
npm install    # first time only
npm run dev
```

The frontend starts on **http://localhost:5173**.

The Vite dev server proxies all `/api/*` requests to the backend at `localhost:8000` automatically.

---

## 4. Using the App

Open your browser to:

> **http://localhost:5173**

### Workflow Steps

1. **Configure** — Choose difficulty, number of source tables, focus skills, and industry. Click **Generate Scenario** (or **Load Demo** for the built-in sample).
2. **Generating / Self-Testing** — The app generates a blueprint (via AI or demo) and runs an automated self-test to verify the scenario is solvable.
3. **Review** — Inspect the generated blueprint and self-test results. Click **Launch Lab** to spin up the Docker environment.
4. **Lab Running** — A JupyterLab workspace opens in an iframe. Complete the ETL tasks described in the notebook.
5. **Validate** — Click **Validate** to run the validation queries against your work. Results show pass/fail for each check.

### Demo Mode Shortcut

With `DEMO_MODE=true`, clicking **Generate Scenario** skips the AI call and instantly loads a pre-built "Retail Sales Pipeline: Daily Revenue Summary" scenario. This is the fastest way to test the full Docker lab lifecycle.

---

## 5. Full Stack via Docker Compose

To run both backend and frontend in Docker (no local Python/Node needed):

```powershell
cd C:\claudeprojects\ScenarioLabGenerator
docker compose up --build
```

- Backend: **http://localhost:8000**
- Frontend: **http://localhost:5173**

> **Note:** Docker Desktop must be running. If `docker compose` is not recognized, ensure Docker Desktop is installed and the `docker` CLI is on your PATH.

---

## 6. API Endpoints (Manual Testing)

You can test the backend directly from PowerShell or any HTTP client:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/demos/blueprint` | Get the demo blueprint |
| `POST` | `/api/scenarios/generate` | Generate a new blueprint |
| `POST` | `/api/scenarios/self-test` | Run self-test on a blueprint |
| `POST` | `/api/labs/launch` | Launch a lab from a blueprint |
| `GET` | `/api/labs` | List all active labs |
| `GET` | `/api/labs/{lab_id}` | Get lab status |
| `POST` | `/api/labs/{lab_id}/validate` | Run validation queries |
| `POST` | `/api/labs/{lab_id}/stop` | Stop and clean up a lab |

Example — generate a scenario:

```powershell
$body = @{
    difficulty = "intermediate"
    num_source_tables = 2
    focus_skills = @("joins", "aggregation")
    industry = "retail"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/scenarios/generate `
    -ContentType "application/json" -Body $body
```

Example — health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

---

## 7. Stopping Everything

1. **Stop a running lab** — Click "Stop Lab" in the UI, or:
   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/labs/{lab_id}/stop
   ```
2. **Stop the frontend** — `Ctrl+C` in the frontend PowerShell window.
3. **Stop the backend** — `Ctrl+C` in the backend PowerShell window. The backend gracefully shuts down any running lab containers on exit.
4. **Stop Docker Compose stack** (if using):
   ```powershell
   docker compose down
   ```

---

## 8. Troubleshooting

| Issue | Fix |
|-------|-----|
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` then retry |
| Backend won't start | Ensure `.venv` is activated and `pip install -r backend\requirements.txt` was run |
| Frontend can't reach backend | Confirm backend is running on port 8000; Vite proxies `/api/*` automatically |
| Lab launch fails | Make sure Docker Desktop is running and ports 8888-8988 are free |
| "Rate limit exceeded" | Wait 60 seconds or increase `GENERATE_RATE_LIMIT_PER_MINUTE` in `.env` |
| Self-test fails | Check Docker logs: `docker compose -f lab_workspaces\lab-{id}\docker-compose.yml logs` |
| No logs in backend terminal | Known issue — uvicorn access logs (POST lines) serve as a proxy for request activity |
| `docker compose` not recognized | Open Docker Desktop, go to Settings > General, ensure "Use Docker Compose V2" is checked |
