"""File-based cache implementation for OpenGov API SDK."""

import hashlib
import json
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .interface import CacheInterface
from .models import CacheEntry

_log = logging.getLogger(__name__)


class FileCache(CacheInterface):
    """File-based cache for storing HTTP responses."""

    def __init__(
        self,
        cache_dir: Path | str = ".opengov_cache",
        default_ttl_hours: int = 24,
        max_cache_size_mb: int = 100,
    ):
        """
        Initialize file cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live in hours (0 = never expires)
            max_cache_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl_hours = default_ttl_hours
        self.max_cache_size_mb = max_cache_size_mb
        self._lock = threading.Lock()

        _log.debug(
            f"Initialized FileCache at {self.cache_dir} "
            f"(TTL: {default_ttl_hours}h, Max: {max_cache_size_mb}MB)"
        )

    def _get_cache_file(self, key: str) -> Path:
        """
        Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """
        Get cached response by key.

        Args:
            key: Cache key

        Returns:
            Cached data if available and not expired, None otherwise
        """
        with self._lock:
            cache_file = self._get_cache_file(key)

            if not cache_file.exists():
                _log.debug(f"Cache miss: {key}")
                return None

            try:
                with open(cache_file) as f:
                    entry_data = json.load(f)
                    entry = CacheEntry(**entry_data)

                # Check if expired
                if entry.is_expired():
                    _log.debug(
                        f"Cache expired: {key} (age: {entry.age_hours():.1f}h, "
                        f"TTL: {entry.ttl_seconds}s)"
                    )
                    self._delete_unlocked(key)
                    return None

                _log.debug(f"Cache hit: {key} (age: {entry.age_hours():.1f}h)")
                return entry.data

            except Exception as e:
                _log.warning(f"Failed to read cache for {key}: {e}")
                return None

    def set(
        self, key: str, data: dict[str, Any], ttl_seconds: int | None = None
    ) -> None:
        """
        Store response in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds (None uses default_ttl_hours)
        """
        with self._lock:
            # Use TTL in seconds, converting from hours if needed
            if ttl_seconds is not None:
                ttl_sec = ttl_seconds
            else:
                ttl_sec = self.default_ttl_hours * 3600

            cache_file = self._get_cache_file(key)

            try:
                entry = CacheEntry(
                    key=key,
                    data=data,
                    cached_at=datetime.now().isoformat(),
                    ttl_seconds=ttl_sec,
                    size_bytes=0,
                )

                # Write to cache
                entry_json = entry.model_dump_json(indent=2)
                cache_file.write_text(entry_json)

                # Update size
                entry.size_bytes = cache_file.stat().st_size

                _log.debug(f"Cached: {key} ({entry.size_bytes} bytes, TTL: {ttl_sec}s)")

                # Check cache size and cleanup if needed
                self._enforce_size_limit()

            except Exception as e:
                _log.warning(f"Failed to cache {key}: {e}")

    def delete(self, key: str) -> None:
        """
        Delete cached response.

        Args:
            key: Cache key
        """
        with self._lock:
            self._delete_unlocked(key)

    def _delete_unlocked(self, key: str) -> None:
        """Delete cached response without acquiring lock (internal use)."""
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()
            _log.debug(f"Deleted cache: {key}")

    def clear(self) -> None:
        """Clear all cached responses."""
        with self._lock:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                _log.info(f"Cleared cache directory: {self.cache_dir}")

    def _enforce_size_limit(self) -> None:
        """Check cache size and cleanup old entries if needed (must be called with lock)."""
        total_size = sum(
            f.stat().st_size for f in self.cache_dir.glob("*.json") if f.is_file()
        )
        total_size_mb = total_size / (1024 * 1024)

        if total_size_mb > self.max_cache_size_mb:
            _log.warning(
                f"Cache size ({total_size_mb:.1f}MB) exceeds limit "
                f"({self.max_cache_size_mb}MB), cleaning up..."
            )
            self._cleanup_old_entries()

    def _cleanup_old_entries(self) -> None:
        """Remove oldest cache entries until under size limit (must be called with lock)."""
        cache_files = list(self.cache_dir.glob("*.json"))

        # Sort by modification time (oldest first)
        cache_files.sort(key=lambda f: f.stat().st_mtime)

        removed_count = 0
        for cache_file in cache_files:
            # Check current size
            total_size = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.json") if f.is_file()
            )
            total_size_mb = total_size / (1024 * 1024)

            if total_size_mb <= self.max_cache_size_mb * 0.8:  # 80% threshold
                break

            cache_file.unlink()
            removed_count += 1

        _log.info(f"Removed {removed_count} old cache entries")

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (count, size, etc.)
        """
        with self._lock:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
            total_size_mb = total_size / (1024 * 1024)

            expired_count = 0
            for cache_file in cache_files:
                try:
                    with open(cache_file) as f:
                        entry_data = json.load(f)
                        entry = CacheEntry(**entry_data)
                        if entry.is_expired():
                            expired_count += 1
                except Exception:
                    pass

            return {
                "total_entries": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size_mb, 4),
                "expired_entries": expired_count,
                "cache_dir": str(self.cache_dir),
                "max_size_mb": self.max_cache_size_mb,
            }
