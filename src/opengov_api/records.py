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
    ApplicantResource,
    AttachmentResource,
    ChangeRequestResource,
    CollectionEntryResource,
    CollectionResource,
    DateRangeFilter,
    FormResource,
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
def get_record(record_id: str) -> JSONAPIResponse[RecordResource]:
    """
    Get a specific record by ID.

    Args:
        record_id: The ID of the record to retrieve

    Returns:
        JSONAPIResponse containing a single RecordResource

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
        >>> response = opengov_api.get_record("12345")
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[RecordResource](
            data=RecordResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def create_record(data: dict[str, Any]) -> JSONAPIResponse[RecordResource]:
    """
    Create a new record.

    Args:
        data: Dictionary containing the record data to create

    Returns:
        JSONAPIResponse containing the created RecordResource

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
        >>> response = opengov_api.create_record(record_data)
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "records")
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[RecordResource](
            data=RecordResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def update_record(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[RecordResource]:
    """
    Update an existing record.

    Args:
        record_id: The ID of the record to update
        data: Dictionary containing the record data to update

    Returns:
        JSONAPIResponse containing the updated RecordResource

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
        >>> response = opengov_api.update_record("12345", record_data)
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[RecordResource](
            data=RecordResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def archive_record(record_id: str) -> None:
    """
    Archive a record.

    Args:
        record_id: The ID of the record to archive

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.archive_record("12345")
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}")
        response = client.delete(url)
        response.raise_for_status()


# Record Form endpoints
@handle_request_errors
def get_record_form(record_id: str) -> FormResource:
    """
    Get form data for a record.

    Args:
        record_id: The ID of the record

    Returns:
        FormResource containing the record form data

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
        >>> print(form.fields)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/form")
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        # Forms use non-standard format: {"data": {"fields": [...]}}
        return FormResource(**data["data"])


@handle_request_errors
def update_record_form(record_id: str, data: dict[str, Any]) -> FormResource:
    """
    Update form data for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the form data to update

    Returns:
        FormResource containing the updated record form data

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
        >>> print(form.fields)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/form")
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        # Forms use non-standard format: {"data": {"fields": [...]}}
        return FormResource(**data["data"])


# Record Applicant endpoints
@handle_request_errors
def get_record_applicant(record_id: str) -> JSONAPIResponse[ApplicantResource]:
    """
    Get the applicant for a record.

    Args:
        record_id: The ID of the record

    Returns:
        JSONAPIResponse containing the applicant data

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
        >>> print(applicant.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[ApplicantResource](
            data=ApplicantResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def update_record_applicant(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[ApplicantResource]:
    """
    Update the applicant for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the applicant data to update

    Returns:
        JSONAPIResponse containing the updated applicant data

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
        >>> print(applicant.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[ApplicantResource](
            data=ApplicantResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def remove_record_applicant(record_id: str) -> None:
    """
    Remove the applicant from a record.

    Args:
        record_id: The ID of the record

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.remove_record_applicant("12345")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/applicant"
        )
        response = client.delete(url)
        response.raise_for_status()


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
def add_record_guest(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[GuestResource]:
    """
    Add a guest to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the guest data

    Returns:
        JSONAPIResponse containing the added GuestResource

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
        >>> response = opengov_api.add_record_guest("12345", guest_data)
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/guests")
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[GuestResource](
            data=GuestResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_guest(record_id: str, user_id: str) -> JSONAPIResponse[GuestResource]:
    """
    Get a specific guest on a record.

    Args:
        record_id: The ID of the record
        user_id: The ID of the guest user

    Returns:
        JSONAPIResponse containing the GuestResource

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
        >>> response = opengov_api.get_record_guest("12345", "user-123")
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/guests/{user_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[GuestResource](
            data=GuestResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def remove_record_guest(record_id: str, user_id: str) -> None:
    """
    Remove a guest from a record.

    Args:
        record_id: The ID of the record
        user_id: The ID of the guest user to remove

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or guest is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.remove_record_guest("12345", "user-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/guests/{user_id}"
        )
        response = client.delete(url)
        response.raise_for_status()


# Record Primary Location endpoints
@handle_request_errors
def get_record_primary_location(record_id: str) -> JSONAPIResponse[LocationResource]:
    """
    Get the primary location for a record.

    Args:
        record_id: The ID of the record

    Returns:
        JSONAPIResponse containing the LocationResource

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
        >>> response = opengov_api.get_record_primary_location("12345")
        >>> print(response.data.attributes.address)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[LocationResource](
            data=LocationResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def update_record_primary_location(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[LocationResource]:
    """
    Update the primary location for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the location data to update

    Returns:
        JSONAPIResponse containing the updated LocationResource

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
        >>> response = opengov_api.update_record_primary_location("12345", location_data)
        >>> print(response.data.attributes.address)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[LocationResource](
            data=LocationResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def remove_record_primary_location(record_id: str) -> None:
    """
    Remove the primary location from a record.

    Args:
        record_id: The ID of the record

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.remove_record_primary_location("12345")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/primary-location"
        )
        response = client.delete(url)
        response.raise_for_status()


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
) -> JSONAPIResponse[LocationResource]:
    """
    Add an additional location to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the location data

    Returns:
        JSONAPIResponse containing the added LocationResource

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
        >>> response = opengov_api.add_record_additional_location("12345", location_data)
        >>> print(response.data.attributes.address)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/additional-locations"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[LocationResource](
            data=LocationResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_additional_location(
    record_id: str, location_id: str
) -> JSONAPIResponse[LocationResource]:
    """
    Get a specific additional location on a record.

    Args:
        record_id: The ID of the record
        location_id: The ID of the location

    Returns:
        JSONAPIResponse containing the LocationResource

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
        >>> response = opengov_api.get_record_additional_location("12345", "loc-123")
        >>> print(response.data.attributes.address)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/additional-locations/{location_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[LocationResource](
            data=LocationResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def remove_record_additional_location(record_id: str, location_id: str) -> None:
    """
    Remove an additional location from a record.

    Args:
        record_id: The ID of the record
        location_id: The ID of the location to remove

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or location is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.remove_record_additional_location("12345", "loc-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/additional-locations/{location_id}",
        )
        response = client.delete(url)
        response.raise_for_status()


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
def add_record_attachment(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[AttachmentResource]:
    """
    Add an attachment to a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the attachment data

    Returns:
        JSONAPIResponse containing the added AttachmentResource

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
        >>> response = opengov_api.add_record_attachment("12345", attachment_data)
        >>> print(response.data.attributes.filename)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/attachments"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[AttachmentResource](
            data=AttachmentResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_attachment(
    record_id: str, attachment_id: str
) -> JSONAPIResponse[AttachmentResource]:
    """
    Get a specific attachment on a record.

    Args:
        record_id: The ID of the record
        attachment_id: The ID of the attachment

    Returns:
        JSONAPIResponse containing the AttachmentResource

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
        >>> response = opengov_api.get_record_attachment("12345", "att-123")
        >>> print(response.data.attributes.filename)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/attachments/{attachment_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[AttachmentResource](
            data=AttachmentResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def remove_record_attachment(record_id: str, attachment_id: str) -> None:
    """
    Remove an attachment from a record.

    Args:
        record_id: The ID of the record
        attachment_id: The ID of the attachment to remove

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or attachment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.remove_record_attachment("12345", "att-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/attachments/{attachment_id}",
        )
        response = client.delete(url)
        response.raise_for_status()


# Record Change Requests endpoints
@handle_request_errors
def get_record_change_request(
    record_id: str, change_request_id: str
) -> JSONAPIResponse[ChangeRequestResource]:
    """
    Get a change request for a record.

    Args:
        record_id: The ID of the record
        change_request_id: The ID of the change request

    Returns:
        JSONAPIResponse containing change request data

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
        >>> print(change_request.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/change-requests/{change_request_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[ChangeRequestResource](
            data=ChangeRequestResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_most_recent_record_change_request(
    record_id: str,
) -> JSONAPIResponse[ChangeRequestResource]:
    """
    Get the most recent change request for a record.

    Args:
        record_id: The ID of the record

    Returns:
        JSONAPIResponse containing change request data

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
        >>> print(change_request.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/change-requests"
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[ChangeRequestResource](
            data=ChangeRequestResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def create_record_change_request(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[ChangeRequestResource]:
    """
    Create a change request for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the change request data

    Returns:
        JSONAPIResponse containing the created change request data

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
        >>> print(change_request.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/change-requests"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[ChangeRequestResource](
            data=ChangeRequestResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def cancel_record_change_request(record_id: str, change_request_id: str) -> None:
    """
    Cancel a change request for a record.

    Args:
        record_id: The ID of the record
        change_request_id: The ID of the change request to cancel

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or change request is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.cancel_record_change_request("12345", "cr-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/change-requests/{change_request_id}",
        )
        response = client.delete(url)
        response.raise_for_status()


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
def create_record_workflow_step(
    record_id: str, data: dict[str, Any]
) -> JSONAPIResponse[WorkflowStepResource]:
    """
    Create a workflow step for a record.

    Args:
        record_id: The ID of the record
        data: Dictionary containing the workflow step data

    Returns:
        JSONAPIResponse containing the created WorkflowStepResource

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
        >>> response = opengov_api.create_record_workflow_step("12345", step_data)
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/workflow-steps"
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepResource](
            data=WorkflowStepResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_workflow_step(
    record_id: str, step_id: str
) -> JSONAPIResponse[WorkflowStepResource]:
    """
    Get a specific workflow step on a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step

    Returns:
        JSONAPIResponse containing the WorkflowStepResource

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
        >>> response = opengov_api.get_record_workflow_step("12345", "step-123")
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepResource](
            data=WorkflowStepResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def update_record_workflow_step(
    record_id: str, step_id: str, data: dict[str, Any]
) -> JSONAPIResponse[WorkflowStepResource]:
    """
    Update a workflow step on a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        data: Dictionary containing the workflow step data to update

    Returns:
        JSONAPIResponse containing the updated WorkflowStepResource

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
        >>> response = opengov_api.update_record_workflow_step("12345", "step-123", step_data)
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepResource](
            data=WorkflowStepResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def delete_record_workflow_step(record_id: str, step_id: str) -> None:
    """
    Delete a workflow step from a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step to delete

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record or step is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.delete_record_workflow_step("12345", "step-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}",
        )
        response = client.delete(url)
        response.raise_for_status()


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
) -> JSONAPIResponse[WorkflowStepCommentResource]:
    """
    Create a comment on a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        data: Dictionary containing the comment data

    Returns:
        JSONAPIResponse containing the created WorkflowStepCommentResource

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
        >>> response = opengov_api.create_record_workflow_step_comment("12345", "step-123", comment_data)
        >>> print(response.data.attributes.text)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments",
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepCommentResource](
            data=WorkflowStepCommentResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_workflow_step_comment(
    record_id: str, step_id: str, comment_id: str
) -> JSONAPIResponse[WorkflowStepCommentResource]:
    """
    Get a specific comment on a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        comment_id: The ID of the comment

    Returns:
        JSONAPIResponse containing the WorkflowStepCommentResource

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
        >>> response = opengov_api.get_record_workflow_step_comment("12345", "step-123", "comment-123")
        >>> print(response.data.attributes.text)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments/{comment_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[WorkflowStepCommentResource](
            data=WorkflowStepCommentResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def delete_record_workflow_step_comment(
    record_id: str, step_id: str, comment_id: str
) -> None:
    """
    Delete a comment from a workflow step.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step
        comment_id: The ID of the comment to delete

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record, step, or comment is not found (404)
        OpenGovAPIStatusError: If API returns an error status code

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> opengov_api.delete_record_workflow_step_comment("12345", "step-123", "comment-123")
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments/{comment_id}",
        )
        response = client.delete(url)
        response.raise_for_status()


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
def get_record_collection(
    record_id: str, collection_id: str
) -> JSONAPIResponse[CollectionResource]:
    """
    Get a specific collection on a record.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection

    Returns:
        JSONAPIResponse containing the CollectionResource

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
        >>> response = opengov_api.get_record_collection("12345", "coll-123")
        >>> print(response.data.attributes.name)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[CollectionResource](
            data=CollectionResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def create_record_collection_entry(
    record_id: str, collection_id: str, data: dict[str, Any]
) -> JSONAPIResponse[CollectionEntryResource]:
    """
    Create an entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        data: Dictionary containing the entry data

    Returns:
        JSONAPIResponse containing the created entry data

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
        >>> print(entry.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}",
        )
        response = client.post(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[CollectionEntryResource](
            data=CollectionEntryResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def get_record_collection_entry(
    record_id: str, collection_id: str, entry_id: str
) -> JSONAPIResponse[CollectionEntryResource]:
    """
    Get a specific entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        entry_id: The ID of the entry

    Returns:
        JSONAPIResponse containing entry data

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
        >>> print(entry.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}/entries/{entry_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[CollectionEntryResource](
            data=CollectionEntryResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def update_record_collection_entry(
    record_id: str, collection_id: str, entry_id: str, data: dict[str, Any]
) -> JSONAPIResponse[CollectionEntryResource]:
    """
    Update an entry in a record collection.

    Args:
        record_id: The ID of the record
        collection_id: The ID of the collection
        entry_id: The ID of the entry
        data: Dictionary containing the entry data to update

    Returns:
        JSONAPIResponse containing the updated entry data

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
        >>> print(entry.data.id)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/collections/{collection_id}/entries/{entry_id}",
        )
        response = client.patch(url, json=data)
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[CollectionEntryResource](
            data=CollectionEntryResource(**data["data"]),
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )
