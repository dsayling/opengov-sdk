"""
HTTP Response Caching Examples

Demonstrates how to use the caching features in the OpenGov API SDK.
"""

import opengov_api
from opengov_api.models import RecordStatus

# Configure API connection
opengov_api.set_api_key("your-api-key-here")
opengov_api.set_community("your-community")


def basic_caching_example():
    """Basic caching with default settings."""
    print("\n=== Basic Caching Example ===")

    # Enable file-based caching with defaults
    opengov_api.enable_file_cache()

    # First request - cache miss (hits API)
    print("Fetching records (cache miss)...")
    records1 = opengov_api.list_records(status=RecordStatus.ACTIVE, page_size=5)
    assert isinstance(records1.data, list)
    print(f"Retrieved {len(records1.data)} records")

    # Second identical request - cache hit (no API call)
    print("\nFetching same records (cache hit)...")
    records2 = opengov_api.list_records(status=RecordStatus.ACTIVE, page_size=5)
    assert isinstance(records2.data, list)
    print(f"Retrieved {len(records2.data)} records from cache")

    # Check cache statistics
    stats = opengov_api.get_cache_stats()
    print("\nCache statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Cache size: {stats['total_size_mb']:.2f} MB")
    print(f"  Cache directory: {stats['cache_dir']}")

    # Clean up
    opengov_api.disable_cache()


def custom_configuration_example():
    """Caching with custom configuration."""
    print("\n=== Custom Configuration Example ===")

    # Enable caching with custom settings
    opengov_api.enable_file_cache(
        cache_dir=".my_api_cache",  # Custom cache directory
        default_ttl_hours=12,  # Cache for 12 hours
        max_cache_size_mb=50,  # Limit cache to 50 MB
    )

    print("Cache enabled with:")
    print("  - Cache directory: .my_api_cache")
    print("  - TTL: 12 hours")
    print("  - Max size: 50 MB")

    # Make some requests
    records = opengov_api.list_records(page_size=10)
    assert isinstance(records.data, list)
    print(f"\nCached {len(records.data)} records")

    stats = opengov_api.get_cache_stats()
    print(f"Cache size: {stats['total_size_mb']:.4f} MB")

    # Clean up
    opengov_api.disable_cache()


def cache_management_example():
    """Managing cache lifecycle."""
    print("\n=== Cache Management Example ===")

    opengov_api.enable_file_cache()

    # Populate cache
    print("Populating cache...")
    opengov_api.list_records(page_size=5)
    opengov_api.list_users()

    stats = opengov_api.get_cache_stats()
    print(f"Cache entries: {stats['total_entries']}")

    # Clear cache
    print("\nClearing cache...")
    opengov_api.clear_cache()

    stats = opengov_api.get_cache_stats()
    print(f"Cache entries after clear: {stats['total_entries']}")

    # Disable caching
    print("\nDisabling cache...")
    opengov_api.disable_cache()

    cache = opengov_api.get_cache()
    if cache is None:
        print("Cache is now disabled")


def cache_isolation_example():
    """Demonstrate cache isolation between communities."""
    print("\n=== Cache Isolation Example ===")

    opengov_api.enable_file_cache()

    # Cache data for first community
    print(f"Fetching records for community: {opengov_api.get_community()}")
    records1 = opengov_api.list_records(page_size=5)
    assert isinstance(records1.data, list)
    print(f"Cached {len(records1.data)} records")

    stats1 = opengov_api.get_cache_stats()
    print(f"Cache entries: {stats1['total_entries']}")

    # Switch community and fetch again
    original_community = opengov_api.get_community()
    opengov_api.set_community("different-community")
    print(f"\nSwitched to community: {opengov_api.get_community()}")

    try:
        # This creates a separate cache entry due to different community
        records2 = opengov_api.list_records(page_size=5)
        assert isinstance(records2.data, list)
        print(f"Cached {len(records2.data)} records for new community")

        stats2 = opengov_api.get_cache_stats()
        print(f"Cache entries: {stats2['total_entries']} (increased due to isolation)")
    except Exception as e:
        print(f"Note: {e}")

    # Restore original community
    opengov_api.set_community(original_community)

    # Clean up
    opengov_api.disable_cache()


