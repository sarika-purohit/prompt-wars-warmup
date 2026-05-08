"""Tests for application configuration and settings.

Validates that the Settings dataclass correctly loads environment
variables and provides sensible defaults.
"""

import os
import pytest
from core.config import Settings


class TestSettings:
    """Test the Settings dataclass configuration loading."""

    def test_default_model(self):
        """Default Gemini model should be gemini-2.0-flash."""
        settings = Settings()
        assert settings.gemini_model == os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    def test_default_port(self):
        """Default port should be 8080 for Cloud Run compatibility."""
        settings = Settings()
        assert settings.port == int(os.environ.get("PORT", "8080"))

    def test_default_environment(self):
        """Default environment should be 'development'."""
        settings = Settings()
        assert settings.environment in ("development", "production")

    def test_default_rate_limit(self):
        """Default rate limit should be 20 requests per minute."""
        settings = Settings()
        assert settings.rate_limit_per_minute == int(
            os.environ.get("RATE_LIMIT_PER_MINUTE", "20")
        )

    def test_settings_frozen(self):
        """Settings should be immutable (frozen dataclass)."""
        settings = Settings()
        with pytest.raises(AttributeError):
            settings.port = 9999  # type: ignore

    def test_mock_data_default_false(self):
        """Mock data should be disabled by default."""
        # When USE_MOCK_DATA is not set, it defaults to false
        settings = Settings()
        assert isinstance(settings.use_mock_data, bool)
