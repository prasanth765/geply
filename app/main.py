from __future__ import annotations
"""
====================================================================
  Project : Geply - AI Interview Platform
  Company : GEP Worldwide
  Author  : Prasanth Ragupathy <prasanth.ragupathy@gep.com>
  File    : main.py
====================================================================
"""
"""
====================================================================
  Project : Geply - AI Interview Platform
  Company : GEP Worldwide
  Author  : Prasanth Ragupathy <prasanth.ragupathy@gep.com>
  File    : main.py
  Purpose : FastAPI application entry point. Configures middleware, routes, CORS, rate limiting and lifespan events.
====================================================================
"""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import api_router
from app.core.config import configure_logging, get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.exceptions import AppException
from app.models.base import create_tables, engine
from app.models import User, Job, Candidate, Interview, ScheduleSlot, Report, Notification, InterviewQuestion  # noqa: F401 - required for create_tables()

logger = structlog.get_logger()


# â”€â”€ Request ID Middleware â”€â”€
# Every request gets a unique ID for tracing through logs, error reports, etc.


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Bind to structlog context so every log line in this request includes it
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# â”€â”€ Lifespan â”€â”€


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging()
    logger.info("app_starting", app=settings.app_name, env=settings.app_env, debug=settings.debug)

    await create_tables()
    logger.info("database_tables_created")

    # Idempotent column migrations (safe to run every boot; Postgres only)
    if "sqlite" not in settings.database_url:
        from sqlalchemy import text as _sql_text
        _migrations = [
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS ask_ctc BOOLEAN NOT NULL DEFAULT FALSE",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS recruiter_questions JSONB",
            "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jd_match_score DOUBLE PRECISION",
            "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jd_match_verdict VARCHAR(50)",
            "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jd_match_breakdown JSONB",
        ]
        try:
            async with engine.begin() as _conn:
                for _stmt in _migrations:
                    await _conn.execute(_sql_text(_stmt))
            logger.info("startup_migrations_applied", count=len(_migrations))
        except Exception as _mig_exc:
            logger.error("startup_migrations_failed", error=str(_mig_exc))

    yield

    await engine.dispose()
    logger.info("app_shutdown")


# â”€â”€ App Factory â”€â”€


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Geply",
        description="AI-Powered Interview Platform by GEP",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # â”€â”€ Middleware (order matters â€” first added = outermost) â”€â”€
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # CORS â€” production uses explicit origins from env; dev uses localhost defaults
    allowed_methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    allowed_headers = ["Authorization", "Content-Type", "X-Request-ID"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
    )

    # â”€â”€ Exception Handlers â”€â”€

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            code=exc.code,
            message=exc.message,
            status=exc.status,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "context": exc.context,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "context": {},
                }
            },
        )

    # â”€â”€ Routes â”€â”€
    app.include_router(api_router)
    from app.api.routes.interview_session import router as interview_session_router
    app.include_router(interview_session_router, prefix="/api/v1")

    # â”€â”€ Password Reset Routes â”€â”€
    from app.api.routes.password_reset import router as password_reset_router
    app.include_router(password_reset_router)

    # -- Candidate Interview Questions CRUD --
    from app.api.routes.questions import router as questions_router
    app.include_router(questions_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "healthy", "service": "geply", "version": "1.0.0"}

    return app


app = create_app()
