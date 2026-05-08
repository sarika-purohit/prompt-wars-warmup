"""Tests for the Gemini service — JSON parsing logic."""

import pytest
from services.gemini_service import GeminiService


class TestParseJson:
    """Test the static JSON parser used on Gemini responses."""

    def test_direct_json(self):
        raw = '{"destination": "Jaipur", "total_cost": 12000}'
        result = GeminiService._parse_json(raw)
        assert result["destination"] == "Jaipur"
        assert result["total_cost"] == 12000

    def test_json_in_code_block(self):
        raw = '```json\n{"destination": "Goa", "total_cost": 8000}\n```'
        result = GeminiService._parse_json(raw)
        assert result["destination"] == "Goa"

    def test_json_with_surrounding_text(self):
        raw = 'Here is your itinerary:\n{"destination": "Delhi", "days": []}\nEnjoy!'
        result = GeminiService._parse_json(raw)
        assert result["destination"] == "Delhi"

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Could not parse"):
            GeminiService._parse_json("This is not JSON at all")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            GeminiService._parse_json("")
