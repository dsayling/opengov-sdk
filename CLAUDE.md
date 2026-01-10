# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=opengov_api --cov-report=html

# Run a single test file
uv run pytest tests/test_records.py

# Run a specific test
uv run pytest tests/test_records.py::TestRecords::test_list_records_success -v

# Type checking
uv run pyright

# Format code
uv run ruff format
uv run ruff check --fix

# Lint code
uv run ruff check
uv run ruff format --check
```

## Architecture

This is a Python SDK for OpenGov APIs using a **functional factory pattern** (inspired by OpenAI Agents SDK):

- **Module-level configuration** (`client.py`): Global state for API key, community, base URL, and timeout. Set once via `set_*()` functions, accessed anywhere via `get_*()` functions.
- **Client factory** (`_get_client()`): Creates fresh `httpx.Client` instances with auth headers. Always used as context manager: `with _get_client() as client:`
- **Shared utilities** (`base.py`):
  - `build_url()` - Constructs API URLs from base URL, community, and endpoint
  - `handle_request_errors` - Decorator that wraps httpx exceptions into custom exceptions
  - `parse_json_response()` - Parses responses with error handling
  - `make_status_error()` - Maps HTTP status codes to specific exception types

## Adding New Endpoints

1. Create endpoint module (e.g., `src/opengov_api/permits.py`):
```python
from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community

@handle_request_errors
def list_permits() -> dict[str, Any]:
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "permits")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
```

2. Export in `__init__.py`

3. Add to parametrized tests (see `adding_new_endpoint_example.md`):
   - Add to `test_infrastructure.py` endpoint lists
   - Add to `test_common_endpoints.py` parametrized fixtures

## Test Structure

Tests use `pytest-httpx` for mocking HTTP calls. Key fixtures in `conftest.py`:
- `reset_config` (autouse) - Resets module-level config between tests
- `configure_client` - Sets up test API key and community

Tests are organized by behavior, not by module:
- `test_infrastructure.py` - Client behaviors (auth headers, config requirements, custom URLs)
- `test_common_endpoints.py` - REST patterns (list success/empty, get success/404, error handling)
- `test_*.py` for specific modules - Only endpoint-specific behaviors
