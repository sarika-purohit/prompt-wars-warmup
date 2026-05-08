from typing import Generator
import logging

from core.config import get_settings, Settings
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.weather_service import WeatherService
from services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

# Singletons for services
_gemini_service = None
_maps_service = None
_weather_service = None
_firestore_service = None

def init_services(settings: Settings):
    global _gemini_service, _maps_service, _weather_service, _firestore_service
    _gemini_service = GeminiService(settings)
    _maps_service = MapsService(settings)
    _weather_service = WeatherService()
    try:
        _firestore_service = FirestoreService()
        logger.info("Firestore connected for dependencies")
    except Exception as e:
        logger.warning(f"Firestore not available in dependencies: {e}")
        _firestore_service = None

async def close_services():
    global _maps_service, _weather_service
    if _maps_service:
        await _maps_service.close()
    if _weather_service:
        await _weather_service.close()

def get_gemini_service() -> GeminiService:
    if not _gemini_service:
        raise ValueError("GeminiService not initialized")
    return _gemini_service

def get_maps_service() -> MapsService:
    if not _maps_service:
        raise ValueError("MapsService not initialized")
    return _maps_service

def get_weather_service() -> WeatherService:
    if not _weather_service:
        raise ValueError("WeatherService not initialized")
    return _weather_service

from typing import Optional

def get_firestore_service() -> Optional[FirestoreService]:
    return _firestore_service
