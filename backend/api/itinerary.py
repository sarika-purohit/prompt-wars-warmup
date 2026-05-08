"""Itinerary generation router.

Provides the primary endpoint for generating AI-powered travel itineraries.
The flow:
    1. Fetch real places from **Google Maps Places API (New)**.
    2. Send enriched prompt to **Google Gemini 2.0 Flash**.
    3. Cache and persist the result in **Google Cloud Firestore**.

Efficiency:
    Results are cached by a deterministic MD5 hash of the request parameters.
    Subsequent identical requests return instantly from Firestore without
    consuming Gemini API tokens.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from models.user_input import Itinerary, TripRequest
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.firestore_service import FirestoreService
from api.dependencies import (
    get_gemini_service,
    get_maps_service,
    get_firestore_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/itinerary", tags=["itinerary"])


def _build_cache_key(request: TripRequest) -> str:
    """Build a deterministic cache key from trip request parameters.

    EFFICIENCY: Uses MD5 hashing for O(1) cache lookups in Firestore,
    avoiding redundant Gemini API calls for identical requests.

    Args:
        request: The user's trip planning request.

    Returns:
        str: 32-character hex digest uniquely identifying this request.
    """
    interests_str = ",".join(sorted(i.value for i in request.interests))
    raw_key = (
        f"{request.destination.lower()}_"
        f"{request.start_date}_{request.end_date}_"
        f"{request.budget}_{request.group_size}_"
        f"{interests_str}"
    )
    return hashlib.md5(raw_key.encode()).hexdigest()


@router.post("/generate", response_model=Itinerary)
async def generate_itinerary(
    request: TripRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    maps: MapsService = Depends(get_maps_service),
    firestore: Optional[FirestoreService] = Depends(get_firestore_service),
) -> Itinerary:
    """Generate a new AI-powered travel itinerary.

    Pipeline:
        1. Check Firestore cache for an identical prior request.
        2. Fetch real places from Google Maps to ground the AI.
        3. Generate structured itinerary via Google Gemini 2.0 Flash.
        4. Geocode the destination for map centering.
        5. Persist the result and update the cache.

    Args:
        request: Validated trip planning parameters from the user.
        gemini: Injected Gemini AI service.
        maps: Injected Google Maps service.
        firestore: Injected Firestore service (optional).

    Returns:
        Itinerary: Complete day-by-day travel plan.

    Raises:
        HTTPException 400: If date range is invalid.
        HTTPException 422: If AI response cannot be parsed.
        HTTPException 500: If generation fails unexpectedly.
        HTTPException 503: If required services are unavailable.
    """
    if not gemini or not maps:
        raise HTTPException(status_code=503, detail="Services not available")

    # ── Input Validation ─────────────────────────────────────────────
    if request.end_date < request.start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be after start_date",
        )

    total_days = (request.end_date - request.start_date).days + 1
    if total_days > 14:
        raise HTTPException(
            status_code=400,
            detail="Trip cannot exceed 14 days",
        )

    # ── Cache Lookup (Efficiency) ────────────────────────────────────
    cache_key = _build_cache_key(request)
    if firestore:
        try:
            cached = await firestore.get_cached_itinerary(cache_key)
            if cached:
                logger.info("Cache HIT — returning cached itinerary")
                return cached
        except Exception as exc:
            logger.warning("Cache lookup failed (non-fatal): %s", exc)

    # ── Generation Pipeline ──────────────────────────────────────────
    try:
        # Step 1: Fetch real places from Google Maps Places API (New)
        logger.info("Searching Google Maps for %s", request.destination)
        places_data = await maps.search_places(
            query=f"top attractions and restaurants in {request.destination}",
            max_results=15,
        )

        # Step 2: Generate itinerary via Google Gemini 2.0 Flash
        itinerary = await gemini.generate_itinerary(request, places_data)

        # Step 3: Geocode destination for map centering
        try:
            geocode_result = await maps.geocode(request.destination)
            if geocode_result:
                itinerary.location = geocode_result
        except Exception as exc:
            logger.warning("Geocoding failed (non-fatal): %s", exc)

        # Step 4: Assign unique ID and persist
        itinerary.id = uuid.uuid4().hex[:12]
        if firestore:
            try:
                await firestore.save_itinerary(itinerary)
                await firestore.save_cached_itinerary(cache_key, itinerary)
                logger.info("Itinerary %s saved to Firestore", itinerary.id)
            except Exception as exc:
                logger.warning("Firestore save failed (non-fatal): %s", exc)

        return itinerary

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Itinerary generation failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate itinerary. Please try again.",
        )


@router.get("/{itinerary_id}", response_model=Itinerary)
async def get_itinerary(
    itinerary_id: str,
    firestore: Optional[FirestoreService] = Depends(get_firestore_service),
) -> Itinerary:
    """Retrieve a previously generated itinerary by ID.

    Args:
        itinerary_id: Unique 12-character hex identifier.
        firestore: Injected Firestore service.

    Returns:
        Itinerary: The stored itinerary.

    Raises:
        HTTPException 404: If the itinerary does not exist.
        HTTPException 503: If Firestore is not available.
    """
    if not firestore:
        raise HTTPException(status_code=503, detail="Persistence not available")

    itinerary = await firestore.get_itinerary(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


@router.get("/", response_model=list[dict])
async def list_itineraries(
    firestore: Optional[FirestoreService] = Depends(get_firestore_service),
) -> list[dict]:
    """List recent itineraries (metadata only).

    Returns:
        list[dict]: Summary list of recent itineraries.
    """
    if not firestore:
        return []

    try:
        return await firestore.list_itineraries()
    except Exception:
        return []
