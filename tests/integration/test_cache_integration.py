"""Integration tests for HTTP caching with API endpoints."""

import pytest
import opengov_api


@pytest.fixture
def cache_setup(tmp_path):
    """Set up and tear down file cache for tests."""
    cache_dir = str(tmp_path / "test_cache")
    opengov_api.enable_file_cache(cache_dir=cache_dir, default_ttl_hours=1)
    yield
    opengov_api.disable_cache()


class TestCacheIntegrationWithMockServer:
    """Integration tests with mock server."""

    def test_list_records_caching(self, mock_server, cache_setup):
        """Test that list_records responses are cached."""
        # First request - cache miss
        response1 = opengov_api.list_records(page_size=5)
        assert isinstance(response1.data, list)
        assert len(response1.data) > 0

        # Check cache stats
        stats = opengov_api.get_cache_stats()
        assert stats["total_entries"] >= 1

        # Second request - should be cached
        response2 = opengov_api.list_records(page_size=5)
        assert isinstance(response2.data, list)
        assert len(response2.data) == len(response1.data)

        # Stats should show cache hit efficiency
        stats2 = opengov_api.get_cache_stats()
        assert stats2["total_entries"] >= 1

    def test_get_record_caching(self, mock_server, cache_setup):
        """Test that get_record responses are cached."""
        # Get a record ID first
        records = opengov_api.list_records(page_size=1)
        if not records.data:
            pytest.skip("No records available")

        assert isinstance(records.data, list)
        record_id = records.data[0].id

        # First request - cache miss
        record1 = opengov_api.get_record(record_id)
        assert not isinstance(record1.data, list)
        assert record1.data.id == record_id

        # Second request - should be cached
        record2 = opengov_api.get_record(record_id)
        assert not isinstance(record2.data, list)
        assert record2.data.id == record1.data.id

        # Verify cache has entries
        stats = opengov_api.get_cache_stats()
        assert stats["total_entries"] >= 1

    def test_post_not_cached(self, mock_server, cache_setup):
        """Test that POST requests are not cached."""
        initial_stats = opengov_api.get_cache_stats()
        initial_count = initial_stats.get("total_entries", 0)

        # Create a record (POST request)
        try:
            _ = opengov_api.create_record(
                {"data": {"type": "records", "attributes": {"name": "Test Record"}}}
            )
        except Exception:
            # POST might not be supported in mock server
            pytest.skip("Create record not supported")

        # Cache should not have grown from POST
        stats = opengov_api.get_cache_stats()
        # Should either be same or only increased from the GET after create
        assert stats["total_entries"] - initial_count <= 1

    def test_cache_isolation_by_community(self, mock_server, tmp_path):
        """Test that different communities have separate cache entries."""
        cache_dir = str(tmp_path / "isolation_cache")
        opengov_api.enable_file_cache(cache_dir=cache_dir)

        # Get original community
        original_community = opengov_api.get_community()

        # Request with first community
        _ = opengov_api.list_records(page_size=5)
        stats1 = opengov_api.get_cache_stats()

        # Switch community and make same request
        opengov_api.set_community("different-community")
        try:
            _ = opengov_api.list_records(page_size=5)
        except Exception:
            # Different community might not exist
            opengov_api.set_community(original_community)
            pytest.skip("Different community not accessible")

        # Should have separate cache entries
        stats2 = opengov_api.get_cache_stats()
        assert stats2["total_entries"] > stats1["total_entries"]

        # Restore original community
        opengov_api.set_community(original_community)
        opengov_api.disable_cache()

    def test_clear_cache(self, mock_server, cache_setup):
        """Test clearing the cache."""
        # Make some requests to populate cache
        opengov_api.list_records(page_size=5)

        stats_before = opengov_api.get_cache_stats()
        assert stats_before["total_entries"] > 0

        # Clear cache
        opengov_api.clear_cache()

        stats_after = opengov_api.get_cache_stats()
        assert stats_after["total_entries"] == 0

    def test_cache_respects_different_params(self, mock_server, cache_setup):
        """Test that different query params result in separate cache entries."""
        # Request with different page sizes
        _ = opengov_api.list_records(page_size=5)
        stats1 = opengov_api.get_cache_stats()

        _ = opengov_api.list_records(page_size=10)
        stats2 = opengov_api.get_cache_stats()

        # Should have separate cache entries for different params
        assert stats2["total_entries"] > stats1["total_entries"]

    def test_disabled_cache_no_caching(self, mock_server):
        """Test that with caching disabled, no cache entries are created."""
        opengov_api.disable_cache()

        # Make requests
        opengov_api.list_records(page_size=5)

        # No cache stats available
        stats = opengov_api.get_cache_stats()
        assert stats == {}


class TestCacheWithoutMockServer:
    """Tests that don't require mock server."""

    def test_cache_configuration_persistence(self, tmp_path):
        """Test that cache configuration persists across function calls."""
        cache_dir = str(tmp_path / "persist_cache")

        opengov_api.enable_file_cache(
            cache_dir=cache_dir, default_ttl_hours=12, max_cache_size_mb=50
        )

        cache = opengov_api.get_cache()
        assert cache is not None

        # Configuration should persist
        stats = opengov_api.get_cache_stats()
        assert stats["cache_dir"] == cache_dir
        assert stats["max_size_mb"] == 50

        opengov_api.disable_cache()

    def test_custom_cache_implementation(self):
        """Test using a custom cache implementation."""
        from opengov_api.cache import CacheInterface

        class MockCache(CacheInterface):
            def __init__(self):
                self.storage = {}

            def get(self, key):
                return self.storage.get(key)

            def set(self, key, data, ttl_seconds=None):
                self.storage[key] = data

            def delete(self, key):
                self.storage.pop(key, None)

            def clear(self):
                self.storage.clear()

        custom_cache = MockCache()
        opengov_api.set_cache(custom_cache)

        assert opengov_api.get_cache() is custom_cache

        # Manually test cache
        custom_cache.set("test", {"data": "value"})
        assert custom_cache.get("test") == {"data": "value"}

        opengov_api.set_cache(None)
