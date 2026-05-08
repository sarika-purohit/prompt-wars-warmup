"""Google Gemini AI service for itinerary generation and adaptation.

This module wraps the Google Gemini 2.0 Flash API to provide:
    1. **Itinerary Generation** — creates structured, budget-aware travel
       plans as valid JSON using the ``google-genai`` SDK.
    2. **Itinerary Adaptation** — modifies existing plans based on
       weather changes, budget updates, or user preferences.
    3. **Mock Mode** — returns realistic mock data for development
       and demo purposes when ``USE_MOCK_DATA=true``.

Google Services:
    - Google Gemini 2.0 Flash — fast generative AI with structured output.
    - Uses the ``google-genai`` Python SDK for async API calls.

Architecture:
    The service is initialized once at startup with API credentials from
    the Settings dataclass and injected into route handlers via FastAPI's
    ``Depends()`` system.  The Gemini client is lazy-initialized on first
    use to avoid blocking application startup.

Efficiency:
    - Lazy client initialization avoids startup overhead.
    - Structured JSON output schema in the prompt minimizes post-processing.
    - Robust 3-stage JSON parser handles markdown-wrapped responses.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import timedelta

from google import genai
from google.genai import types

from core.config import Settings
from models.user_input import (
    AdaptRequest,
    DayPlan,
    Itinerary,
    PlaceDetail,
    TripRequest,
)

logger = logging.getLogger(__name__)

# ── Prompt Templates ─────────────────────────────────────────────────────
# These prompts are engineered to produce valid, parseable JSON from Gemini.

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
    """Wrapper around the Google Gemini API for AI-powered itinerary operations.

    Supports two modes:
        - **Live mode**: Calls Gemini 2.0 Flash API for real AI generation.
        - **Mock mode**: Returns realistic mock data for development/demos.

    Attributes:
        _settings: Application configuration with API keys and model name.
        _api_key: Google Gemini API key.
        _model: Gemini model identifier (e.g., ``gemini-2.0-flash``).
        _client: Lazy-initialized ``genai.Client`` instance.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the Gemini service with application settings.

        Args:
            settings: Configuration containing Gemini API key and model name.
        """
        self._settings = settings
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._client = None

    def _get_client(self) -> genai.Client:
        """Lazy-initialize the Gemini API client.

        EFFICIENCY: Client is created on first use, not at startup,
        so that application boot is never blocked by network issues.

        Returns:
            genai.Client: Configured Gemini API client.

        Raises:
            ValueError: If ``GEMINI_API_KEY`` is not set.
        """
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set. Add it to backend/.env"
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    # ── Public API ───────────────────────────────────────────────────────

    async def generate_itinerary(
        self,
        request: TripRequest,
        places_context: str = "",
    ) -> Itinerary:
        """Generate a complete trip itinerary using Gemini AI.

        If ``USE_MOCK_DATA`` is enabled, returns realistic mock data
        without making any API calls.

        Args:
            request: Validated trip planning parameters.
            places_context: Real Google Maps places data to ground the AI.

        Returns:
            Itinerary: Complete day-by-day travel plan.

        Raises:
            ValueError: If the Gemini response cannot be parsed as JSON.
        """
        # EFFICIENCY: Skip API call entirely in mock/demo mode
        if self._settings.use_mock_data:
            logger.info("Using mock data for itinerary generation")
            return self._get_mock_itinerary(request)

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

        logger.info(
            "Generating itinerary for %s (%d days) via Gemini %s",
            request.destination,
            total_days,
            self._model,
        )

        response = await self._call_gemini(ITINERARY_SYSTEM_PROMPT, user_prompt)
        data = self._parse_json(response)

        return self._build_itinerary(data, request, total_days)

    async def adapt_itinerary(
        self,
        current: Itinerary,
        adapt_request: AdaptRequest,
        weather_info: dict | None = None,
    ) -> dict:
        """Adapt an existing itinerary based on changed conditions.

        Uses Gemini AI to intelligently modify the plan based on
        weather forecasts, budget changes, or user preferences.

        Args:
            current: The existing itinerary to modify.
            adapt_request: Parameters describing what changed.
            weather_info: Optional weather forecast data.

        Returns:
            dict: Adapted itinerary with change descriptions.
        """
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

        logger.info("Adapting itinerary %s via Gemini", current.id)
        response = await self._call_gemini(ADAPT_SYSTEM_PROMPT, user_prompt)
        return self._parse_json(response)

    # ── Private Helpers ──────────────────────────────────────────────────

    def _get_mock_itinerary(self, request: TripRequest) -> Itinerary:
        """Generate realistic mock itinerary data for development/demos.

        Creates a properly structured Itinerary with activities, meals,
        and budget tracking — without making any API calls.

        Args:
            request: The trip planning request to mock.

        Returns:
            Itinerary: A complete mock itinerary matching the request.
        """
        total_days = (request.end_date - request.start_date).days + 1
        per_day_budget = request.budget / total_days
        days: list[DayPlan] = []

        for i in range(1, total_days + 1):
            day_date = (request.start_date + timedelta(days=i - 1)).isoformat()
            days.append(DayPlan(
                day_number=i,
                date=day_date,
                theme=f"Exploring {request.destination} — Day {i}",
                travel_tip="Wear comfortable shoes and carry a water bottle!",
                day_cost=round(per_day_budget * 0.8, 2),
                activities=[
                    PlaceDetail(
                        name=f"Cultural Landmark {i}",
                        description="A must-visit attraction with rich history.",
                        category="culture",
                        latitude=0.0, longitude=0.0,
                        estimated_cost=round(per_day_budget * 0.15, 2),
                        duration_minutes=120,
                        time_slot="10:00 - 12:00",
                        rating=4.5, is_indoor=True,
                        address="123 Heritage Street",
                    ),
                    PlaceDetail(
                        name=f"Nature Park {i}",
                        description="Beautiful natural scenery and walking trails.",
                        category="nature",
                        latitude=0.0, longitude=0.0,
                        estimated_cost=round(per_day_budget * 0.10, 2),
                        duration_minutes=120,
                        time_slot="14:00 - 16:00",
                        rating=4.7, is_indoor=False,
                        address="456 Park Avenue",
                    ),
                ],
                meals=[
                    PlaceDetail(
                        name=f"Breakfast Café {i}",
                        description="Local breakfast specialties.",
                        category="food",
                        latitude=0.0, longitude=0.0,
                        estimated_cost=round(per_day_budget * 0.10, 2),
                        duration_minutes=45,
                        time_slot="08:00 - 08:45",
                        rating=4.0, is_indoor=True,
                        address="789 Morning Lane",
                    ),
                    PlaceDetail(
                        name=f"Lunch Restaurant {i}",
                        description="Popular midday dining spot.",
                        category="food",
                        latitude=0.0, longitude=0.0,
                        estimated_cost=round(per_day_budget * 0.15, 2),
                        duration_minutes=60,
                        time_slot="12:30 - 13:30",
                        rating=4.2, is_indoor=True,
                        address="321 Lunch Boulevard",
                    ),
                    PlaceDetail(
                        name=f"Dinner Restaurant {i}",
                        description="Fine dining with local cuisine.",
                        category="food",
                        latitude=0.0, longitude=0.0,
                        estimated_cost=round(per_day_budget * 0.20, 2),
                        duration_minutes=90,
                        time_slot="19:00 - 20:30",
                        rating=4.6, is_indoor=True,
                        address="654 Dinner Drive",
                    ),
                ],
            ))

        return Itinerary(
            destination=request.destination,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            total_days=total_days,
            total_cost=round(request.budget * 0.80, 2),
            budget=request.budget,
            currency=request.currency,
            group_size=request.group_size,
            days=days,
            summary=(
                f"A fantastic {total_days}-day trip to {request.destination} "
                f"featuring cultural landmarks, nature parks, and local cuisine. "
                f"Budget-optimized for {request.group_size} traveler(s)."
            ),
            budget_utilization=80.0,
        )

    async def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Make an async call to the Google Gemini API.

        Args:
            system_prompt: System-level instructions for the AI model.
            user_prompt: The user's specific request.

        Returns:
            str: Raw text response from Gemini.
        """
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
        """Extract and parse JSON from Gemini's text response.

        Uses a 3-stage parsing strategy to handle various output formats:
            1. Direct JSON parse (ideal case).
            2. Extract from markdown code block (```json ... ```).
            3. Find first ``{`` to last ``}`` (last resort).

        Args:
            text: Raw text response from the Gemini API.

        Returns:
            dict: Parsed JSON object.

        Raises:
            ValueError: If no valid JSON can be extracted.
        """
        # Stage 1: Direct parse (most efficient path)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Stage 2: Extract from markdown code block
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Stage 3: Find first { to last } (fallback)
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
        data: dict, request: TripRequest, total_days: int,
    ) -> Itinerary:
        """Build an Itinerary model from parsed Gemini JSON.

        Maps the raw AI output to strongly-typed Pydantic models,
        ensuring data consistency before it reaches the frontend.

        Args:
            data: Parsed JSON dict from Gemini's response.
            request: Original trip request for metadata.
            total_days: Calculated trip duration.

        Returns:
            Itinerary: Validated, structured itinerary object.
        """
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
