"""Cache interface for OpenGov API SDK."""

from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Abstract interface for caching HTTP responses."""

    @abstractmethod
    def get(self, key: str) -> dict[str, Any] | None:
        """
        Get cached response by key.

        Args:
            key: Cache key

        Returns:
            Cached data if available, None otherwise
        """
        pass

    @abstractmethod
    def set(
        self, key: str, data: dict[str, Any], ttl_seconds: int | None = None
    ) -> None:
        """
        Store response in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds. Use None to apply the
                cache's default TTL, or 0 to indicate no expiration.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete cached response.

        Args:
            key: Cache key
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached responses."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (implementation-specific)
        """
        return {}
