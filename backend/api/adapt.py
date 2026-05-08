"""Itinerary adaptation router."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, HTTPException, Depends

from models.user_input import AdaptRequest, AdaptationResult, Itinerary, DayPlan, PlaceDetail
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from services.weather_service import WeatherService
from services.firestore_service import FirestoreService
from api.dependencies import get_gemini_service, get_maps_service, get_weather_service, get_firestore_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/adapt", tags=["adapt"])


@router.post("/", response_model=AdaptationResult)
async def adapt_itinerary(
    request: AdaptRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    maps: MapsService = Depends(get_maps_service),
    weather: WeatherService = Depends(get_weather_service),
    firestore: FirestoreService = Depends(get_firestore_service)
) -> AdaptationResult:
    """Adapt an existing itinerary based on changed conditions."""

    # Load current itinerary
    current = await firestore.get_itinerary(request.itinerary_id)
    if not current:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Optionally update budget
    if request.new_budget is not None:
        current.budget = request.new_budget

    # Fetch weather if requested
    weather_info = None
    if request.weather_check:
        try:
            coords = await maps.geocode(current.destination)
            if coords["lat"] != 0.0:
                weather_info = await weather.get_forecast(
                    coords["lat"],
                    coords["lng"],
                    date.fromisoformat(current.start_date),
                    date.fromisoformat(current.end_date),
                )
        except Exception as exc:
            logger.warning("Weather fetch failed (non-fatal): %s", exc)

    try:
        result = await gemini.adapt_itinerary(current, request, weather_info)

        # Build adapted itinerary from response
        adapted_data = result.get("adapted_itinerary", {})
        adapted = Itinerary(
            id=f"{current.id}_adapted",
            destination=current.destination,
            start_date=current.start_date,
            end_date=current.end_date,
            total_days=current.total_days,
            total_cost=adapted_data.get("total_cost", current.total_cost),
            budget=request.new_budget or current.budget,
            currency=current.currency,
            group_size=current.group_size,
            days=[],
            summary=adapted_data.get("summary", current.summary),
            budget_utilization=adapted_data.get("budget_utilization", 0),
        )

        # Parse days from adapted data
        for day_data in adapted_data.get("days", []):
            activities = [PlaceDetail(**a) for a in day_data.get("activities", [])]
            meals = [PlaceDetail(**m) for m in day_data.get("meals", [])]
            adapted.days.append(
                DayPlan(
                    day_number=day_data.get("day_number", 0),
                    date=day_data.get("date", ""),
                    theme=day_data.get("theme", ""),
                    activities=activities,
                    meals=meals,
                    day_cost=day_data.get("day_cost", 0),
                    travel_tip=day_data.get("travel_tip", ""),
                )
            )

        # Save adapted version
        try:
            await firestore.save_itinerary(adapted)
        except Exception:
            pass

        return AdaptationResult(
            original_itinerary_id=request.itinerary_id,
            adapted_itinerary=adapted,
            changes=result.get("changes", []),
            reason=result.get("reason", ""),
            weather_info=weather_info,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Adaptation failed")
        raise HTTPException(status_code=500, detail="Failed to adapt itinerary")


@router.get("/weather")
async def get_weather(
    lat: float,
    lng: float,
    start_date: str,
    end_date: str,
    weather: WeatherService = Depends(get_weather_service)
) -> dict:
    """Get weather forecast for a location and date range."""
    try:
        return await weather.get_forecast(
            lat, lng,
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
        )
    except Exception as exc:
        logger.exception("Weather fetch failed")
        raise HTTPException(status_code=500, detail="Weather service error")
