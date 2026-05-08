"""Gemini AI service for itinerary generation and adaptation."""

from __future__ import annotations

import json
import logging
import re
from datetime import timedelta

from google import genai
from google.genai import types

from config import Settings
from models.user_input import (
    AdaptRequest,
    DayPlan,
    Itinerary,
    PlaceDetail,
    TripRequest,
)

logger = logging.getLogger(__name__)

# ── Prompt Templates ────────────────────────────────────────────────────

ITINERARY_SYSTEM_PROMPT = """You are TripFlow AI, an expert travel planner.
Generate a detailed day-by-day travel itinerary as valid JSON.

RULES:
- Respect the budget strictly. Total cost must not exceed the budget.
- Schedule activities between 08:00 and 21:00.
- Include 3 meals per day (breakfast, lunch, dinner) from local restaurants.
- Include 3-5 activities per day based on interests.
- Provide realistic cost estimates in the specified currency.
- Add travel tips for each day.
- Mark activities as indoor or outdoor.
- Ensure logical geographic ordering to minimize travel time.
- Use realistic time slots (format: "HH:MM - HH:MM").
"""

ITINERARY_USER_TEMPLATE = """Create a travel itinerary with these details:

Destination: {destination}
Dates: {start_date} to {end_date} ({total_days} days)
Budget: {budget} {currency} (total for {group_size} person(s))
Interests: {interests}
{special_requirements}

{places_context}

Respond ONLY with valid JSON matching this exact schema:
{{
  "destination": "string",
  "summary": "2-3 sentence overview of the trip",
  "total_cost": number,
  "budget_utilization": number (percentage 0-100),
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "theme": "string describing the day's theme",
      "travel_tip": "practical tip for this day",
      "day_cost": number,
      "activities": [
        {{
          "name": "string",
          "description": "1-2 sentences",
          "category": "culture|food|adventure|nature|shopping|relaxation|nightlife|history",
          "latitude": number,
          "longitude": number,
          "estimated_cost": number,
          "duration_minutes": number,
          "time_slot": "HH:MM - HH:MM",
          "rating": number or null,
          "is_indoor": boolean,
          "address": "string"
        }}
      ],
      "meals": [
        {{
          "name": "Restaurant Name",
          "description": "cuisine type and specialty",
          "category": "food",
          "latitude": number,
          "longitude": number,
          "estimated_cost": number,
          "duration_minutes": 45,
          "time_slot": "HH:MM - HH:MM",
          "rating": number or null,
          "is_indoor": true,
          "address": "string"
        }}
      ]
    }}
  ]
}}"""

ADAPT_SYSTEM_PROMPT = """You are TripFlow AI's adaptation engine.
Given an existing itinerary and changed conditions, modify the plan intelligently.

RULES:
- Only change what's necessary. Preserve the user's original preferences.
- If weather is bad, swap outdoor activities with indoor alternatives.
- If budget changed, adjust by replacing expensive items with cheaper alternatives, not by removing activities.
- Explain each change clearly.
- Keep the same JSON structure as the original itinerary.
- Total cost must respect the new budget if provided.
"""

ADAPT_USER_TEMPLATE = """Adapt this itinerary based on changed conditions:

CURRENT ITINERARY:
{current_itinerary}

CHANGES NEEDED:
{changes}

{weather_context}

Respond ONLY with valid JSON:
{{
  "adapted_itinerary": {{ ... same structure as input itinerary ... }},
  "changes": ["Human-readable description of each change made"],
  "reason": "Overall explanation of why changes were made"
}}"""


class GeminiService:
    """Wrapper around the Gemini API for itinerary generation."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._client = None

    def _get_client(self):
        """Lazy-init the Gemini client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set. Add it to backend/.env"
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate_itinerary(
        self,
        request: TripRequest,
        places_context: str = "",
    ) -> Itinerary:
        """Generate a complete trip itinerary using Gemini."""
        total_days = (request.end_date - request.start_date).days + 1

        special_req = ""
        if request.special_requirements:
            special_req = f"Special requirements: {request.special_requirements}"

        user_prompt = ITINERARY_USER_TEMPLATE.format(
            destination=request.destination,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            total_days=total_days,
            budget=request.budget,
            currency=request.currency,
            group_size=request.group_size,
            interests=", ".join(i.value for i in request.interests),
            special_requirements=special_req,
            places_context=places_context,
        )

        logger.info("Generating itinerary for %s (%d days)", request.destination, total_days)

        response = await self._call_gemini(ITINERARY_SYSTEM_PROMPT, user_prompt)
        data = self._parse_json(response)

        return self._build_itinerary(data, request, total_days)

    async def adapt_itinerary(
        self,
        current: Itinerary,
        adapt_request: AdaptRequest,
        weather_info: dict | None = None,
    ) -> dict:
        """Adapt an existing itinerary based on changed conditions."""
        changes_parts: list[str] = []
        if adapt_request.new_budget is not None:
            changes_parts.append(
                f"Budget changed to {adapt_request.new_budget} {current.currency}"
            )
        if adapt_request.excluded_places:
            changes_parts.append(
                f"Remove these places: {', '.join(adapt_request.excluded_places)}"
            )
        if adapt_request.reason:
            changes_parts.append(f"User note: {adapt_request.reason}")
        if adapt_request.weather_check and weather_info:
            changes_parts.append("Adjust for weather conditions shown below.")

        weather_ctx = ""
        if weather_info:
            weather_ctx = f"WEATHER FORECAST:\n{json.dumps(weather_info, indent=2)}"

        user_prompt = ADAPT_USER_TEMPLATE.format(
            current_itinerary=current.model_dump_json(indent=2),
            changes="\n".join(f"- {c}" for c in changes_parts),
            weather_context=weather_ctx,
        )

        logger.info("Adapting itinerary %s", current.id)
        response = await self._call_gemini(ADAPT_SYSTEM_PROMPT, user_prompt)
        return self._parse_json(response)

    # ── Private helpers ─────────────────────────────────────────────────

    async def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Make an async call to the Gemini API."""
        response = await self._get_client().aio.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        return response.text

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract and parse JSON from Gemini's response."""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Last resort: find first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        logger.error("Failed to parse Gemini response as JSON: %s", text[:500])
        raise ValueError("Could not parse AI response. Please try again.")

    @staticmethod
    def _build_itinerary(
        data: dict, request: TripRequest, total_days: int
    ) -> Itinerary:
        """Build an Itinerary model from parsed Gemini JSON."""
        days: list[DayPlan] = []
        for day_data in data.get("days", []):
            activities = [
                PlaceDetail(**a) for a in day_data.get("activities", [])
            ]
            meals = [PlaceDetail(**m) for m in day_data.get("meals", [])]
            days.append(
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

        return Itinerary(
            destination=request.destination,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            total_days=total_days,
            total_cost=data.get("total_cost", 0),
            budget=request.budget,
            currency=request.currency,
            group_size=request.group_size,
            days=days,
            summary=data.get("summary", ""),
            budget_utilization=data.get("budget_utilization", 0),
        )
