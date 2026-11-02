"""
KindBite Backend — FastAPI Application Entry Point
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import router as api_v1_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KindBite backend starting", env=settings.APP_ENV)
    yield
    logger.info("KindBite backend shutdown")


app = FastAPI(
    title="KindBite API",
    description=(
        "KindBite — AI-powered food waste prediction and redistribution platform. "
        "Every Bite Deserves a Chance."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ──────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    return response


# ── Health endpoints ───────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "kindbite-api", "version": "0.1.0"}


@app.get("/ready", tags=["Health"])
async def ready():
    """Check readiness including database connectivity."""
    from app.db.session import engine
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    ready = db_status == "ok"
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "db": db_status},
    )


# ── API Router ────────────────────────────────────────────
app.include_router(api_v1_router, prefix="/api/v1")
