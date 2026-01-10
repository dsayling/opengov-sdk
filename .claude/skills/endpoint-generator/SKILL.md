---
name: endpoint-generator
description: Generate SDK endpoint modules from OpenAPI specifications for the opengov_api SDK. Use when adding new API endpoints based on OpenAPI/Swagger specs, or when the user provides an OpenAPI specification and wants SDK methods generated. Handles creating endpoint modules, updating exports, and adding parametrized tests.
---

# OpenAPI Endpoint Generator

Generate SDK endpoint modules from OpenAPI specifications following the functional factory pattern.

## Workflow

1. Parse the OpenAPI spec (user provides JSON/YAML or file path)
2. For each endpoint path, generate the appropriate SDK functions
3. Update `src/opengov_api/__init__.py` exports
4. Add to parametrized test fixtures

## Endpoint Module Pattern

Create `src/opengov_api/{resource}.py` with a comprehensive module docstring that includes usage examples:

```python
"""
{Resource} API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List resources
resources = opengov_api.list_{resource}()
print(resources)

# Get a specific resource
resource = opengov_api.get_{resource}("resource-id")
print(resource)

# Create a new resource
new_resource = opengov_api.create_{resource}({
    "data": {
        "type": "{resource}",
        "attributes": {...}
    }
})

# Update a resource
updated = opengov_api.update_{resource}("resource-id", {
    "data": {
        "type": "{resource}",
        "attributes": {...}
    }
})
```
"""

from typing import Any

from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_{resource}() -> dict[str, Any]:
    """List all {resource} for the configured community."""
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "{resource}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_{singular}({singular}_id: str) -> dict[str, Any]:
    """Get a specific {singular} by ID."""
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"{resource}/{{{singular}_id}}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
```

**Note:** Include relevant examples for the specific resource in the module docstring. Show common workflows and typical use cases for that resource type.

## Update Exports

In `src/opengov_api/__init__.py`:

1. Add import: `from .{resource} import list_{resource}, get_{singular}`
2. Add to `__all__` list under appropriate comment section

## Update Parametrized Tests

### test_infrastructure.py

Add to `TestInfrastructure` parametrized lists:

```python
# In test_requires_api_key and test_requires_community:
@pytest.mark.parametrize("endpoint_func", [
    opengov_api.list_records,
    opengov_api.list_users,
    opengov_api.list_{resource},  # ADD
])

# In test_sends_auth_header and test_handles_invalid_json:
@pytest.mark.parametrize("endpoint_func,url_pattern", [
    (opengov_api.list_{resource}, "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}"),  # ADD
])

# In test_custom_base_url:
@pytest.mark.parametrize("endpoint_func,custom_url", [
    (opengov_api.list_{resource}, "https://custom.api.com/v3/testcommunity/{resource}"),  # ADD
])
```

For get endpoints, add to `TestGetEndpointInfrastructure`:

```python
# In test_get_requires_api_key and test_get_requires_community:
@pytest.mark.parametrize("endpoint_func,resource_id", [
    (opengov_api.get_{singular}, "12345"),  # ADD
])

# In test_get_sends_auth_header:
@pytest.mark.parametrize("endpoint_func,resource_id,url", [
    (opengov_api.get_{singular}, "12345", "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/12345"),  # ADD
])

# In test_get_custom_base_url:
@pytest.mark.parametrize("endpoint_func,resource_id,custom_url", [
    (opengov_api.get_{singular}, "12345", "https://custom.api.com/v3/testcommunity/{resource}/12345"),  # ADD
])
```

### test_common_endpoints.py

Add to `TestListEndpoints`:

```python
@pytest.mark.parametrize("endpoint_func,url,response_key", [
    (opengov_api.list_{resource}, "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}", "{resource}"),  # ADD
])
```

Add to `TestGetEndpoints`:

```python
@pytest.mark.parametrize("endpoint_func,url_template,resource_id", [
    (opengov_api.get_{singular}, "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/{{}}", "12345"),  # ADD
])
```

## OpenAPI Mapping Rules

| OpenAPI | SDK |
|---------|-----|
| `GET /resource` | `list_{resource}()` |
| `GET /resource/{id}` | `get_{singular}({singular}_id: str)` |
| `POST /resource` | `create_{singular}(data: dict)` |
| `PUT /resource/{id}` | `update_{singular}({singular}_id: str, data: dict)` |
| `PATCH /resource/{id}` | `patch_{singular}({singular}_id: str, data: dict)` |
| `DELETE /resource/{id}` | `delete_{singular}({singular}_id: str)` |

For POST/PUT/PATCH, use `client.post(url, json=data)` etc.

## Verification

After generating, run:
```bash
uv run pytest
uv run pyright
uv run ruff check
```

Check the coverage report to ensure new endpoints are covered 100%.

## Important Notes

- **DO NOT** create separate summary or documentation files (e.g., `RECORDS_API_SUMMARY.md`)
- **DO** include comprehensive usage examples in the module-level docstring
- Module docstrings should demonstrate real-world workflows for the resource
- Keep examples practical and show common operations for that specific API resource
