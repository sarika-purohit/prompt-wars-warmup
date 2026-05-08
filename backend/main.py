"""TripFlow AI — FastAPI backend entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from routers import itinerary, places, adapt
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.weather_service import WeatherService

# ── Logging ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("tripflow")

# ── Lifespan ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down services."""
    settings = get_settings()

    gemini = GeminiService(settings)
    maps = MapsService(settings)
    weather = WeatherService()

    # Try Firestore, fall back gracefully if not configured
    firestore = None
    try:
        from services.firestore_service import FirestoreService
        firestore = FirestoreService()
        logger.info("Firestore connected")
    except Exception as exc:
        logger.warning("Firestore not available (running without persistence): %s", exc)

    # Wire services into routers
    itinerary.init_services(gemini, maps, firestore)
    places.init_services(maps)
    adapt.init_services(gemini, maps, weather, firestore)

    logger.info("TripFlow AI started | model=%s | env=%s", settings.gemini_model, settings.environment)
    yield

    # Cleanup
    await maps.close()
    await weather.close()
    logger.info("TripFlow AI shut down")

# ── App ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="TripFlow AI",
    description="AI-powered travel itinerary engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
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


# ── Global Error Handler ───────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler — never expose raw stack traces."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# ── Routes ──────────────────────────────────────────────────────────────

app.include_router(itinerary.router)
app.include_router(places.router)
app.include_router(adapt.router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "service": "tripflow-api", "version": "1.0.0"}
