"""Places search router — Google Maps Platform integration.

Exposes Google Maps Places API (New) and Geocoding API through
clean REST endpoints for the React frontend.

Google Services Used:
    - Places API (New) — Text Search for attractions and restaurants.
    - Geocoding API — Convert addresses to lat/lng coordinates.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, List, Dict

from fastapi import APIRouter, HTTPException, Query, Depends

from services.maps_service import MapsService
from api.dependencies import get_maps_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("/search")
async def search_places(
    q: str = Query(..., min_length=2, description="Search query"),
    lat: Optional[float] = Query(
        default=None, description="Latitude for location bias"
    ),
    lng: Optional[float] = Query(
        default=None, description="Longitude for location bias"
    ),
    limit: int = Query(default=10, ge=1, le=20, description="Max results"),
    maps: MapsService = Depends(get_maps_service),
) -> List[Dict[str, Any]]:
    """Search for places using Google Maps Places API (New).

    Supports optional location bias to prefer results near a given
    coordinate, improving relevance for destination-specific queries.

    Args:
        q: Free-text search query (e.g., "restaurants in Kyoto").
        lat: Optional latitude for location bias.
        lng: Optional longitude for location bias.
        limit: Maximum number of results (1–20).
        maps: Injected Google Maps service.

    Returns:
        list: Simplified place objects with name, address, rating, coords.

    Raises:
        HTTPException 503: If the Maps service is unavailable.
        HTTPException 500: If the search fails.
    """
    if not maps:
        raise HTTPException(status_code=503, detail="Maps service not available")

    location = None
    if lat is not None and lng is not None:
        location = {"lat": lat, "lng": lng}

    try:
        return await maps.search_places(q, location, max_results=limit)
    except Exception as exc:
        logger.exception("Place search failed for query: %s", q)
        raise HTTPException(status_code=500, detail="Place search failed")


@router.get("/geocode")
async def geocode(
    address: str = Query(..., min_length=2, description="Address to geocode"),
    maps: MapsService = Depends(get_maps_service),
) -> Dict[str, float]:
    """Geocode an address to latitude/longitude coordinates.

    Uses Google Maps Geocoding API to convert a human-readable address
    into geographic coordinates for map centering and location bias.

    Args:
        address: The address or place name to geocode.
        maps: Injected Google Maps service.

    Returns:
        dict: Object with ``lat`` and ``lng`` float values.

    Raises:
        HTTPException 503: If the Maps service is unavailable.
    """
    if not maps:
        raise HTTPException(status_code=503, detail="Maps service not available")

    return await maps.geocode(address)