def monitoring_cache_example():
    """Monitor cache performance and health."""
    print("\n=== Cache Monitoring Example ===")

    opengov_api.enable_file_cache(max_cache_size_mb=10)

    # Make several different requests
    print("Making various API calls...")
    opengov_api.list_records(page_size=10)
    opengov_api.list_records(page_size=20)  # Different params = new cache entry
    opengov_api.list_users()

    # Get detailed statistics
    stats = opengov_api.get_cache_stats()
    print("\nCache Statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Total size: {stats['total_size_mb']:.4f} MB")
    print(f"  Max size: {stats['max_size_mb']} MB")
    print(f"  Usage: {stats['total_size_mb'] / stats['max_size_mb'] * 100:.1f}%")
    print(f"  Expired entries: {stats['expired_entries']}")

    # Simulate cache health check
    if stats["total_size_mb"] > stats["max_size_mb"] * 0.8:
        print("\n⚠️  Cache is >80% full - consider clearing or increasing size")
    else:
        print("\n✅  Cache size is healthy")

    # Clean up
    opengov_api.disable_cache()


def custom_cache_implementation_example():
    """Example of using a custom cache implementation."""
    print("\n=== Custom Cache Implementation Example ===")

    from opengov_api.cache import CacheInterface

    # Example: In-memory cache (for demonstration)
    class SimpleMemoryCache(CacheInterface):
        """Simple in-memory cache implementation."""

        def __init__(self):
            self.storage = {}
            print("Initialized SimpleMemoryCache")

        def get(self, key):
            return self.storage.get(key)

        def set(self, key, data, ttl_seconds=None):
            # Simplified: ignore TTL for this example
            self.storage[key] = data
            print(f"Cached item (total: {len(self.storage)})")

        def delete(self, key):
            self.storage.pop(key, None)

        def clear(self):
            count = len(self.storage)
            self.storage.clear()
            print(f"Cleared {count} cache entries")

        def get_stats(self):
            return {
                "total_entries": len(self.storage),
                "type": "memory",
            }

    # Use custom cache
    custom_cache = SimpleMemoryCache()
    opengov_api.set_cache(custom_cache)

    # Make requests
    print("\nMaking API calls with custom cache...")
    opengov_api.list_records(page_size=5)
    opengov_api.list_users()

    # Check stats
    stats = opengov_api.get_cache_stats()
    print(f"\nCustom cache statistics: {stats}")

    # Clean up
    opengov_api.set_cache(None)
    print("Custom cache disabled")


def conditional_caching_example():
    """Example of enabling/disabling cache conditionally."""
    print("\n=== Conditional Caching Example ===")

    # Enable caching for read operations
    print("Phase 1: Reading data (cache enabled)")
    opengov_api.enable_file_cache()

    records = opengov_api.list_records(page_size=5)
    assert isinstance(records.data, list)
    print(f"Fetched {len(records.data)} records (cached)")

    # Disable for write operations to ensure fresh data
    print("\nPhase 2: Writing data (cache disabled)")
    opengov_api.disable_cache()

    # Simulate creating records (write operation - never cached anyway)
    print("Creating new record...")
    # opengov_api.create_record({...})  # Not cached

    # Re-enable cache and clear to get fresh data
    print("\nPhase 3: Reading updated data (cache cleared and re-enabled)")
    opengov_api.enable_file_cache()
    opengov_api.clear_cache()  # Clear to get fresh data

    records_updated = opengov_api.list_records(page_size=5)
    assert isinstance(records_updated.data, list)
    print(f"Fetched {len(records_updated.data)} records (fresh)")

    # Clean up
    opengov_api.disable_cache()


if __name__ == "__main__":
    """Run all examples."""
    print("OpenGov API SDK - Caching Examples")
    print("=" * 50)

    try:
        # Run examples
        basic_caching_example()
        custom_configuration_example()
        cache_management_example()
        monitoring_cache_example()
        conditional_caching_example()

        # Optional examples (may fail if data not available)
        try:
            cache_isolation_example()
        except Exception as e:
            print(f"\nSkipped isolation example: {e}")

        try:
            custom_cache_implementation_example()
        except Exception as e:
            print(f"\nSkipped custom cache example: {e}")

        print("\n" + "=" * 50)
        print("✅  All examples completed!")

    except opengov_api.OpenGovConfigurationError:
        print("\n⚠️  Please configure your API key and community first:")
        print("  export OPENGOV_API_KEY='your-key'")
        print("  export OPENGOV_COMMUNITY='your-community'")
    except Exception as e:
        print(f"\n❌  Error: {e}")
