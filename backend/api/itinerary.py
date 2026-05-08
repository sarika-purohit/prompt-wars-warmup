"""Itinerary generation router."""

from __future__ import annotations

import logging
import uuid
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Depends

from models.user_input import Itinerary, TripRequest
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.firestore_service import FirestoreService
from api.dependencies import get_gemini_service, get_maps_service, get_firestore_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])


@router.post("/generate", response_model=Itinerary)
async def generate_itinerary(
    request: TripRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    maps: MapsService = Depends(get_maps_service),
    firestore: FirestoreService = Depends(get_firestore_service)
) -> Itinerary:
    """Generate a new travel itinerary.

    1. Fetches real places from Google Maps.
    2. Sends enriched prompt to Gemini.
    3. Saves result to Firestore.
    """
    if not gemini or not maps:
        raise HTTPException(status_code=503, detail="Services not available")

    # Validate date range
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    total_days = (request.end_date - request.start_date).days + 1
    if total_days > 14:
        raise HTTPException(status_code=400, detail="Trip cannot exceed 14 days")

    cache_key = None
    if firestore:
        import hashlib
        interests_str = ",".join(sorted([i.value for i in request.interests]))
        raw_key = f"{request.destination.lower()}_{request.start_date}_{request.end_date}_{request.budget}_{request.group_size}_{interests_str}"
        cache_key = hashlib.md5(raw_key.encode()).hexdigest()
        
        try:
            cached_itinerary = await firestore.get_cached_itinerary(cache_key)
            if cached_itinerary:
                return cached_itinerary
        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")

    try:
        # Step 1: Fetch real places from Google Maps to ground the AI
        logger.info(f"Searching places for {request.destination}")
        places_data = await maps.search_places(
            query=f"top attractions and restaurants in {request.destination}", max_results=15
        )

        # Step 2: Generate itinerary via Gemini
        itinerary = await gemini.generate_itinerary(request, places_data)
        
        # Geocode the destination to give a central map focus
        try:
            geocode_result = await maps.geocode(request.destination)
            if geocode_result:
                itinerary.location = geocode_result
        except Exception as e:
            logger.warning(f"Geocoding failed for {request.destination}: {e}")

        # Step 3: Assign ID and persist
        itinerary.id = uuid.uuid4().hex[:12]
        if firestore:
            try:
                await firestore.save_itinerary(itinerary)
                if cache_key:
                    await firestore.save_cached_itinerary(cache_key, itinerary)
            except Exception as exc:
                logger.warning("Firestore save failed (non-fatal): %s", exc)

        return itinerary

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Itinerary generation failed")
        raise HTTPException(status_code=500, detail="Failed to generate itinerary. Please try again.")


@router.get("/{itinerary_id}", response_model=Itinerary)
async def get_itinerary(
    itinerary_id: str,
    firestore: FirestoreService = Depends(get_firestore_service)
) -> Itinerary:
    """Retrieve a previously generated itinerary."""
    if not firestore:
        raise HTTPException(status_code=503, detail="Persistence not available")

    itinerary = await firestore.get_itinerary(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


@router.get("/", response_model=list[dict])
async def list_itineraries(firestore: FirestoreService = Depends(get_firestore_service)):
    """List recent itineraries."""
    if not firestore:
        return []

    try:
        return await firestore.list_itineraries()
    except Exception:
        return []
