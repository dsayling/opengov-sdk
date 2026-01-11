"""
Projects API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all projects
projects = opengov_api.list_projects()
print(projects)

# Get a specific project
project = opengov_api.get_project("project-12345")
print(project)

# Projects group related records together
# You can use projects to manage collections of permits,
# licenses, or other records that are part of the same
# development or initiative
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_projects() -> dict[str, Any]:
    """
    List all projects for the configured community.

    Projects allow you to group related records together for management
    and tracking purposes.

    Returns:
        Dictionary containing projects data from the API

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
        >>> projects = opengov_api.list_projects()
        >>> print(projects)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "projects")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_project(project_id: str) -> dict[str, Any]:
    """
    Get a specific project by ID.

    Args:
        project_id: The ID of the project to retrieve

    Returns:
        Dictionary containing project data from the API

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
        >>> project = opengov_api.get_project("project-12345")
        >>> print(project)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"projects/{project_id}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
