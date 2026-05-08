"""Weather service using the free Open-Meteo API.

Provides daily weather forecasts for trip destinations to enable
weather-aware itinerary adaptation.  Bad weather detection (rain,
storms) triggers automatic outdoor→indoor activity swaps.

Efficiency:
    Uses the Open-Meteo API which requires no API key, reducing
    configuration overhead.  Responses are lightweight JSON with
    only the fields needed for adaptation decisions.

Architecture:
    Uses ``httpx.AsyncClient`` for non-blocking HTTP requests.
    WMO weather codes are translated to human-readable conditions.
"""

from __future__ import annotations

import logging
from datetime import date

import httpx

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherService:
    """Fetch weather forecasts from the free Open-Meteo API."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=10.0)

    async def get_forecast(
        self,
        lat: float,
        lng: float,
        start_date: date,
        end_date: date,
    ) -> dict:
        """Get daily weather forecast for the given location and date range.

        Returns a simplified dict with daily forecasts.
        """
        params = {
            "latitude": lat,
            "longitude": lng,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "weathercode,"
                "windspeed_10m_max"
            ),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto",
        }

        try:
            response = await self._client.get(FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, Exception) as exc:
            logger.warning("Weather API call failed: %s", exc)
            return {"available": False, "message": "Weather data unavailable"}

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        forecasts = []

        for i, d in enumerate(dates):
            weather_code = daily.get("weathercode", [0])[i]
            forecasts.append({
                "date": d,
                "temp_max": daily.get("temperature_2m_max", [0])[i],
                "temp_min": daily.get("temperature_2m_min", [0])[i],
                "rain_probability": daily.get("precipitation_probability_max", [0])[i],
                "wind_speed_max": daily.get("windspeed_10m_max", [0])[i],
                "weather_code": weather_code,
                "condition": self._weather_code_to_text(weather_code),
                "is_bad_weather": (
                    daily.get("precipitation_probability_max", [0])[i] > 60
                    or weather_code >= 61
                ),
            })

        return {
            "available": True,
            "location": {"lat": lat, "lng": lng},
            "forecasts": forecasts,
            "has_bad_weather": any(f["is_bad_weather"] for f in forecasts),
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    @staticmethod
    def _weather_code_to_text(code: int) -> str:
        """Convert WMO weather code to human-readable text."""
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snowfall",
            73: "Moderate snowfall",
            75: "Heavy snowfall",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return codes.get(code, "Unknown")
