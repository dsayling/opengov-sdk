"""
Users API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all users
users = opengov_api.list_users()
print(users)

# Get a specific user
user = opengov_api.get_user("user-12345")
print(user)

# Create a new user
new_user = opengov_api.create_user({
    "data": {
        "type": "user",
        "attributes": {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@example.com",
            "phoneNo": "555-0123",
            "address": "123 Main St",
            "city": "Springfield",
            "state": "CA",
            "zip": "90210"
        }
    }
})

# List user flags for a specific user
flags = opengov_api.list_user_flags("user-12345")
print(flags)
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_users() -> dict[str, Any]:
    """
    List all users for the configured community.

    Returns:
        Dictionary containing users data from the API

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
        >>> users = opengov_api.list_users()
        >>> print(users)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "users")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_user(user_id: str) -> dict[str, Any]:
    """
    Get a specific user by ID.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        Dictionary containing user data from the API

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
        >>> user = opengov_api.get_user("user-12345")
        >>> print(user)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"users/{user_id}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_user(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new user.

    Args:
        data: Dictionary containing user data following JSON:API format

    Returns:
        Dictionary containing the created user data from the API

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
        >>> new_user = opengov_api.create_user({
        ...     "data": {
        ...         "type": "user",
        ...         "attributes": {
        ...             "firstName": "John",
        ...             "lastName": "Doe",
        ...             "email": "john.doe@example.com"
        ...         }
        ...     }
        ... })
        >>> print(new_user)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "users")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def list_user_flags(user_id: str) -> dict[str, Any]:
    """
    List all flags for a specific user.

    Args:
        user_id: The ID of the user to retrieve flags for

    Returns:
        Dictionary containing user flags data from the API

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
        >>> flags = opengov_api.list_user_flags("user-12345")
        >>> print(flags)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"users/{user_id}/flags")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
