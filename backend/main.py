"""TripFlow AI — FastAPI backend entry point.

This module bootstraps the FastAPI application with:
- **Lifespan management**: initializes and tears down service singletons.
- **Security middleware**: CORS, security headers (HSTS, X-Content-Type-Options).
- **Observability middleware**: request timing and structured logging.
- **Global error handling**: prevents stack trace leakage to clients.

Architecture:
    The application follows a clean layered architecture:
    ``api/`` (routers) → ``services/`` (business logic) → external APIs.
    All services are initialized once at startup and injected via FastAPI
    ``Depends()`` for testability and thread-safety.

Google Services:
    - Google Gemini 2.0 Flash — AI itinerary generation and adaptation.
    - Google Maps Platform — Places API (New), Geocoding, Directions.
    - Google Cloud Firestore — serverless itinerary persistence and caching.
    - Google Cloud Run — production deployment target.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from api import itinerary, places, adapt
from middleware.logging import TimingMiddleware
from middleware.security import SecurityHeadersMiddleware

# ── Logging Configuration ────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("tripflow")


# ── Application Lifespan ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down application services.

    This async context manager runs once at startup and shutdown.
    It creates singleton instances of all services (Gemini, Maps,
    Weather, Firestore) and makes them available through the
    dependency injection layer in ``api.dependencies``.

    Yields:
        None: Control is yielded to the application during its lifetime.
    """
    settings = get_settings()

    # Initialize service singletons for dependency injection
    from api.dependencies import init_services, close_services
    init_services(settings)

    logger.info(
        "TripFlow AI started | model=%s | env=%s | mock=%s",
        settings.gemini_model,
        settings.environment,
        settings.use_mock_data,
    )
    yield

    # Graceful shutdown — close HTTP clients and release resources
    await close_services()
    logger.info("TripFlow AI shut down")


# ── FastAPI Application ──────────────────────────────────────────────────

app = FastAPI(
    title="TripFlow AI",
    description=(
        "AI-powered travel itinerary engine using Google Gemini "
        "and Google Maps Platform."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── Middleware Stack (order matters: outermost first) ─────────────────────

# 1. Performance monitoring — logs request duration for every API call
app.add_middleware(TimingMiddleware)

# 2. Security headers — HSTS, X-Content-Type-Options, X-Frame-Options
app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS — restrict cross-origin access to known frontends only
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Error Handler ─────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all error handler to prevent stack trace leakage.

    SECURITY: Never expose raw Python tracebacks to clients.
    All unhandled exceptions are logged server-side and the client
    receives a generic 500 error message.

    Args:
        request: The incoming HTTP request that caused the error.
        exc: The unhandled exception.

    Returns:
        JSONResponse: Generic error message with 500 status code.
    """
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# ── API Routers ──────────────────────────────────────────────────────────

app.include_router(itinerary.router)
app.include_router(places.router)
app.include_router(adapt.router)


# ── Health Check Endpoints ───────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint for Cloud Run liveness probes.

    Returns:
        dict: Service status, name, and version.
    """
    return {"status": "healthy", "service": "tripflow-api", "version": "2.0.0"}


@app.get("/", tags=["health"])
async def root() -> dict:
    """Root endpoint — API discovery for developers.

    Returns:
        dict: Links to documentation and health endpoints.
    """
    return {
        "service": "TripFlow AI API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }
