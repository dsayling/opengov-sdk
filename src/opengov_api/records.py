"""
Records API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# Create a record
record = opengov_api.create_record({
    "data": {
        "type": "records",
        "attributes": {"name": "Building Permit"}
    }
})

# Update the record
updated = opengov_api.update_record(record["data"]["id"], {
    "data": {
        "type": "records",
        "attributes": {"status": "ACTIVE"}
    }
})

# Add an applicant
opengov_api.update_record_applicant(record["data"]["id"], {
    "data": {"id": "user-123"}
})

# Add a guest
opengov_api.add_record_guest(record["data"]["id"], {
    "data": {"id": "user-456"}
})

# Create a workflow step
step = opengov_api.create_record_workflow_step(record["data"]["id"], {
    "data": {"type": "inspection-step"}
})

# Add a comment to the step
opengov_api.create_record_workflow_step_comment(
    record["data"]["id"],
    step["data"]["id"],
    {"data": {"attributes": {"text": "Inspection scheduled"}}}
)
```
"""

from datetime import date, datetime
from typing import Any, Iterator

from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community
from .models import (
    AttachmentResource,
    CollectionResource,
    DateRangeFilter,
    GuestResource,
    JSONAPIResponse,
    Links,
    ListRecordAdditionalLocationsParams,
    ListRecordAttachmentsParams,
    ListRecordCollectionsParams,
    ListRecordGuestsParams,
    ListRecordsParams,
    ListRecordWorkflowStepCommentsParams,
    ListRecordWorkflowStepsParams,
    LocationResource,
    Meta,
    RecordResource,
    RecordStatus,
    WorkflowStepCommentResource,
    WorkflowStepResource,
)


