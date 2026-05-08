"""Dependency injection providers for FastAPI route handlers.

This module creates singleton instances of each service at application
startup and exposes them through ``Depends()`` callables.  This pattern
ensures:

- **Efficiency**: Services are created once, not per-request.
- **Testability**: Services can be easily mocked in unit tests.
- **Security**: API keys are loaded once from environment variables
  and never re-read during the request lifecycle.

Usage in a route handler::

    @router.post("/generate")
    async def generate(
        gemini: GeminiService = Depends(get_gemini_service),
    ) -> Itinerary:
        ...
"""

from __future__ import annotations

import logging
from typing import Optional

from core.config import Settings
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.weather_service import WeatherService
from services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

# ── Service Singletons ───────────────────────────────────────────────────

_gemini_service: Optional[GeminiService] = None
_maps_service: Optional[MapsService] = None
_weather_service: Optional[WeatherService] = None
_firestore_service: Optional[FirestoreService] = None


def init_services(settings: Settings) -> None:
    """Initialize all service singletons from application settings.

    Called once during FastAPI lifespan startup.  Each service receives
    the Settings dataclass which contains the required API keys.

    Args:
        settings: Application configuration loaded from environment variables.
    """
    global _gemini_service, _maps_service, _weather_service, _firestore_service

    _gemini_service = GeminiService(settings)
    _maps_service = MapsService(settings)
    _weather_service = WeatherService()

    # Firestore requires Application Default Credentials in production.
    # Gracefully degrade if credentials are not available (e.g., local dev).
    try:
        _firestore_service = FirestoreService()
        logger.info("Firestore service initialized successfully")
    except Exception as exc:
        logger.warning("Firestore not available (non-fatal): %s", exc)
        _firestore_service = None


async def close_services() -> None:
    """Gracefully shut down services and release resources.

    Closes open HTTP client connections to prevent resource leaks.
    Called during FastAPI lifespan shutdown.
    """
    global _maps_service, _weather_service
    if _maps_service:
        await _maps_service.close()
    if _weather_service:
        await _weather_service.close()


# ── Dependency Providers ─────────────────────────────────────────────────

def get_gemini_service() -> GeminiService:
    """Provide the GeminiService singleton for route handlers.

    Raises:
        ValueError: If services have not been initialized.
    """
    if not _gemini_service:
        raise ValueError("GeminiService not initialized")
    return _gemini_service


def get_maps_service() -> MapsService:
    """Provide the MapsService singleton for route handlers.

    Raises:
        ValueError: If services have not been initialized.
    """
    if not _maps_service:
        raise ValueError("MapsService not initialized")
    return _maps_service


def get_weather_service() -> WeatherService:
    """Provide the WeatherService singleton for route handlers.

    Raises:
        ValueError: If services have not been initialized.
    """
    if not _weather_service:
        raise ValueError("WeatherService not initialized")
    return _weather_service


def get_firestore_service() -> Optional[FirestoreService]:
    """Provide the FirestoreService singleton for route handlers.

    Returns ``None`` if Firestore is not available (e.g., missing
    Application Default Credentials in local development).
    This allows the application to function without persistence.

    Returns:
        Optional[FirestoreService]: The Firestore service, or None.
    """
    return _firestore_service
