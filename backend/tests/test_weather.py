"""Tests for the weather service — code-to-text mapping."""

from services.weather_service import WeatherService


class TestWeatherCodeToText:
    """Test WMO weather code translation."""

    def test_clear_sky(self):
        assert WeatherService._weather_code_to_text(0) == "Clear sky"

    def test_rain(self):
        assert WeatherService._weather_code_to_text(63) == "Moderate rain"

    def test_thunderstorm(self):
        assert WeatherService._weather_code_to_text(95) == "Thunderstorm"

    def test_unknown_code(self):
        assert WeatherService._weather_code_to_text(999) == "Unknown"
