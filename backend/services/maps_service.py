"""Google Maps Platform service for place discovery and routing.

Google Services Used:
    - **Places API (New)** — Text Search for discovering attractions,
      restaurants, and activities near a destination.
    - **Geocoding API** — Convert human-readable addresses to
      latitude/longitude coordinates.
    - **Directions API** — Calculate travel time and distance between
      points for realistic itinerary scheduling.

Architecture:
    Uses ``httpx.AsyncClient`` for non-blocking HTTP requests, enabling
    high concurrency under FastAPI's async event loop.  The client is
    created once at initialization and reused across all requests for
    connection pooling efficiency.

Security:
    API keys are passed via HTTP headers (``X-Goog-Api-Key``) rather
    than URL parameters for the Places API (New), following Google's
    recommended security practice.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from core.config import Settings

logger = logging.getLogger(__name__)

PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


class MapsService:
    """Wrapper around Google Maps Platform APIs."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.google_maps_api_key
        self._client = httpx.AsyncClient(timeout=15.0)

    async def geocode(self, address: str) -> dict[str, float]:
        """Convert an address to latitude/longitude coordinates.

        Returns:
            dict with ``lat`` and ``lng`` keys.
        """
        params = {"address": address, "key": self._api_key}
        response = await self._client.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            logger.warning("Geocoding failed for '%s': %s", address, data.get("status"))
            return {"lat": 0.0, "lng": 0.0}

        location = data["results"][0]["geometry"]["location"]
        return {"lat": location["lat"], "lng": location["lng"]}

    async def search_places(
        self,
        query: str,
        location: dict[str, float] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for places using the Places API (New) Text Search.

        Returns a simplified list of place dicts.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": (
                "places.displayName,"
                "places.formattedAddress,"
                "places.location,"
                "places.rating,"
                "places.types,"
                "places.editorialSummary,"
                "places.photos,"
                "places.currentOpeningHours,"
                "places.priceLevel"
            ),
        }

        body: dict[str, Any] = {
            "textQuery": query,
            "maxResultCount": max_results,
            "languageCode": "en",
        }

        if location:
            body["locationBias"] = {
                "circle": {
                    "center": {
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                    },
                    "radius": 30000.0,  # 30 km
                }
            }

        response = await self._client.post(
            PLACES_NEARBY_URL, headers=headers, json=body
        )
        response.raise_for_status()
        data = response.json()

        return [self._simplify_place(p) for p in data.get("places", [])]

    async def get_directions(
        self,
        origin: dict[str, float],
        destination: dict[str, float],
        mode: str = "driving",
    ) -> dict[str, Any]:
        """Get directions between two points.

        Returns:
            dict with ``distance``, ``duration``, and ``polyline`` keys.
        """
        params = {
            "origin": f"{origin['lat']},{origin['lng']}",
            "destination": f"{destination['lat']},{destination['lng']}",
            "mode": mode,
            "key": self._api_key,
        }
        response = await self._client.get(DIRECTIONS_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("routes"):
            return {"distance": "N/A", "duration": "N/A", "polyline": ""}

        leg = data["routes"][0]["legs"][0]
        return {
            "distance": leg["distance"]["text"],
            "duration": leg["duration"]["text"],
            "polyline": data["routes"][0]["overview_polyline"]["points"],
        }

    async def get_place_context_for_ai(
        self, destination: str, interests: list[str]
    ) -> str:
        """Build a text context of real places for the Gemini prompt.

        This enriches AI generation with actual Google Maps data.
        """
        location = await self.geocode(destination)
        if location["lat"] == 0.0:
            return ""

        all_places: list[dict] = []
        for interest in interests[:4]:  # Cap at 4 to limit API calls
            query = f"best {interest} places in {destination}"
            places = await self.search_places(query, location, max_results=5)
            all_places.extend(places)

        if not all_places:
            return ""

        lines = ["REAL PLACES DATA (from Google Maps — use these in the itinerary):"]
        for p in all_places:
            line = (
                f"- {p['name']} | {p.get('address', 'N/A')} | "
                f"Rating: {p.get('rating', 'N/A')} | "
                f"Lat: {p.get('lat', 0)}, Lng: {p.get('lng', 0)} | "
                f"Indoor: {p.get('is_indoor', False)}"
            )
            if p.get("summary"):
                line += f" | {p['summary']}"
            lines.append(line)

        return "\n".join(lines)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    # ── Private helpers ─────────────────────────────────────────────────

    @staticmethod
    def _simplify_place(place: dict) -> dict[str, Any]:
        """Flatten a Places API (New) response into a simpler dict."""
        location = place.get("location", {})
        display_name = place.get("displayName", {})
        editorial = place.get("editorialSummary", {})
        types = place.get("types", [])

        # Heuristic: if it has indoor-related types, mark as indoor
        indoor_types = {
            "museum", "art_gallery", "shopping_mall", "restaurant",
            "cafe", "library", "movie_theater", "spa",
        }
        is_indoor = bool(indoor_types & set(types))

        photo_url = None
        photos = place.get("photos", [])
        if photos:
            photo_url = photos[0].get("name", "")

        return {
            "name": display_name.get("text", "Unknown"),
            "address": place.get("formattedAddress", ""),
            "lat": location.get("latitude", 0),
            "lng": location.get("longitude", 0),
            "rating": place.get("rating"),
            "types": types,
            "summary": editorial.get("text", ""),
            "is_indoor": is_indoor,
            "photo_ref": photo_url,
            "price_level": place.get("priceLevel"),
        }
