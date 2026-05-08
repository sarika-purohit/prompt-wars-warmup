"""Tests for Pydantic request models — validation."""

import pytest
from datetime import date
from models.user_input import TripRequest, Interest


class TestTripRequest:
    """Validate TripRequest model constraints."""

    def test_valid_request(self):
        req = TripRequest(
            destination="Jaipur",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
            budget=15000,
            interests=[Interest.CULTURE, Interest.FOOD],
        )
        assert req.destination == "Jaipur"
        assert req.group_size == 1  # default

    def test_budget_must_be_positive(self):
        with pytest.raises(Exception):
            TripRequest(
                destination="Goa",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 3),
                budget=-100,
                interests=[Interest.NATURE],
            )

    def test_destination_min_length(self):
        with pytest.raises(Exception):
            TripRequest(
                destination="A",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 3),
                budget=5000,
                interests=[Interest.FOOD],
            )

    def test_group_size_max(self):
        with pytest.raises(Exception):
            TripRequest(
                destination="Mumbai",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 2),
                budget=10000,
                interests=[Interest.SHOPPING],
                group_size=25,
            )
