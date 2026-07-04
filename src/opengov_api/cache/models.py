"""Cache models for OpenGov API SDK."""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel


class CacheEntry(BaseModel):
    """Single cache entry with metadata."""

    key: str
    data: dict[str, Any]
    cached_at: str
    ttl_seconds: int
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds == 0:
            return False  # Never expires

        cached_time = datetime.fromisoformat(self.cached_at)
        expiry_time = cached_time + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time

    def age_hours(self) -> float:
        """Get age of cache entry in hours."""
        cached_time = datetime.fromisoformat(self.cached_at)
        age = datetime.now() - cached_time
        return age.total_seconds() / 3600
