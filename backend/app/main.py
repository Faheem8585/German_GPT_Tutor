"""FastAPI app setup — middleware, metrics, routes, health checks."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    GermanGPTError,
    germangpt_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

# prometheus counters/histograms
REQUEST_COUNT = Counter(
    "germangpt_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "germangpt_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)
LLM_CALLS = Counter("germangpt_llm_calls_total", "LLM API calls", ["provider", "model"])
GAME_SESSIONS = Counter("germangpt_game_sessions_total", "Game sessions started", ["game_type"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("germangpt_starting", version=settings.app_version, env=settings.environment.value)

    # Initialize RAG pipeline
    if settings.enable_rag:
        try:
            from app.rag.pipeline import rag_pipeline
            await rag_pipeline.initialize()
            logger.info("rag_pipeline_ready")
        except Exception as e:
            logger.warning("rag_init_failed", error=str(e))

    logger.info("germangpt_ready")
    yield

    logger.info("germangpt_shutting_down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="GermanGPT Tutor API",
        description="German language learning platform with LLM tutoring, games, and voice support.",
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        latency = time.monotonic() - start

        endpoint = request.url.path
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
        response.headers["X-Response-Time"] = f"{latency:.3f}s"
        return response

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # TODO: wire up Redis sliding window — slowapi works well for this
        return await call_next(request)

    from fastapi import HTTPException

    app.add_exception_handler(GermanGPTError, germangpt_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(api_router)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment.value,
            "timestamp": time.time(),
        }

    @app.get("/health/ready", tags=["Health"])
    async def readiness_check():
        """Kubernetes readiness probe — checks all dependencies."""
        checks = {"api": True, "rag": False, "redis": False}

        try:
            from app.memory.user_memory import UserMemoryService
            mem = UserMemoryService()
            r = await mem._get_redis()
            await r.ping()
            checks["redis"] = True
        except Exception:
            pass

        try:
            from app.rag.pipeline import rag_pipeline
            checks["rag"] = rag_pipeline._initialized
        except Exception:
            pass

        all_healthy = checks["api"] and checks["redis"]
        return {
            "ready": all_healthy,
            "checks": checks,
        }

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="info",
        access_log=True,
    )
