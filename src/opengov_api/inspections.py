"""
Inspection Steps API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all inspection steps
inspection_steps = opengov_api.list_inspection_steps()
print(inspection_steps)

# Get a specific inspection step
inspection_step = opengov_api.get_inspection_step("inspection-step-12345")
print(inspection_step)

# Update an inspection step
updated = opengov_api.update_inspection_step("inspection-step-12345", {
    "data": {
        "type": "inspection-steps",
        "attributes": {
            "status": "COMPLETED"
        }
    }
})

# List inspection types for a step
inspection_types = opengov_api.list_inspection_types("inspection-step-12345")
print(inspection_types)

# Add an inspection type to a step
new_type = opengov_api.create_inspection_type("inspection-step-12345", {
    "data": {
        "type": "inspection-types",
        "attributes": {
            "name": "Foundation Inspection"
        }
    }
})
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_inspection_steps() -> dict[str, Any]:
    """
    List all inspection steps for the configured community.

    Returns:
        Dictionary containing inspection steps data from the API

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
        >>> inspection_steps = opengov_api.list_inspection_steps()
        >>> print(inspection_steps)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "inspection-steps")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_inspection_step(inspection_step_id: str) -> dict[str, Any]:
    """
    Get a specific inspection step by ID.

    Args:
        inspection_step_id: The ID of the inspection step to retrieve

    Returns:
        Dictionary containing inspection step data from the API

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
        >>> inspection_step = opengov_api.get_inspection_step("inspection-step-12345")
        >>> print(inspection_step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"inspection-steps/{inspection_step_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_inspection_step(
    inspection_step_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Update an inspection step.

    Args:
        inspection_step_id: The ID of the inspection step to update
        data: Dictionary containing updated inspection step data in JSON:API format

    Returns:
        Dictionary containing the updated inspection step data from the API

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
        >>> inspection_step = opengov_api.update_inspection_step("inspection-step-12345", {
        ...     "data": {
        ...         "type": "inspection-steps",
        ...         "attributes": {"status": "COMPLETED"}
        ...     }
        ... })
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"inspection-steps/{inspection_step_id}"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def list_inspection_types(inspection_step_id: str) -> dict[str, Any]:
    """
    List all inspection types for a specific inspection step.

    Args:
        inspection_step_id: The ID of the inspection step

    Returns:
        Dictionary containing inspection types data from the API

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
        >>> types = opengov_api.list_inspection_types("inspection-step-12345")
        >>> print(types)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"inspection-steps/{inspection_step_id}/inspection-types",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_inspection_type(
    inspection_step_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Add an inspection type to an inspection step.

    Args:
        inspection_step_id: The ID of the inspection step
        data: Dictionary containing inspection type data in JSON:API format

    Returns:
        Dictionary containing the created inspection type data from the API

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
        >>> inspection_type = opengov_api.create_inspection_type("inspection-step-12345", {
        ...     "data": {
        ...         "type": "inspection-types",
        ...         "attributes": {"name": "Foundation Inspection"}
        ...     }
        ... })
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"inspection-steps/{inspection_step_id}/inspection-types",
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)
