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
for step in document_steps.data:
    print(f"{step.attributes.label}: {step.attributes.status}")

# Filter document steps
from opengov_api.models import DocumentStepStatus
active_steps = opengov_api.list_document_steps(
    status=DocumentStepStatus.ACTIVE,
    record_id="record-12345"
)

# Iterate through all pages automatically
for step in opengov_api.iter_document_steps(status=DocumentStepStatus.COMPLETE):
    print(f"{step.attributes.document_title}")

# Get a specific document generation step
document_step = opengov_api.get_document_step("document-step-12345")
print(document_step)
```
"""

from datetime import date, datetime
from typing import Any, Iterator


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community
from .models import (
    DateRangeFilter,
    DocumentStepResource,
    DocumentStepStatus,
    JSONAPIResponse,
    Links,
    ListDocumentStepsParams,
    Meta,
)


@handle_request_errors
def list_document_steps(
    *,
    # Filters - use keyword-only args
    record_id: str | None = None,
    label: str | None = None,
    status: DocumentStepStatus | None = None,
    completed_at: date | datetime | DateRangeFilter | None = None,
    activated_at: date | datetime | DateRangeFilter | None = None,
    # Pagination
    page_number: int = 1,
    page_size: int = 20,
    # JSON:API standard
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[DocumentStepResource]:
    """
    List document generation steps for the configured community with pagination.

    Args:
        record_id: Filter by record ID
        label: Filter by record step label
        status: Filter by document step status
        completed_at: Filter by completion date (date or DateRangeFilter)
        activated_at: Filter by activation date (date or DateRangeFilter)
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"documentStep": ["label", "status"]})
        sort: Sort order (e.g., "label", "-completedAt")

    Returns:
        JSONAPIResponse containing DocumentStepResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> from opengov_api.models import DocumentStepStatus, DateRangeFilter
        >>> from datetime import date
        >>>
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>>
        >>> # Simple filter
        >>> response = opengov_api.list_document_steps(
        ...     status=DocumentStepStatus.COMPLETE,
        ...     record_id="record-12345"
        ... )
        >>>
        >>> # Access records
        >>> for step in response.data:
        ...     print(f"{step.attributes.label}: {step.attributes.status}")
        >>>
        >>> # Check pagination
        >>> print(f"Page {response.current_page()} of {response.total_pages()}")
    """
    # Build params using ListDocumentStepsParams model
    params_model = ListDocumentStepsParams(
        filter_record_id=record_id,
        filter_label=label,
        filter_status=status,
        filter_completed_at=completed_at,
        filter_activated_at=activated_at,
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "document-steps")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        # Parse into typed response
        return JSONAPIResponse[DocumentStepResource](
            data=[DocumentStepResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def iter_document_steps(
    *,
    # Same filters as list_document_steps except page_number
    record_id: str | None = None,
    label: str | None = None,
    status: DocumentStepStatus | None = None,
    completed_at: date | datetime | DateRangeFilter | None = None,
    activated_at: date | datetime | DateRangeFilter | None = None,
    page_size: int = 100,  # Default to larger page for efficiency
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[DocumentStepResource]:
    """
    Iterate through all document steps automatically handling pagination.

    This generator function fetches all pages automatically, yielding
    individual items one at a time.

    Args:
        Same as list_document_steps, but page_number is managed automatically
        and page_size defaults to 100 for efficiency

    Yields:
        DocumentStepResource objects one at a time across all pages

    Example:
        >>> for step in opengov_api.iter_document_steps(status=DocumentStepStatus.COMPLETE):
        ...     print(f"{step.attributes.document_title}")
    """
    page = 1
    while True:
        response = list_document_steps(
            record_id=record_id,
            label=label,
            status=status,
            completed_at=completed_at,
            activated_at=activated_at,
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
