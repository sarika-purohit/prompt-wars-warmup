"""Places search router."""

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
    lat: Optional[float] = Query(default=None, description="Latitude for location bias"),
    lng: Optional[float] = Query(default=None, description="Longitude for location bias"),
    limit: int = Query(default=10, ge=1, le=20),
    maps: MapsService = Depends(get_maps_service)
) -> List[Dict[str, Any]]:
    """Search for places using Google Maps."""
    if not maps:
        raise HTTPException(status_code=503, detail="Maps service not available")

    location = None
    if lat is not None and lng is not None:
        location = {"lat": lat, "lng": lng}

    try:
        return await maps.search_places(q, location, max_results=limit)
    except Exception as exc:
        logger.exception("Place search failed")
        raise HTTPException(status_code=500, detail="Place search failed")


@router.get("/geocode")
async def geocode(address: str = Query(..., min_length=2)) -> dict[str, float]:
    """Geocode an address to coordinates."""
    if not _maps:
        raise HTTPException(status_code=503, detail="Maps service not available")

    return await _maps.geocode(address)
