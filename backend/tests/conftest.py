"""Shared test fixtures and configuration for pytest.

Provides reusable fixtures for creating test data (TripRequest,
Itinerary) and mocking service dependencies.
"""

from __future__ import annotations

import pytest
from datetime import date

from core.config import Settings
from models.user_input import TripRequest, Interest, Itinerary, DayPlan, PlaceDetail
from services.gemini_service import GeminiService


@pytest.fixture
def sample_settings() -> Settings:
    """Provide test settings with mock mode enabled."""
    return Settings()


@pytest.fixture
def sample_trip_request() -> TripRequest:
    """Provide a valid TripRequest for testing."""
    return TripRequest(
        destination="Kyoto, Japan",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        budget=2000,
        currency="USD",
        interests=[Interest.CULTURE, Interest.FOOD],
        group_size=2,
    )


@pytest.fixture
def sample_itinerary() -> Itinerary:
    """Provide a minimal Itinerary for testing."""
    return Itinerary(
        id="test123",
        destination="Kyoto, Japan",
        start_date="2026-06-01",
        end_date="2026-06-03",
        total_days=3,
        total_cost=1500,
        budget=2000,
        currency="USD",
        group_size=2,
        days=[
            DayPlan(
                day_number=1,
                date="2026-06-01",
                theme="Culture Day",
                day_cost=500,
                activities=[
                    PlaceDetail(
                        name="Kinkaku-ji",
                        description="Golden Pavilion temple",
                        category="culture",
                        latitude=35.0394,
                        longitude=135.7292,
                        estimated_cost=100,
                        duration_minutes=90,
                        time_slot="10:00 - 11:30",
                        rating=4.8,
                        is_indoor=False,
                    )
                ],
                meals=[
                    PlaceDetail(
                        name="Nishiki Market",
                        description="Famous food market",
                        category="food",
                        latitude=35.005,
                        longitude=135.764,
                        estimated_cost=50,
                        duration_minutes=60,
                        time_slot="12:00 - 13:00",
                        rating=4.5,
                        is_indoor=True,
                    )
                ],
                travel_tip="Arrive early to avoid crowds.",
            )
        ],
        summary="A cultural exploration of Kyoto.",
        budget_utilization=75.0,
    )


@pytest.fixture
def gemini_service(sample_settings) -> GeminiService:
    """Provide a GeminiService instance for testing."""
    return GeminiService(sample_settings)
