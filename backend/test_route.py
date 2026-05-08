import asyncio
from fastapi.testclient import TestClient
from main import app

with TestClient(app) as client:
    response = client.post(
        "/api/itinerary/generate",
        json={
            "destination": "Kyoto, Japan",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "budget": 2000,
            "currency": "USD",
            "interests": ["culture"],
            "group_size": 2
        }
    )
    print("Status Code:", response.status_code)
    print("Response:", response.json())