@handle_request_errors
def list_records(
    *,
    number: str | None = None,
    hist_id: str | None = None,
    hist_number: str | None = None,
    type_id: str | None = None,
    project_id: str | None = None,
    status: RecordStatus | None = None,
    created_at: date | datetime | DateRangeFilter | None = None,
    updated_at: date | datetime | DateRangeFilter | None = None,
    submitted_at: date | datetime | DateRangeFilter | None = None,
    expires_at: date | datetime | DateRangeFilter | None = None,
    is_enabled: bool | None = None,
    renewal_submitted: bool | None = None,
    submitted_online: bool | None = None,
    renewal_number: str | None = None,
    renewal_of_record_id: str | None = None,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[RecordResource]:
    """
    List records for the configured community with pagination.

    Args:
        number: Filter by record number
        hist_id: Filter by historical ID
        hist_number: Filter by historical permit number
        type_id: Filter by record type ID
        project_id: Filter by project ID
        status: Filter by status
        created_at: Filter by creation date (date or DateRangeFilter)
        updated_at: Filter by last updated date (date or DateRangeFilter)
        submitted_at: Filter by submission date (date or DateRangeFilter)
        expires_at: Filter by expiration date (date or DateRangeFilter)
        is_enabled: Filter by enabled status
        renewal_submitted: Filter by renewal submission status
        submitted_online: Filter by online submission status
        renewal_number: Filter by renewal number
        renewal_of_record_id: Filter by renewal of record ID
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"records": ["name", "status"]})
        sort: Sort order (e.g., "name", "-createdAt")

    Returns:
        JSONAPIResponse containing RecordResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> from opengov_api.models import RecordStatus, DateRangeFilter
        >>> from datetime import date
        >>>
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>>
        >>> # Simple filter
        >>> response = opengov_api.list_records(
        ...     status=RecordStatus.ACTIVE,
        ...     is_enabled=True
        ... )
        >>>
        >>> # Access records
        >>> for record in response.data:
        ...     print(f"{record.attributes.name}: {record.attributes.status}")
        >>>
        >>> # Check pagination
        >>> print(f"Page {response.current_page()} of {response.total_pages()}")
        >>> print(f"Total records: {response.total_records()}")
        >>>
        >>> # Date range filter
        >>> response = opengov_api.list_records(
        ...     created_at=DateRangeFilter(gt=date(2025, 3, 1)),
        ...     page_size=50
        ... )
        >>>
        >>> # Fetch next page
        >>> if response.has_next_page():
        ...     next_page = opengov_api.list_records(
        ...         status=RecordStatus.ACTIVE,
        ...         page_number=response.current_page() + 1
        ...     )
    """
    # Build params using ListRecordsParams model
    params_model = ListRecordsParams(
        filter_number=number,
        filter_hist_id=hist_id,
        filter_hist_number=hist_number,
        filter_type_id=type_id,
        filter_project_id=project_id,
        filter_status=status,
        filter_created_at=created_at,
        filter_updated_at=updated_at,
        filter_submitted_at=submitted_at,
        filter_expires_at=expires_at,
        filter_is_enabled=is_enabled,
        filter_renewal_submitted=renewal_submitted,
        filter_submitted_online=submitted_online,
        filter_renewal_number=renewal_number,
        filter_renewal_of_record_id=renewal_of_record_id,
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "records")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        # Parse into typed response
        return JSONAPIResponse[RecordResource](
            data=[RecordResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def iter_records(
    *,
    number: str | None = None,
    hist_id: str | None = None,
    hist_number: str | None = None,
    type_id: str | None = None,
    project_id: str | None = None,
    status: RecordStatus | None = None,
    created_at: date | datetime | DateRangeFilter | None = None,
    updated_at: date | datetime | DateRangeFilter | None = None,
    submitted_at: date | datetime | DateRangeFilter | None = None,
    expires_at: date | datetime | DateRangeFilter | None = None,
    is_enabled: bool | None = None,
    renewal_submitted: bool | None = None,
    submitted_online: bool | None = None,
    renewal_number: str | None = None,
    renewal_of_record_id: str | None = None,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[RecordResource]:
    """
    Iterate through all records automatically handling pagination.

    This generator function fetches all pages automatically, yielding
    individual records one at a time. Use this when you want to process
    all matching records without manually handling pagination.

    Args:
        Same as list_records, but page_number is managed automatically
        and page_size defaults to 100 for efficiency

    Yields:
        RecordResource objects one at a time across all pages

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> from opengov_api.models import RecordStatus
        >>>
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>>
        >>> # Iterate through all active records across all pages
        >>> for record in opengov_api.iter_records(status=RecordStatus.ACTIVE):
        ...     print(f"{record.attributes.name}: {record.attributes.number}")
        >>>
        >>> # With date range filter
        >>> from datetime import date
        >>> from opengov_api.models import DateRangeFilter
        >>>
        >>> for record in opengov_api.iter_records(
        ...     created_at=DateRangeFilter(gt=date(2025, 1, 1)),
        ...     is_enabled=True
        ... ):
        ...     process_record(record)
    """
    page = 1
    while True:
        response = list_records(
            number=number,
            hist_id=hist_id,
            hist_number=hist_number,
            type_id=type_id,
            project_id=project_id,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            submitted_at=submitted_at,
            expires_at=expires_at,
            is_enabled=is_enabled,
            renewal_submitted=renewal_submitted,
            submitted_online=submitted_online,
            renewal_number=renewal_number,
            renewal_of_record_id=renewal_of_record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        # Yield all records from this page
        if isinstance(response.data, list):
            for record in response.data:
                yield record
        else:
            yield response.data

        # Check if there's a next page
        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_guests(
    record_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[GuestResource]:
    """
    Iterate through all guests for a record, automatically handling pagination.

    Args:
        record_id: The ID of the record
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        GuestResource objects one at a time across all pages

    Example:
        >>> for guest in opengov_api.iter_record_guests("12345"):
        ...     print(f"{guest.attributes.name}")
    """
    page = 1
    while True:
        response = list_record_guests(
            record_id=record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_additional_locations(
    record_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[LocationResource]:
    """
    Iterate through all additional locations for a record, automatically handling pagination.

    Args:
        record_id: The ID of the record
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        LocationResource objects one at a time across all pages

    Example:
        >>> for location in opengov_api.iter_record_additional_locations("12345"):
        ...     print(f"{location.attributes.address}")
    """
    page = 1
    while True:
        response = list_record_additional_locations(
            record_id=record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_attachments(
    record_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[AttachmentResource]:
    """
    Iterate through all attachments for a record, automatically handling pagination.

    Args:
        record_id: The ID of the record
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        AttachmentResource objects one at a time across all pages

    Example:
        >>> for attachment in opengov_api.iter_record_attachments("12345"):
        ...     print(f"{attachment.attributes.filename}")
    """
    page = 1
    while True:
        response = list_record_attachments(
            record_id=record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_workflow_steps(
    record_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[WorkflowStepResource]:
    """
    Iterate through all workflow steps for a record, automatically handling pagination.

    Args:
        record_id: The ID of the record
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        WorkflowStepResource objects one at a time across all pages

    Example:
        >>> for step in opengov_api.iter_record_workflow_steps("12345"):
        ...     print(f"{step.attributes.name}")
    """
    page = 1
    while True:
        response = list_record_workflow_steps(
            record_id=record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_workflow_step_comments(
    record_id: str,
    step_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[WorkflowStepCommentResource]:
    """
    Iterate through all comments for a workflow step, automatically handling pagination.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        WorkflowStepCommentResource objects one at a time across all pages

    Example:
        >>> for comment in opengov_api.iter_record_workflow_step_comments("12345", "step-123"):
        ...     print(f"{comment.attributes.text}")
    """
    page = 1
    while True:
        response = list_record_workflow_step_comments(
            record_id=record_id,
            step_id=step_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def iter_record_collections(
    record_id: str,
    *,
    page_size: int = 100,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> Iterator[CollectionResource]:
    """
    Iterate through all collections for a record, automatically handling pagination.

    Args:
        record_id: The ID of the record
        page_size: Number of records per page (1-100, default 100 for efficiency)
        include: List of related resources to include
        fields: Sparse fieldsets dict
        sort: Sort order

    Yields:
        CollectionResource objects one at a time across all pages

    Example:
        >>> for collection in opengov_api.iter_record_collections("12345"):
        ...     print(f"{collection.attributes.name}")
    """
    page = 1
    while True:
        response = list_record_collections(
            record_id=record_id,
            page_number=page,
            page_size=page_size,
            include=include,
            fields=fields,
            sort=sort,
        )

        if isinstance(response.data, list):
            for item in response.data:
                yield item
        else:
            yield response.data

        if not response.has_next_page():
            break

        page += 1


@handle_request_errors
def get_record(record_id: str) -> dict[str, Any]:
    """
    Get a specific record by ID.

    Args:
        record_id: The ID of the record to retrieve

    Returns:
        Dictionary containing record data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> record = opengov_api.get_record("12345")
        >>> print(record)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_record(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new record.

    Args:
        data: Dictionary containing the record data to create

    Returns:
        Dictionary containing the created record data from the API

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
        >>> record_data = {"data": {"type": "records", "attributes": {...}}}
        >>> record = opengov_api.create_record(record_data)
        >>> print(record)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "records")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update an existing record.

    Args:
        record_id: The ID of the record to update
        data: Dictionary containing the record data to update

    Returns:
        Dictionary containing the updated record data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> record_data = {"data": {"type": "records", "attributes": {...}}}
        >>> record = opengov_api.update_record("12345", record_data)
        >>> print(record)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def archive_record(record_id: str) -> dict[str, Any]:
    """
    Archive a record.

    Args:
        record_id: The ID of the record to archive

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.archive_record("12345")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Form endpoints
@handle_request_errors
def get_record_form(record_id: str) -> dict[str, Any]:
    """
    Get form data for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing the record form data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> form = opengov_api.get_record_form("12345")
        >>> print(form)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/form")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record_form(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update form data for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the form data to update

    Returns:
        Dictionary containing the updated record form data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> form_data = {"data": {...}}
        >>> form = opengov_api.update_record_form("12345", form_data)
        >>> print(form)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/form")
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


# Record Applicant endpoints
@handle_request_errors
def get_record_applicant(record_id: str) -> dict[str, Any]:
    """
    Get the applicant for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing the applicant data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> applicant = opengov_api.get_record_applicant("12345")
        >>> print(applicant)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record_applicant(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update the applicant for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the applicant data to update

    Returns:
        Dictionary containing the updated applicant data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> applicant_data = {"data": {...}}
        >>> applicant = opengov_api.update_record_applicant("12345", applicant_data)
        >>> print(applicant)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_record_applicant(record_id: str) -> dict[str, Any]:
    """
    Remove the applicant from a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.remove_record_applicant("12345")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Guests endpoints
@handle_request_errors
def list_record_guests(
    record_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[GuestResource]:
    """
    List guests for a record with pagination.

    Args:
        record_id: The ID of the record
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"guests": ["name", "email"]})
        sort: Sort order (e.g., "name", "-createdAt")

    Returns:
        JSONAPIResponse containing GuestResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_guests("12345")
        >>> for guest in response.data:
        ...     print(f"{guest.attributes.name}: {guest.attributes.email}")
    """
    params_model = ListRecordGuestsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/guests")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[GuestResource](
            data=[GuestResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def add_record_guest(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Add a guest to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the guest data

    Returns:
        Dictionary containing the added guest data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> guest_data = {"data": {...}}
        >>> guest = opengov_api.add_record_guest("12345", guest_data)
        >>> print(guest)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/guests")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_guest(record_id: str, user_id: str) -> dict[str, Any]:
    """
    Get a specific guest on a record.

    Args:
        record_id: The ID of the record
        user_id: The ID of the guest user

    Returns:
        Dictionary containing guest data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or guest is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> guest = opengov_api.get_record_guest("12345", "user-123")
        >>> print(guest)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/guests/{user_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_record_guest(record_id: str, user_id: str) -> dict[str, Any]:
    """
    Remove a guest from a record.

    Args:
        record_id: The ID of the record
        user_id: The ID of the guest user to remove

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or guest is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.remove_record_guest("12345", "user-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/guests/{user_id}"
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Primary Location endpoints
@handle_request_errors
def get_record_primary_location(record_id: str) -> dict[str, Any]:
    """
    Get the primary location for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing the primary location data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> location = opengov_api.get_record_primary_location("12345")
        >>> print(location)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record_primary_location(
    record_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Update the primary location for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the location data to update

    Returns:
        Dictionary containing the updated primary location data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> location_data = {"data": {...}}
        >>> location = opengov_api.update_record_primary_location("12345", location_data)
        >>> print(location)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_record_primary_location(record_id: str) -> dict[str, Any]:
    """
    Remove the primary location from a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.remove_record_primary_location("12345")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Additional Locations endpoints
@handle_request_errors
def list_record_additional_locations(
    record_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[LocationResource]:
    """
    List additional locations for a record with pagination.

    Args:
        record_id: The ID of the record
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"locations": ["address", "city"]})
        sort: Sort order (e.g., "address", "-createdAt")

    Returns:
        JSONAPIResponse containing LocationResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_additional_locations("12345")
        >>> for location in response.data:
        ...     print(f"{location.attributes.address}")
    """
    params_model = ListRecordAdditionalLocationsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/additional-locations"
        )
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[LocationResource](
            data=[LocationResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def add_record_additional_location(
    record_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Add an additional location to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the location data

    Returns:
        Dictionary containing the added location data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> location_data = {"data": {...}}
        >>> location = opengov_api.add_record_additional_location("12345", location_data)
        >>> print(location)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/additional-locations"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_additional_location(record_id: str, location_id: str) -> dict[str, Any]:
    """
    Get a specific additional location on a record.

    Args:
        record_id: The ID of the record
        location_id: The ID of the location

    Returns:
        Dictionary containing location data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or location is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> location = opengov_api.get_record_additional_location("12345", "loc-123")
        >>> print(location)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/additional-locations/{location_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_record_additional_location(
    record_id: str, location_id: str
) -> dict[str, Any]:
    """
    Remove an additional location from a record.

    Args:
        record_id: The ID of the record
        location_id: The ID of the location to remove

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or location is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.remove_record_additional_location("12345", "loc-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/additional-locations/{location_id}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Attachments endpoints
@handle_request_errors
def list_record_attachments(
    record_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[AttachmentResource]:
    """
    List attachments for a record with pagination.

    Args:
        record_id: The ID of the record
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"attachments": ["filename", "size"]})
        sort: Sort order (e.g., "filename", "-createdAt")

    Returns:
        JSONAPIResponse containing AttachmentResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_attachments("12345")
        >>> for attachment in response.data:
        ...     print(f"{attachment.attributes.filename}: {attachment.attributes.size} bytes")
    """
    params_model = ListRecordAttachmentsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/attachments"
        )
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[AttachmentResource](
            data=[AttachmentResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def add_record_attachment(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Add an attachment to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the attachment data

    Returns:
        Dictionary containing the added attachment data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> attachment_data = {"data": {...}}
        >>> attachment = opengov_api.add_record_attachment("12345", attachment_data)
        >>> print(attachment)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/attachments"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_attachment(record_id: str, attachment_id: str) -> dict[str, Any]:
    """
    Get a specific attachment on a record.

    Args:
        record_id: The ID of the record
        attachment_id: The ID of the attachment

    Returns:
        Dictionary containing attachment data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or attachment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> attachment = opengov_api.get_record_attachment("12345", "att-123")
        >>> print(attachment)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/attachments/{attachment_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def remove_record_attachment(record_id: str, attachment_id: str) -> dict[str, Any]:
    """
    Remove an attachment from a record.

    Args:
        record_id: The ID of the record
        attachment_id: The ID of the attachment to remove

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or attachment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.remove_record_attachment("12345", "att-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/attachments/{attachment_id}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Change Requests endpoints
@handle_request_errors
def get_record_change_request(record_id: str, change_request_id: str) -> dict[str, Any]:
    """
    Get a change request for a record.

    Args:
        record_id: The ID of the record
        change_request_id: The ID of the change request

    Returns:
        Dictionary containing change request data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or change request is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> change_request = opengov_api.get_record_change_request("12345", "cr-123")
        >>> print(change_request)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/change-requests/{change_request_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_most_recent_record_change_request(record_id: str) -> dict[str, Any]:
    """
    Get the most recent change request for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing change request data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> change_request = opengov_api.get_most_recent_record_change_request("12345")
        >>> print(change_request)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/change-requests"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_record_change_request(
    record_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create a change request for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the change request data

    Returns:
        Dictionary containing the created change request data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> change_request_data = {"data": {...}}
        >>> change_request = opengov_api.create_record_change_request("12345", change_request_data)
        >>> print(change_request)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/change-requests"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def cancel_record_change_request(
    record_id: str, change_request_id: str
) -> dict[str, Any]:
    """
    Cancel a change request for a record.

    Args:
        record_id: The ID of the record
        change_request_id: The ID of the change request to cancel

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or change request is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.cancel_record_change_request("12345", "cr-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/change-requests/{change_request_id}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Workflow Steps endpoints
@handle_request_errors
def list_record_workflow_steps(
    record_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[WorkflowStepResource]:
    """
    List workflow steps for a record with pagination.

    Args:
        record_id: The ID of the record
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"workflow-steps": ["name", "status"]})
        sort: Sort order (e.g., "name", "-createdAt")

    Returns:
        JSONAPIResponse containing WorkflowStepResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_workflow_steps("12345")
        >>> for step in response.data:
        ...     print(f"{step.attributes.name}: {step.attributes.status}")
    """
    params_model = ListRecordWorkflowStepsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/workflow-steps"
        )
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepResource](
            data=[WorkflowStepResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def create_record_workflow_step(record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a workflow step for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the workflow step data

    Returns:
        Dictionary containing the created workflow step data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> step_data = {"data": {...}}
        >>> step = opengov_api.create_record_workflow_step("12345", step_data)
        >>> print(step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/workflow-steps"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_workflow_step(record_id: str, step_id: str) -> dict[str, Any]:
    """
    Get a specific workflow step on a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step

    Returns:
        Dictionary containing workflow step data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> step = opengov_api.get_record_workflow_step("12345", "step-123")
        >>> print(step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record_workflow_step(
    record_id: str, step_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Update a workflow step on a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        data: Dictionary containing the workflow step data to update

    Returns:
        Dictionary containing the updated workflow step data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> step_data = {"data": {...}}
        >>> step = opengov_api.update_record_workflow_step("12345", "step-123", step_data)
        >>> print(step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def delete_record_workflow_step(record_id: str, step_id: str) -> dict[str, Any]:
    """
    Delete a workflow step from a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step to delete

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.delete_record_workflow_step("12345", "step-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Workflow Step Comments endpoints
@handle_request_errors
def list_record_workflow_step_comments(
    record_id: str,
    step_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[WorkflowStepCommentResource]:
    """
    List comments for a workflow step on a record with pagination.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"comments": ["text", "createdBy"]})
        sort: Sort order (e.g., "createdAt", "-createdAt")

    Returns:
        JSONAPIResponse containing WorkflowStepCommentResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_workflow_step_comments("12345", "step-123")
        >>> for comment in response.data:
        ...     print(f"{comment.attributes.text}")
    """
    params_model = ListRecordWorkflowStepCommentsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments",
        )
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepCommentResource](
            data=[WorkflowStepCommentResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def create_record_workflow_step_comment(
    record_id: str, step_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create a comment on a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        data: Dictionary containing the comment data

    Returns:
        Dictionary containing the created comment data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> comment_data = {"data": {...}}
        >>> comment = opengov_api.create_record_workflow_step_comment("12345", "step-123", comment_data)
        >>> print(comment)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments",
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_workflow_step_comment(
    record_id: str, step_id: str, comment_id: str
) -> dict[str, Any]:
    """
    Get a specific comment on a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        comment_id: The ID of the comment

    Returns:
        Dictionary containing comment data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record, step, or comment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> comment = opengov_api.get_record_workflow_step_comment("12345", "step-123", "comment-123")
        >>> print(comment)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments/{comment_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def delete_record_workflow_step_comment(
    record_id: str, step_id: str, comment_id: str
) -> dict[str, Any]:
    """
    Delete a comment from a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        comment_id: The ID of the comment to delete

    Returns:
        Dictionary containing the response from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record, step, or comment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> result = opengov_api.delete_record_workflow_step_comment("12345", "step-123", "comment-123")
        >>> print(result)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments/{comment_id}",
        )
        response = client.delete(url)
        response.raise_for_status()
        return parse_json_response(response)


# Record Collections endpoints
@handle_request_errors
def list_record_collections(
    record_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
    include: list[str] | None = None,
    fields: dict[str, list[str]] | None = None,
    sort: str | None = None,
) -> JSONAPIResponse[CollectionResource]:
    """
    List collections for a record with pagination.

    Args:
        record_id: The ID of the record
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)
        include: List of related resources to include
        fields: Sparse fieldsets dict (e.g., {"collections": ["name", "collectionType"]})
        sort: Sort order (e.g., "name", "-createdAt")

    Returns:
        JSONAPIResponse containing CollectionResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> response = opengov_api.list_record_collections("12345")
        >>> for collection in response.data:
        ...     print(f"{collection.attributes.name}")
    """
    params_model = ListRecordCollectionsParams(
        page_number=page_number,
        page_size=page_size,
        include=include,
        fields=fields,
        sort=sort,
    )

    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/collections"
        )
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[CollectionResource](
            data=[CollectionResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_collection(record_id: str, collection_id: str) -> dict[str, Any]:
    """
    Get a specific collection on a record.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection

    Returns:
        Dictionary containing collection data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or collection is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> collection = opengov_api.get_record_collection("12345", "coll-123")
        >>> print(collection)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_record_collection_entry(
    record_id: str, collection_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create an entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        data: Dictionary containing the entry data

    Returns:
        Dictionary containing the created entry data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or collection is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> entry_data = {"data": {...}}
        >>> entry = opengov_api.create_record_collection_entry("12345", "coll-123", entry_data)
        >>> print(entry)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}",
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_collection_entry(
    record_id: str, collection_id: str, entry_id: str
) -> dict[str, Any]:
    """
    Get a specific entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        entry_id: The ID of the entry

    Returns:
        Dictionary containing entry data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record, collection, or entry is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> entry = opengov_api.get_record_collection_entry("12345", "coll-123", "entry-123")
        >>> print(entry)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}/entries/{entry_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def update_record_collection_entry(
    record_id: str, collection_id: str, entry_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Update an entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        entry_id: The ID of the entry
        data: Dictionary containing the entry data to update

    Returns:
        Dictionary containing the updated entry data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record, collection, or entry is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> entry_data = {"data": {...}}
        >>> entry = opengov_api.update_record_collection_entry("12345", "coll-123", "entry-123", entry_data)
        >>> print(entry)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}/entries/{entry_id}",
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)
