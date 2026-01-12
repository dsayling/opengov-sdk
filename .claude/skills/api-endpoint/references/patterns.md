# SDK Code Patterns

Complete code examples for implementing OpenGov API SDK endpoints.

## Table of Contents

1. [Endpoint Module Structure](#endpoint-module-structure)
2. [List Endpoint with Typed Response](#list-endpoint-with-typed-response)
3. [Iterator Function](#iterator-function)
4. [Simple CRUD Endpoints](#simple-crud-endpoints)
5. [Nested Resource Endpoints](#nested-resource-endpoints)
6. [Model Definitions](#model-definitions)
7. [Params Model](#params-model)
8. [Enum Definitions](#enum-definitions)
9. [Test Patterns](#test-patterns)
10. [Export Patterns](#export-patterns)

---

## Endpoint Module Structure

Every endpoint module follows this structure:

```python
"""
{Resource} API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List {resource}
items = opengov_api.list_{resource}()
print(items)
```
"""

from datetime import date, datetime
from typing import Any, Iterator

from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community
from .models import (
    DateRangeFilter,
    JSONAPIResponse,
    Links,
    Meta,
    List{Resource}Params,
    {Resource}Resource,
    {Resource}Status,  # if enum exists
)


# Endpoint functions follow...
```

---

## List Endpoint with Typed Response

The most complete pattern - used for primary list endpoints:

```python
@handle_request_errors
def list_{resource}(
    *,
    # Filters - use keyword-only args
    number: str | None = None,
    status: {Resource}Status | None = None,
    created_at: date | datetime | DateRangeFilter | None = None,
    updated_at: date | datetime | DateRangeFilter | None = None,
    is_enabled: bool | None = None,
    # Pagination
    page_number: int = 1,
    page_size: int = 20,
    # JSON:API standard
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[{Resource}Resource]:
    """
    List {resource} for the configured community with pagination.

    Args:
        number: Filter by {resource} number
        status: Filter by status
        created_at: Filter by creation date (date or DateRangeFilter)
        updated_at: Filter by last updated date (date or DateRangeFilter)
        is_enabled: Filter by enabled status
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {{"{resource}": ["name", "status"]}})
        sort: Sort order (e.g., "name", "-createdAt")

    Returns:
        JSONAPIResponse containing {Resource}Resource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> from opengov_api.models import {Resource}Status, DateRangeFilter
        >>> from datetime import date
        >>>
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>>
        >>> # Simple filter
        >>> response = opengov_api.list_{resource}(
        ...     status={Resource}Status.ACTIVE,
        ...     is_enabled=True
        ... )
        >>>
        >>> # Access records
        >>> for item in response.data:
        ...     print(f"{{item.attributes.name}}: {{item.attributes.status}}")
        >>>
        >>> # Check pagination
        >>> print(f"Page {{response.current_page()}} of {{response.total_pages()}}")
    """
    # Build params using List{Resource}Params model
    params_model = List{Resource}Params(
        filter_number=number,
        filter_status=status,
        filter_created_at=created_at,
        filter_updated_at=updated_at,
        filter_is_enabled=is_enabled,
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "{resource}")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        # Parse into typed response
        return JSONAPIResponse[{Resource}Resource](
            data=[{Resource}Resource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )
```

---

## Iterator Function

Auto-pagination iterator for list endpoints:

```python
@handle_request_errors
def iter_{resource}(
    *,
    # Same filters as list_{resource} except page_number
    number: str | None = None,
    status: {Resource}Status | None = None,
    created_at: date | datetime | DateRangeFilter | None = None,
    updated_at: date | datetime | DateRangeFilter | None = None,
    is_enabled: bool | None = None,
    page_size: int = 100,  # Default to larger page for efficiency
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[{Resource}Resource]:
    """
    Iterate through all {resource} automatically handling pagination.

    This generator function fetches all pages automatically, yielding
    individual items one at a time.

    Args:
        Same as list_{resource}, but page_number is managed automatically
        and page_size defaults to 100 for efficiency

    Yields:
        {Resource}Resource objects one at a time across all pages

    Example:
        >>> for item in opengov_api.iter_{resource}(status={Resource}Status.ACTIVE):
        ...     print(f"{{item.attributes.name}}")
    """
    page = 1
    while True:
        response = list_{resource}(
            number=number,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            is_enabled=is_enabled,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        # Yield all items from this page
        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        # Check if there's a next page
        if not response.has_next_page():
            break

        page += 1
```

---

## Simple CRUD Endpoints

For endpoints that return untyped dict responses:

```python
@handle_request_errors
def get_{resource}({resource}_id: str) -> dict[str, Any]:
    """
    Get a specific {resource} by ID.

    Args:
        {resource}_id: The ID of the {resource} to retrieve

    Returns:
        Dictionary containing {resource} data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If {resource} is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> item = opengov_api.get_{resource}("12345")
        >>> print(item)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"{resource}/{{{resource}_id}}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_{resource}(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new {resource}.

    Args:
        data: Dictionary containing the {resource} data to create

    Returns:
        Dictionary containing the created {resource} data from the API
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "{resource}")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_{resource}({resource}_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update an existing {resource}.

    Args:
        {resource}_id: The ID of the {resource} to update
        data: Dictionary containing the {resource} data to update

    Returns:
        Dictionary containing the updated {resource} data from the API
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"{resource}/{{{resource}_id}}")
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def delete_{resource}({resource}_id: str) -> dict[str, Any]:
    """
    Delete a {resource}.

    Args:
        {resource}_id: The ID of the {resource} to delete

    Returns:
        Dictionary containing the response from the API
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"{resource}/{{{resource}_id}}")
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)
```

---

## Nested Resource Endpoints

For child resources under a parent:

```python
@handle_request_errors
def list_{parent}_{child}({parent}_id: str) -> dict[str, Any]:
    """
    List {child} for a {parent}.

    Args:
        {parent}_id: The ID of the {parent}

    Returns:
        Dictionary containing {child} data from the API
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"{parent}/{{{parent}_id}}/{child}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def add_{parent}_{child}({parent}_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Add a {child} to a {parent}.

    Args:
        {parent}_id: The ID of the {parent}
        data: Dictionary containing the {child} data

    Returns:
        Dictionary containing the added {child} data from the API
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"{parent}/{{{parent}_id}}/{child}"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_{parent}_{child}({parent}_id: str, {child}_id: str) -> dict[str, Any]:
    """
    Get a specific {child} on a {parent}.

    Args:
        {parent}_id: The ID of the {parent}
        {child}_id: The ID of the {child}

    Returns:
        Dictionary containing {child} data from the API
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"{parent}/{{{parent}_id}}/{child}/{{{child}_id}}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_{parent}_{child}({parent}_id: str, {child}_id: str) -> dict[str, Any]:
    """
    Remove a {child} from a {parent}.

    Args:
        {parent}_id: The ID of the {parent}
        {child}_id: The ID of the {child} to remove

    Returns:
        Dictionary containing the response from the API
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"{parent}/{{{parent}_id}}/{child}/{{{child}_id}}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)
```

---

## Model Definitions

### Resource Attributes Model

Create in `src/opengov_api/models/{resource}.py`:

```python
"""{Resource} models for OpenGov API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .enums import {Resource}Status


class {Resource}Attributes(BaseModel):
    """{Resource} attributes."""

    name: str | None = None
    number: str | None = None
    status: {Resource}Status | None = None
    description: str | None = None
    # Use Field(alias=...) for camelCase JSON keys
    hist_id: str | None = Field(None, alias="histID")
    is_enabled: bool | None = Field(None, alias="isEnabled")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class {Resource}Resource(BaseModel):
    """{Resource} resource object."""

    id: str
    type: str
    attributes: {Resource}Attributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


class {Resource}CreateAttributes(BaseModel):
    """Attributes for creating a {resource}."""

    name: str
    description: str | None = None


class {Resource}CreateData(BaseModel):
    """Data wrapper for creating a {resource}."""

    type: str = "{resource}"
    attributes: {Resource}CreateAttributes
    relationships: dict[str, Any] | None = None


class {Resource}CreateRequest(BaseModel):
    """Request body for creating a {resource}."""

    data: {Resource}CreateData


class {Resource}UpdateAttributes(BaseModel):
    """Attributes for updating a {resource}."""

    name: str | None = None
    description: str | None = None
    status: {Resource}Status | None = None


class {Resource}UpdateData(BaseModel):
    """Data wrapper for updating a {resource}."""

    type: str = "{resource}"
    attributes: {Resource}UpdateAttributes


class {Resource}UpdateRequest(BaseModel):
    """Request body for updating a {resource}."""

    data: {Resource}UpdateData
```

---

## Params Model

Add to `src/opengov_api/models/params.py`:

```python
class List{Resource}Params(BaseModel):
    """
    Query parameters for listing {resource}.

    Example:
        >>> from opengov_api.models import List{Resource}Params, {Resource}Status
        >>> params = List{Resource}Params(
        ...     filter_status={Resource}Status.ACTIVE,
        ...     filter_is_enabled=True
        ... )
    """

    # Filters
    filter_number: str | None = None
    filter_status: {Resource}Status | None = None
    filter_created_at: date | datetime | DateRangeFilter | None = None
    filter_updated_at: date | datetime | DateRangeFilter | None = None
    filter_is_enabled: bool | None = None

    # Pagination
    page_number: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    # JSON:API standard params
    include: list[str] | None = None
    fields: dict[str, list[str]] | None = None
    sort: str | None = None

    def to_query_params(self) -> dict[str, Any]:
        """
        Convert to query parameter dict with proper JSON:API bracket notation.

        Returns:
            Dictionary suitable for httpx params argument
        """
        params: dict[str, Any] = {}

        # Simple filters
        if self.filter_number:
            params["filter[number]"] = self.filter_number
        if self.filter_status:
            params["filter[status]"] = self.filter_status.value
        if self.filter_is_enabled is not None:
            params["filter[isEnabled]"] = self.filter_is_enabled

        # Date filters (can be simple date or range)
        for field_name, param_value in [
            ("createdAt", self.filter_created_at),
            ("updatedAt", self.filter_updated_at),
        ]:
            if param_value:
                if isinstance(param_value, DateRangeFilter):
                    params.update(param_value.to_query_params(field_name))
                else:
                    # Simple date/datetime
                    params[f"filter[{field_name}]"] = (
                        param_value.isoformat()
                        if isinstance(param_value, (date, datetime))
                        else param_value
                    )

        # Pagination
        params["page[number]"] = self.page_number
        params["page[size]"] = self.page_size

        # JSON:API standard params
        if self.include:
            params["include"] = ",".join(self.include)
        if self.fields:
            for resource_type, field_list in self.fields.items():
                params[f"fields[{resource_type}]"] = ",".join(field_list)
        if self.sort:
            params["sort"] = self.sort

        return params
```

---

## Enum Definitions

Add to `src/opengov_api/models/enums.py`:

```python
from enum import Enum


class {Resource}Status(str, Enum):
    """Status values for {resource}."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
```

---

## Test Patterns

### Resource-Specific Tests

Create `tests/test_{resource}.py`:

```python
"""
Tests for {resource}-specific endpoint behaviors.

Infrastructure and common endpoint tests are in test_infrastructure.py
and test_common_endpoints.py. This file tests behaviors unique to the
{resource} resource.
"""

from pytest_httpx import HTTPXMock

import opengov_api


class Test{Resource}CRUD:
    """Tests for basic {resource} CRUD operations."""

    def test_create_{resource}(self, httpx_mock: HTTPXMock, configure_client):
        """Test creating a {resource}."""
        url = "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}"
        data = {{"data": {{"type": "{resource}", "attributes": {{"name": "Test"}}}}}}
        httpx_mock.add_response(url=url, json={{"data": {{"id": "123"}}}})

        result = opengov_api.create_{resource}(data)
        assert result["data"]["id"] == "123"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"

    def test_update_{resource}(self, httpx_mock: HTTPXMock, configure_client):
        """Test updating a {resource}."""
        url = "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/123"
        data = {{"data": {{"type": "{resource}", "attributes": {{"name": "Updated"}}}}}}
        httpx_mock.add_response(url=url, json={{"data": {{"id": "123"}}}})

        result = opengov_api.update_{resource}("123", data)
        assert result["data"]["id"] == "123"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PATCH"

    def test_delete_{resource}(self, httpx_mock: HTTPXMock, configure_client):
        """Test deleting a {resource}."""
        url = "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/123"
        httpx_mock.add_response(url=url, json={{}})

        opengov_api.delete_{resource}("123")

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class Test{Resource}EdgeCases:
    """Tests for edge cases and special behaviors."""

    def test_get_{resource}_with_special_characters(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test get_{resource} handles special characters in IDs."""
        {resource}_id = "{resource}-123-abc"
        httpx_mock.add_response(
            url=f"https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/{{{resource}_id}}",
            json={{"id": {resource}_id, "name": "Special"}},
        )

        result = opengov_api.get_{resource}({resource}_id)
        assert result["id"] == {resource}_id
```

### Add to test_common_endpoints.py

Add entries to the parametrized lists:

```python
# In TestListEndpoints.test_list_success and test_list_empty:
(
    opengov_api.list_{resource},
    "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}",
    "{resource}",
),

# In TestGetEndpoints.test_get_success and test_get_not_found:
(
    opengov_api.get_{resource},
    "https://api.plce.opengov.com/plce/v2/testcommunity/{resource}/{{}}",
    "12345",
),
```

---

## Export Patterns

### Module Exports (`src/opengov_api/__init__.py`)

```python
# Add to imports
from .{resource} import (
    list_{resource},
    iter_{resource},
    get_{resource},
    create_{resource},
    update_{resource},
    delete_{resource},
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    # {Resource}
    "list_{resource}",
    "iter_{resource}",
    "get_{resource}",
    "create_{resource}",
    "update_{resource}",
    "delete_{resource}",
]
```

### Model Exports (`src/opengov_api/models/__init__.py`)

```python
# Add to imports
from .{resource} import (
    {Resource}Attributes,
    {Resource}CreateAttributes,
    {Resource}CreateData,
    {Resource}CreateRequest,
    {Resource}Resource,
    {Resource}UpdateAttributes,
    {Resource}UpdateData,
    {Resource}UpdateRequest,
)
from .params import List{Resource}Params
from .enums import {Resource}Status

# Add to __all__
__all__ = [
    # ... existing exports ...
    # {Resource}
    "{Resource}Attributes",
    "{Resource}CreateAttributes",
    "{Resource}CreateData",
    "{Resource}CreateRequest",
    "{Resource}Resource",
    "{Resource}UpdateAttributes",
    "{Resource}UpdateData",
    "{Resource}UpdateRequest",
    "List{Resource}Params",
    "{Resource}Status",
]
```
