"""
Locations API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all locations
locations = opengov_api.list_locations()
print(locations)

# Get a specific location
location = opengov_api.get_location("location-12345")
print(location)

# Create a new location
new_location = opengov_api.create_location({
    "data": {
        "type": "locations",
        "attributes": {
            "address": "123 Main St",
            "city": "Springfield",
            "state": "CA",
            "zipCode": "90210"
        }
    }
})

# Update a location
updated = opengov_api.update_location("location-12345", {
    "data": {
        "type": "locations",
        "attributes": {
            "address": "456 Oak Ave"
        }
    }
})

# Delete a location
opengov_api.delete_location("location-12345")

# List location flags for a specific location
flags = opengov_api.list_location_flags("location-12345")
print(flags)
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_locations() -> dict[str, Any]:
    """
    List all locations for the configured community.

    Returns:
        Dictionary containing locations data from the API

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
        >>> locations = opengov_api.list_locations()
        >>> print(locations)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "locations")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_location(location_id: str) -> dict[str, Any]:
    """
    Get a specific location by ID.

    Args:
        location_id: The ID of the location to retrieve

    Returns:
        Dictionary containing location data from the API

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
        >>> location = opengov_api.get_location("location-12345")
        >>> print(location)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"locations/{location_id}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_location(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new location.

    Args:
        data: Dictionary containing location data in JSON:API format

    Returns:
        Dictionary containing the created location data from the API

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
        >>> location = opengov_api.create_location({
        ...     "data": {
        ...         "type": "locations",
        ...         "attributes": {
        ...             "address": "123 Main St",
        ...             "city": "Springfield"
        ...         }
        ...     }
        ... })
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "locations")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_location(location_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update a location.

    Args:
        location_id: The ID of the location to update
        data: Dictionary containing updated location data in JSON:API format

    Returns:
        Dictionary containing the updated location data from the API

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
        >>> location = opengov_api.update_location("location-12345", {
        ...     "data": {
        ...         "type": "locations",
        ...         "attributes": {"address": "456 Oak Ave"}
        ...     }
        ... })
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"locations/{location_id}")
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def delete_location(location_id: str) -> None:
    """
    Delete a location.

    Args:
        location_id: The ID of the location to delete

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.delete_location("location-12345")
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"locations/{location_id}")
        response = client.delete(url)
        response.raise_for_status()


@handle_request_errors
def list_location_flags(location_id: str) -> dict[str, Any]:
    """
    List all flags for a specific location.

    Args:
        location_id: The ID of the location

    Returns:
        Dictionary containing location flags data from the API

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
        >>> flags = opengov_api.list_location_flags("location-12345")
        >>> print(flags)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"locations/{location_id}/flags"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
