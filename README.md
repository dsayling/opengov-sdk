# OpenGov API SDK

A Python SDK for interacting with OpenGov APIs using a functional factory pattern.

## Features

- 🔧 **Simple configuration** - Set API key and community once, use everywhere
- 🛡️ **Type-safe** - Full type hints for better IDE support
- 🎯 **Error handling** - Custom exceptions for different error scenarios
- 🚀 **HTTP caching** - Optional response caching for improved performance
- ✅ **Well-tested** - Comprehensive test suite with mocked HTTP calls
- 📦 **Modular** - Easy to extend with new API endpoints

## Installation

This package is not yet published to PyPI. To install it locally, clone the repository and run:

```bash
pip install -e .
```

or use `uv` if you have it installed:

```bash
uv sync
```

## Quick Start

```python
import opengov_api

# Configure the SDK
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all records
records = opengov_api.list_records()
print(f"Found {len(records['records'])} records")

# Get a specific record
record = opengov_api.get_record("12345")
print(f"Record: {record['name']}")

# List all users
users = opengov_api.list_users()
print(f"Found {len(users['users'])} users")
```

## Configuration

### Environment Variables

The SDK automatically reads configuration from environment variables:

```bash
export OPENGOV_API_KEY="your-api-key"
export OPENGOV_COMMUNITY="your-community"
```

### Programmatic Configuration

You can also configure the SDK programmatically:

```python
import opengov_api

# Required settings
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# Optional settings
opengov_api.set_base_url("https://api.plce.opengov.com/plce/v2")
opengov_api.set_timeout(60.0)  # Default: 30.0 seconds
```

## HTTP Response Caching

The SDK includes optional HTTP response caching to improve performance and reduce API calls.

### Enable Caching

```python
import opengov_api

# Configure API
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# Enable file-based caching
opengov_api.enable_file_cache()

# Now GET requests through resource helpers are automatically cached
records = opengov_api.list_records()  # Fetches from API
records = opengov_api.list_records()  # Returns from cache
```

### Configuration Options

```python
opengov_api.enable_file_cache(
    cache_dir=".opengov_cache",  # Cache directory
    default_ttl_hours=24,         # Cache lifetime in hours
    max_cache_size_mb=100        # Maximum cache size
)
```

### Cache Management

```python
# Get cache statistics
stats = opengov_api.get_cache_stats()
print(f"Cached entries: {stats['total_entries']}")
print(f"Cache size: {stats['total_size_mb']} MB")

# Clear cache
opengov_api.clear_cache()

# Disable caching
opengov_api.disable_cache()
```

### Key Features

- **Automatic**: GET requests through resource helpers cached automatically when enabled
- **HTTP-aware**: Respects `Cache-Control` headers from API
- **Isolated**: Separate caches per community/account
- **Thread-safe**: Safe for concurrent access
- **Smart eviction**: Cleans up oldest cache files first (based on modification time) when size limit is exceeded

See [examples/caching_usage.py](examples/caching_usage.py) for usage examples.

## Troubleshooting

### "API key not set" error

Make sure to set your API key before making requests:

```python
opengov_api.set_api_key("your-api-key")
# or set environment variable
# export OPENGOV_API_KEY="your-api-key"
```

### "Community not set" error

Make sure to set your community before making requests:

```python
opengov_api.set_community("your-community")
# or set environment variable
# export OPENGOV_COMMUNITY="your-community"
```

### Connection timeouts

Increase the timeout if you're experiencing timeout errors:

```python
opengov_api.set_timeout(60.0)  # 60 seconds
```

### Rate limiting

The API may return 429 errors if you exceed rate limits. Implement exponential backoff:

```python
import time
from opengov_api import OpenGovRateLimitError

for attempt in range(3):
    try:
        records = opengov_api.list_records()
        break
    except OpenGovRateLimitError:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
        else:
            raise
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

```bash
# Run tests
uv run pytest

# Run type checking
uv run pyright

# Format code
uv run ruff format
uv run ruff check --fix
```
