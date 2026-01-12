# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Design Principles

This codebase follows **SOLID principles** and emphasizes **DRY (Don't Repeat Yourself)**:

### DRY (Don't Repeat Yourself)
- **Never duplicate code** - Extract common patterns into reusable functions, fixtures, or utilities
- **Single source of truth** - Configuration, URLs, and test data should be centralized
- **Fixtures over repetition** - Use pytest fixtures for shared test setup and utilities
- **Parametrization** - Test similar behaviors across multiple endpoints using `@pytest.mark.parametrize`

### SOLID Principles
- **Single Responsibility** - Each function/module has one clear purpose
- **Open/Closed** - Code is open for extension, closed for modification (use parametrization to add new endpoints)
- **Liskov Substitution** - All endpoints follow consistent interfaces and behaviors
- **Interface Segregation** - Functions have minimal, focused parameters
- **Dependency Inversion** - Depend on abstractions (fixtures, decorators) not concrete implementations

### Examples in this Codebase
- ✅ **DRY URLs**: `build_url()` fixture centralizes URL construction
- ✅ **DRY Testing**: Parametrized tests verify all endpoints behave consistently
- ✅ **DRY Mocking**: `mock_url_with_params()` and `assert_request_method()` fixtures eliminate repeated patterns
- ✅ **Single Responsibility**: `base.py` handles HTTP concerns, endpoint modules handle business logic
- ✅ **Open/Closed**: Add new endpoints by extending parametrized test lists, not modifying test logic

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

### Auto-use Fixtures (Applied to All Tests)
- `block_network_calls` - Prevents accidental real API calls (uses `pytest-httpx`)
- `reset_config` - Resets module-level config between tests for isolation

### Configuration Fixtures
- `configure_client` - Sets up test API key and community (`test-api-key`, `testcommunity`)
- `test_base_url` - Returns the base URL for tests (`https://api.example.com/v2`)

### Helper Fixtures (DRY utilities)
- `build_url(path)` - Constructs full URL from path: `build_url("testcommunity/records")` → `https://api.example.com/v2/testcommunity/records`
- `mock_url_with_params(url)` - Returns regex pattern matching URL with any query params (for pagination tests)
- `assert_request_method(method)` - Asserts the last request used the expected HTTP method

### Test Organization
Tests are organized by behavior, not by module:
- `test_infrastructure.py` - Client behaviors (auth headers, config requirements, custom URLs)
- `test_common_endpoints.py` - REST patterns (list success/empty, get success/404, error handling)
- `test_*.py` for specific modules - Only endpoint-specific behaviors

### DRY Testing Patterns

**Use fixtures to eliminate repetition:**
```python
# ❌ BAD - Repeated pattern
def test_delete_record(httpx_mock, configure_client):
    url = "https://api.plce.opengov.com/plce/v2/testcommunity/records/123"
    httpx_mock.add_response(url=url, json={})
    opengov_api.delete_record("123")
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "DELETE"

# ✅ GOOD - Using fixtures
def test_delete_record(httpx_mock, configure_client, build_url, assert_request_method):
    httpx_mock.add_response(url=build_url("testcommunity/records/123"), json={})
    opengov_api.delete_record("123")
    assert_request_method("DELETE")
```

**Use parametrization for similar tests:**
```python
# ❌ BAD - Duplicated test logic
def test_list_records():
    # ... test logic ...
def test_list_users():
    # ... same logic ...

# ✅ GOOD - Parametrized
@pytest.mark.parametrize("endpoint_func,url_path", [
    (opengov_api.list_records, "testcommunity/records"),
    (opengov_api.list_users, "testcommunity/users"),
])
def test_list_endpoints(endpoint_func, url_path):
    # ... test logic once ...
```
