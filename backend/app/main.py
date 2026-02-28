"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router, get_lab_sessions
from .config import settings
from .services.orchestrator import cleanup_orphaned_labs, stop_lab

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: clean up orphaned lab containers from previous runs
    try:
        cleaned = cleanup_orphaned_labs()
        if cleaned:
            logger.info("Cleaned up %d orphaned lab(s) from previous run", cleaned)
    except Exception:
        logger.warning("Failed to clean up orphaned labs", exc_info=True)

    yield

    # Shutdown: stop all running labs gracefully
    sessions = get_lab_sessions()
    for session in list(sessions.values()):
        if session.status.value in ("running", "starting"):
            try:
                stop_lab(session)
                logger.info("Stopped lab %s during shutdown", session.lab_id)
            except Exception:
                logger.warning("Failed to stop lab %s during shutdown", session.lab_id)


app = FastAPI(
    title="Labwright",
    description="AI-powered scenario-based lab training for data pipeline / ETL skills",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
