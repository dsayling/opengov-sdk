"""
Shared resource operation helpers for OpenGov API SDK.

Provides reusable CRUD operations and pagination helpers that can be used
across all resource modules (records, users, locations, projects, etc.).
"""

from typing import Any, Callable, Iterator, TypeVar

from .base import build_url, parse_json_response
from .client import _get_client, get_base_url, get_community
from .models import JSONAPIResponse, Links, Meta

# Generic type variable for resource types
T = TypeVar("T")


def get_resource(
    endpoint: str,
    resource_type: type[T],
) -> JSONAPIResponse[T]:
    """
    Get a single resource by endpoint path.

    Args:
        endpoint: The API endpoint path (e.g., "records/123" or "records/123/guests/user-1")
        resource_type: The Pydantic model class for the resource

    Returns:
        JSONAPIResponse containing the typed resource

    Example:
        >>> from opengov_api.models import RecordResource
        >>> response = get_resource("records/123", RecordResource)
        >>> print(response.data.id)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), endpoint)
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[resource_type](
            data=resource_type(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


def create_resource(
    endpoint: str,
    resource_type: type[T],
    json_data: dict[str, Any],
) -> JSONAPIResponse[T]:
    """
    Create a new resource via POST request.

    Args:
        endpoint: The API endpoint path (e.g., "records" or "records/123/guests")
        resource_type: The Pydantic model class for the resource
        json_data: The request body data

    Returns:
        JSONAPIResponse containing the created typed resource

    Example:
        >>> from opengov_api.models import RecordResource
        >>> data = {"data": {"type": "records", "attributes": {"name": "Test"}}}
        >>> response = create_resource("records", RecordResource, data)
        >>> print(response.data.id)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), endpoint)
        response = client.post(url, json=json_data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[resource_type](
            data=resource_type(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


def update_resource(
    endpoint: str,
    resource_type: type[T],
    json_data: dict[str, Any],
) -> JSONAPIResponse[T]:
    """
    Update an existing resource via PATCH request.

    Args:
        endpoint: The API endpoint path (e.g., "records/123" or "records/123/guests/user-1")
        resource_type: The Pydantic model class for the resource
        json_data: The request body data

    Returns:
        JSONAPIResponse containing the updated typed resource

    Example:
        >>> from opengov_api.models import RecordResource
        >>> data = {"data": {"type": "records", "attributes": {"status": "ACTIVE"}}}
        >>> response = update_resource("records/123", RecordResource, data)
        >>> print(response.data.attributes.status)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), endpoint)
        response = client.patch(url, json=json_data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[resource_type](
            data=resource_type(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


def delete_resource(endpoint: str) -> None:
    """
    Delete a resource via DELETE request.

    Args:
        endpoint: The API endpoint path (e.g., "records/123" or "records/123/guests/user-1")

    Returns:
        None

    Example:
        >>> delete_resource("records/123/guests/user-1")
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), endpoint)
        response = client.delete(url)
        response.raise_for_status()


def list_resources(
    endpoint: str,
    resource_type: type[T],
    params: dict[str, Any] | None = None,
) -> JSONAPIResponse[list[T]]:
    """
    List resources with optional query parameters.

    Args:
        endpoint: The API endpoint path (e.g., "records" or "records/123/guests")
        resource_type: The Pydantic model class for the resource
        params: Optional query parameters for filtering, pagination, etc.

    Returns:
        JSONAPIResponse containing a list of typed resources

    Example:
        >>> from opengov_api.models import RecordResource
        >>> response = list_resources("records", RecordResource, {"page[size]": 10})
        >>> for record in response.data:
        ...     print(record.id)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), endpoint)
        response = client.get(url, params=params or {})
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[list[resource_type]](
            data=[resource_type(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


def iter_paginated(
    list_func: Callable[..., JSONAPIResponse[list[T]]],
    **kwargs: Any,
) -> Iterator[T]:
    """
    Iterate through all pages of a paginated list endpoint.

    Automatically handles pagination by calling the list function repeatedly
    until all pages are retrieved. Yields individual resources one at a time.

    Args:
        list_func: The list function to call (e.g., list_records, list_record_guests)
        **kwargs: Arguments to pass to the list function (filters, etc.)
                 Note: page_number and page_size are handled automatically

    Yields:
        Individual resource items

    Example:
        >>> from opengov_api import list_records
        >>> from opengov_api.models import RecordStatus
        >>> for record in iter_paginated(list_records, status=RecordStatus.ACTIVE):
        ...     print(record.attributes.name)
    """
    page = 1
    page_size = kwargs.pop("page_size", 100)

    while True:
        response = list_func(page_number=page, page_size=page_size, **kwargs)

        # Handle both single resources and lists
        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        # Check if there are more pages
        if not response.has_next_page():
            break

        page += 1


def build_nested_url(*parts: str) -> str:
    """
    Build a nested resource URL from parts.

    Args:
        *parts: URL path segments (e.g., "records", "123", "guests", "user-1")

    Returns:
        Joined URL path string

    Example:
        >>> url = build_nested_url("records", "123", "guests", "user-1")
        >>> print(url)  # "records/123/guests/user-1"
    """
    return "/".join(str(part) for part in parts)
