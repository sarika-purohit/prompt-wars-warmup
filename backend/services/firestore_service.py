"""Firestore service for persisting itineraries."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from google.cloud import firestore

from models.user_input import Itinerary

logger = logging.getLogger(__name__)


class FirestoreService:
    """CRUD operations for itineraries stored in Cloud Firestore."""

    COLLECTION = "itineraries"
    CACHE_COLLECTION = "itinerary_cache"

    def __init__(self) -> None:
        self._db = firestore.AsyncClient()

    async def save_itinerary(self, itinerary: Itinerary) -> str:
        """Save an itinerary and return its ID."""
        if not itinerary.id:
            itinerary.id = uuid.uuid4().hex[:12]

        doc_ref = self._db.collection(self.COLLECTION).document(itinerary.id)
        await doc_ref.set(itinerary.model_dump())
        logger.info("Saved itinerary %s", itinerary.id)
        return itinerary.id

    async def get_itinerary(self, itinerary_id: str) -> Itinerary | None:
        """Retrieve an itinerary by ID."""
        doc_ref = self._db.collection(self.COLLECTION).document(itinerary_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return None
        return Itinerary(**doc.to_dict())

    async def delete_itinerary(self, itinerary_id: str) -> bool:
        """Delete an itinerary. Returns True if it existed."""
        doc_ref = self._db.collection(self.COLLECTION).document(itinerary_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return False
        await doc_ref.delete()
        logger.info("Deleted itinerary %s", itinerary_id)
        return True

    async def list_itineraries(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent itineraries (metadata only)."""
        query = (
            self._db.collection(self.COLLECTION)
            .order_by("start_date", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            results.append({
                "id": doc.id,
                "destination": data.get("destination"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "total_cost": data.get("total_cost"),
                "budget": data.get("budget"),
            })
        return results

    async def get_cached_itinerary(self, cache_key: str) -> Itinerary | None:
        """Retrieve an itinerary from the cache."""
        doc_ref = self._db.collection(self.CACHE_COLLECTION).document(cache_key)
        doc = await doc_ref.get()
        if not doc.exists:
            return None
        logger.info(f"Cache HIT for {cache_key}")
        return Itinerary(**doc.to_dict())

    async def save_cached_itinerary(self, cache_key: str, itinerary: Itinerary) -> None:
        """Save an itinerary to the cache."""
        doc_ref = self._db.collection(self.CACHE_COLLECTION).document(cache_key)
        await doc_ref.set(itinerary.model_dump())
        logger.info(f"Cache SET for {cache_key}")
