"""Application configuration loaded from environment variables.

This module defines the central Settings dataclass that provides
type-safe access to all environment variables required by TripFlow AI.
Settings are loaded once at startup via ``get_settings()`` and injected
into services through FastAPI's dependency injection system.

Security:
    - All secrets (API keys) are loaded **exclusively** from environment
      variables or a ``.env`` file that is never committed to version control.
    - The ``.gitignore`` includes ``.env`` to prevent accidental exposure.

Environment loading:
    ``python-dotenv`` is used to automatically load variables from the
    local ``.env`` file during development.  In production (Cloud Run),
    environment variables are injected via the deployment manifest.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

# SECURITY: Load .env file for local development only.
# In production (Cloud Run), secrets are injected as env vars.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    """Immutable application settings populated from environment variables.

    Using ``frozen=True`` ensures settings cannot be mutated after creation,
    providing thread-safety guarantees for concurrent request handling.

    Attributes:
        google_cloud_project: GCP project ID for Firestore and Cloud Logging.
        gemini_api_key: API key for Google Gemini AI (generative AI).
        gemini_model: Gemini model identifier (e.g., ``gemini-2.0-flash``).
        use_mock_data: When True, returns mock itinerary data instead of
            calling the Gemini API.  Useful for development and demo mode.
        google_maps_api_key: API key for Google Maps Platform services.
        port: HTTP port for the Uvicorn server (default: 8080).
        environment: Runtime environment — ``development`` or ``production``.
        frontend_url: Allowed CORS origin for the React frontend.
        rate_limit_per_minute: Max API requests per minute per client.
    """

    # ── Google Cloud ─────────────────────────────────────────────────
    google_cloud_project: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    )

    # ── Gemini AI (Google GenAI) ─────────────────────────────────────
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )
    gemini_model: str = field(
        default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    )
    use_mock_data: bool = field(
        default_factory=lambda: os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
    )

    # ── Google Maps Platform ─────────────────────────────────────────
    google_maps_api_key: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_MAPS_API_KEY", "")
    )

    # ── Server ───────────────────────────────────────────────────────
    port: int = field(
        default_factory=lambda: int(os.environ.get("PORT", "8080"))
    )
    environment: str = field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "development")
    )

    # ── CORS ─────────────────────────────────────────────────────────
    frontend_url: str = field(
        default_factory=lambda: os.environ.get(
            "FRONTEND_URL", "http://localhost:5173"
        )
    )

    # ── Rate Limiting ────────────────────────────────────────────────
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(
            os.environ.get("RATE_LIMIT_PER_MINUTE", "20")
        )
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Create and return application settings (cached singleton).

    Uses ``lru_cache`` to ensure the Settings object is only created once,
    improving efficiency by avoiding repeated environment variable lookups.

    Returns:
        Settings: Frozen dataclass with all configuration values.
    """
    return Settings()
