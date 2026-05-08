"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # Google Cloud
    google_cloud_project: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    )

    # Gemini AI
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )
    gemini_model: str = field(
        default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    )
    use_mock_data: bool = field(
        default_factory=lambda: os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
    )

    # Google Maps
    google_maps_api_key: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_MAPS_API_KEY", "")
    )

    # Server
    port: int = field(
        default_factory=lambda: int(os.environ.get("PORT", "8080"))
    )
    environment: str = field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "development")
    )

    # CORS
    frontend_url: str = field(
        default_factory=lambda: os.environ.get(
            "FRONTEND_URL", "http://localhost:5173"
        )
    )

    # Rate limiting
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(
            os.environ.get("RATE_LIMIT_PER_MINUTE", "20")
        )
    )


def get_settings() -> Settings:
    """Create and return application settings."""
    return Settings()
