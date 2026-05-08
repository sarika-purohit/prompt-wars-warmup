"""Itinerary generation router."""

from __future__ import annotations

import logging
import uuid
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException

from models.user_input import Itinerary, TripRequest
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])

# Services are injected at startup via app.state (see main.py)
_gemini = None
_maps = None
_firestore = None


def init_services(gemini: GeminiService, maps: MapsService, firestore: FirestoreService) -> None:
    """Wire service instances into this router."""
    global _gemini, _maps, _firestore
    _gemini, _maps, _firestore = gemini, maps, firestore


@router.post("/generate", response_model=Itinerary)
async def generate_itinerary(request: TripRequest) -> Itinerary:
    """Generate a new travel itinerary.

    1. Fetches real places from Google Maps.
    2. Sends enriched prompt to Gemini.
    3. Saves result to Firestore.
    """
    if not _gemini or not _maps:
        raise HTTPException(status_code=503, detail="Services not initialized")

    # Validate date range
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    total_days = (request.end_date - request.start_date).days + 1
    if total_days > 14:
        raise HTTPException(status_code=400, detail="Trip cannot exceed 14 days")

    try:
        # Step 1: Enrich with real Google Maps data
        interests = [i.value for i in request.interests]
        places_context = await _maps.get_place_context_for_ai(
            request.destination, interests
        )

        # Step 2: Generate itinerary via Gemini
        itinerary = await _gemini.generate_itinerary(request, places_context)

        # Step 3: Assign ID and persist
        itinerary.id = uuid.uuid4().hex[:12]
        if _firestore:
            try:
                await _firestore.save_itinerary(itinerary)
            except Exception as exc:
                logger.warning("Firestore save failed (non-fatal): %s", exc)

        return itinerary

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Itinerary generation failed")
        raise HTTPException(status_code=500, detail="Failed to generate itinerary. Please try again.")


@router.get("/{itinerary_id}", response_model=Itinerary)
async def get_itinerary(itinerary_id: str) -> Itinerary:
    """Retrieve a saved itinerary by ID."""
    if not _firestore:
        raise HTTPException(status_code=503, detail="Storage not available")

    itinerary = await _firestore.get_itinerary(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


@router.get("/", response_model=list[dict])
async def list_itineraries():
    """List recent itineraries."""
    if not _firestore:
        return []

    try:
        return await _firestore.list_itineraries()
    except Exception:
        return []
