"""Integration tests for API endpoints.

Tests the FastAPI routes using ``TestClient`` to validate:
- Input validation (Pydantic model constraints).
- Error handling (proper HTTP status codes).
- Health check endpoints.

These tests do NOT require live API keys — they exercise the
request validation and routing layers only.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client with lifespan events."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoints:
    """Test health check and root endpoints."""

    def test_health_check(self, client):
        """GET /health should return 200 with service info."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "tripflow-api"
        assert "version" in data

    def test_root_endpoint(self, client):
        """GET / should return API discovery information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "TripFlow AI API"
        assert "docs" in data


class TestItineraryValidation:
    """Test input validation for itinerary generation."""

    def test_missing_destination(self, client):
        """Should reject requests with missing destination."""
        response = client.post("/api/itinerary/generate", json={
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "budget": 2000,
            "interests": ["culture"],
        })
        assert response.status_code == 422

    def test_negative_budget(self, client):
        """Should reject requests with negative budget."""
        response = client.post("/api/itinerary/generate", json={
            "destination": "Tokyo",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "budget": -100,
            "interests": ["culture"],
        })
        assert response.status_code == 422

    def test_short_destination(self, client):
        """Should reject destination shorter than 2 characters."""
        response = client.post("/api/itinerary/generate", json={
            "destination": "A",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "budget": 1000,
            "interests": ["food"],
        })
        assert response.status_code == 422

    def test_invalid_interest(self, client):
        """Should reject invalid interest categories."""
        response = client.post("/api/itinerary/generate", json={
            "destination": "Paris",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "budget": 1000,
            "interests": ["invalid_interest"],
        })
        assert response.status_code == 422

    def test_group_size_too_large(self, client):
        """Should reject group size exceeding 20."""
        response = client.post("/api/itinerary/generate", json={
            "destination": "London",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "budget": 5000,
            "interests": ["culture"],
            "group_size": 25,
        })
        assert response.status_code == 422


class TestPlacesValidation:
    """Test input validation for places search."""

    def test_search_requires_query(self, client):
        """Should reject place search without query parameter."""
        response = client.get("/api/places/search")
        assert response.status_code == 422

    def test_search_short_query(self, client):
        """Should reject query shorter than 2 characters."""
        response = client.get("/api/places/search", params={"q": "a"})
        assert response.status_code == 422


class TestSecurityHeaders:
    """Test that security headers are present on responses."""

    def test_x_content_type_options(self, client):
        """Should include X-Content-Type-Options: nosniff header."""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        """Should include X-Frame-Options: DENY header."""
        response = client.get("/health")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection(self, client):
        """Should include X-XSS-Protection header."""
        response = client.get("/health")
        assert "1" in response.headers.get("X-XSS-Protection", "")

    def test_referrer_policy(self, client):
        """Should include Referrer-Policy header."""
        response = client.get("/health")
        assert response.headers.get("Referrer-Policy") is not None
