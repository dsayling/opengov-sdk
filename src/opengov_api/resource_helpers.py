"""
Shared resource operation helpers for OpenGov API SDK.

Provides reusable CRUD operations and pagination helpers that can be used
across all resource modules (records, users, locations, projects, etc.).
"""

import hashlib
import json
from typing import Any, Callable, Generator, TypeVar, cast

import httpx

from .base import build_url, parse_json_response
from .cache import HTTPCacheHelper
from .client import _get_client, get_api_key, get_base_url, get_cache, get_community
from .models import JSONAPIResponse, Links, Meta

# Generic type variable for resource types
T = TypeVar("T")


def _generate_cache_key(method: str, url: str, params: dict[str, Any] | None) -> str:
    """
    Generate a cache key from request parameters.

    Includes method, URL, params, community, and API key hash to ensure
    cache isolation between different requests and accounts.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        params: Query parameters

    Returns:
        SHA256 hash of the request signature
    """
    # Sort params for consistent keys
    params_str = json.dumps(params or {}, sort_keys=True)

    # Include community and API key hash for isolation
    community = get_community()
    api_key_hash = hashlib.sha256(get_api_key().encode()).hexdigest()[:8]

    # Create composite key
    key_parts = f"{method}:{url}:{params_str}:{community}:{api_key_hash}"

    # Hash for safe, fixed-length key
    return hashlib.sha256(key_parts.encode()).hexdigest()


def _make_cached_request(
    client: httpx.Client,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    """
    Make an HTTP request with optional caching.

    Only GET requests are cached. Cache respects HTTP Cache-Control headers.

    Args:
        client: httpx.Client instance
        method: HTTP method
        url: Request URL
        **kwargs: Additional arguments for httpx request (params, json, etc.)

    Returns:
        httpx.Response object
    """
    cache = get_cache()

    # Skip cache for non-GET requests or if caching is disabled
    if cache is None or method.upper() != "GET":
        return client.request(method, url, **kwargs)

    # Generate cache key
    params = kwargs.get("params")
    cache_key = _generate_cache_key(method, url, params)

    # Check cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        # Reconstruct response from cached data
        return httpx.Response(
            status_code=cached_data["status_code"],
            headers=cached_data["headers"],
            content=cached_data["content"],
            request=httpx.Request(method, url),
        )

    # Make actual request
    response = client.request(method, url, **kwargs)

    # Cache successful responses if cacheable
    if HTTPCacheHelper.is_cacheable(response):
        # Extract TTL from response headers
        ttl_seconds = HTTPCacheHelper.get_cache_ttl(response)

        # Cache response data
        cache.set(
            cache_key,
            {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
            },
            ttl_seconds=ttl_seconds,
        )

    return response


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
        response = _make_cached_request(client, "GET", url)
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
) -> JSONAPIResponse[T]:
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
        response = _make_cached_request(client, "GET", url, params=params or {})
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[resource_type](
            data=[resource_type(**item) for item in data["data"]],  # type: ignore[arg-type]
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


def iter_paginated(
    list_func: Callable[..., JSONAPIResponse[T]],
    **kwargs: Any,
) -> Generator[T, None, None]:
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

        # list_func returns JSONAPIResponse[T], so data is T | list[T]
        # For list endpoints, data is always list[T], cast to help type checker
        data = cast(list[T], response.data)
        for item in data:
            yield item

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
