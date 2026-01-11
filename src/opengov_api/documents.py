"""
Document Steps API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all document generation steps
document_steps = opengov_api.list_document_steps()
print(document_steps)

# Get a specific document generation step
document_step = opengov_api.get_document_step("document-step-12345")
print(document_step)
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_document_steps() -> dict[str, Any]:
    """
    List all document generation steps for the configured community.

    Returns:
        Dictionary containing document steps data from the API

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
        >>> document_steps = opengov_api.list_document_steps()
        >>> print(document_steps)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "document-steps")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_document_step(document_step_id: str) -> dict[str, Any]:
    """
    Get a specific document generation step by ID.

    Args:
        document_step_id: The ID of the document step to retrieve

    Returns:
        Dictionary containing document step data from the API

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
        >>> document_step = opengov_api.get_document_step("document-step-12345")
        >>> print(document_step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"document-steps/{document_step_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
