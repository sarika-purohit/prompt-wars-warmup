"""Pydantic models for API request and response schemas."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────

class Interest(str, Enum):
    """Travel interest categories."""
    CULTURE = "culture"
    FOOD = "food"
    ADVENTURE = "adventure"
    NATURE = "nature"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    NIGHTLIFE = "nightlife"
    HISTORY = "history"


# ── Request Models ─────────────────────────────────────────────────────

class TripRequest(BaseModel):
    """Input from the user to generate an itinerary."""
    destination: str = Field(..., min_length=2, max_length=200, examples=["Jaipur, Rajasthan"])
    start_date: date = Field(..., examples=["2026-06-01"])
    end_date: date = Field(..., examples=["2026-06-04"])
    budget: float = Field(..., gt=0, examples=[15000])
    currency: str = Field(default="INR", max_length=3, examples=["INR", "USD"])
    interests: list[Interest] = Field(
        default_factory=lambda: [Interest.CULTURE, Interest.FOOD],
        min_length=1,
    )
    group_size: int = Field(default=1, ge=1, le=20, examples=[2])
    special_requirements: Optional[str] = Field(
        default=None, max_length=500,
        examples=["Vegetarian food only, wheelchair accessible"]
    )


class AdaptRequest(BaseModel):
    """Request to adapt an existing itinerary."""
    itinerary_id: str = Field(..., min_length=1)
    new_budget: Optional[float] = Field(default=None, gt=0)
    weather_check: bool = Field(default=True)
    excluded_places: list[str] = Field(default_factory=list)
    reason: Optional[str] = Field(
        default=None, max_length=300,
        examples=["It's raining, suggest indoor activities"]
    )


# ── Response Models ────────────────────────────────────────────────────

class PlaceDetail(BaseModel):
    """A single place/attraction in the itinerary."""
    name: str
    description: str
    category: str
    latitude: float
    longitude: float
    estimated_cost: float = 0
    duration_minutes: int = 60
    time_slot: str = ""          # e.g. "09:00 - 10:30"
    rating: Optional[float] = None
    photo_url: Optional[str] = None
    is_indoor: bool = False
    address: Optional[str] = None


class DayPlan(BaseModel):
    """A single day's itinerary."""
    day_number: int
    date: str
    theme: str = ""              # e.g. "Heritage & Culture"
    activities: list[PlaceDetail] = Field(default_factory=list)
    meals: list[PlaceDetail] = Field(default_factory=list)
    day_cost: float = 0
    travel_tip: str = ""


class Itinerary(BaseModel):
    """Complete trip itinerary."""
    id: str = ""
    destination: str
    start_date: str
    end_date: str
    total_days: int
    total_cost: float
    budget: float
    currency: str = "INR"
    group_size: int = 1
    days: list[DayPlan] = Field(default_factory=list)
    summary: str = ""
    budget_utilization: float = 0  # percentage


class AdaptationResult(BaseModel):
    """Result of an itinerary adaptation."""
    original_itinerary_id: str
    adapted_itinerary: Itinerary
    changes: list[str] = Field(default_factory=list)
    reason: str = ""
    weather_info: Optional[dict] = None
