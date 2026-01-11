"""
Approval Steps API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all approval steps
approval_steps = opengov_api.list_approval_steps()
print(approval_steps)

# Get a specific approval step
approval_step = opengov_api.get_approval_step("approval-step-12345")
print(approval_step)

# Update an approval step
updated = opengov_api.update_approval_step("approval-step-12345", {
    "data": {
        "type": "approval-steps",
        "attributes": {
            "status": "APPROVED"
        }
    }
})
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_approval_steps() -> dict[str, Any]:
    """
    List all approval steps for the configured community.

    Returns:
        Dictionary containing approval steps data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> approval_steps = opengov_api.list_approval_steps()
        >>> print(approval_steps)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "approval-steps")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_approval_step(approval_step_id: str) -> dict[str, Any]:
    """
    Get a specific approval step by ID.

    Args:
        approval_step_id: The ID of the approval step to retrieve

    Returns:
        Dictionary containing approval step data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> approval_step = opengov_api.get_approval_step("approval-step-12345")
        >>> print(approval_step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"approval-steps/{approval_step_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_approval_step(approval_step_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update an approval step.

    Args:
        approval_step_id: The ID of the approval step to update
        data: Dictionary containing updated approval step data in JSON:API format

    Returns:
        Dictionary containing the updated approval step data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> approval_step = opengov_api.update_approval_step("approval-step-12345", {
        ...     "data": {
        ...         "type": "approval-steps",
        ...         "attributes": {"status": "APPROVED"}
        ...     }
        ... })
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"approval-steps/{approval_step_id}"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)
