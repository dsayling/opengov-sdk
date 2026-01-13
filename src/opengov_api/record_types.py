"""
Record Types API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all record types
record_types = opengov_api.list_record_types()
print(record_types)

# Filter by department
record_types = opengov_api.list_record_types(department_id="dept-123")
print(record_types)

# Get a specific record type
record_type = opengov_api.get_record_type("rt-456789")
print(record_type)

# Record types define the configuration for permits, licenses, and other records
# They specify required fields, workflows, fees, and other settings
```
"""

from typing import Any, Iterator

from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community
from .models import (
    JSONAPIResponse,
    Links,
    ListRecordTypesParams,
    Meta,
    RecordTypeResource,
)


@handle_request_errors
def list_record_types(
    *,
    department_id: str | None = None,
    page_number: int = 1,
    page_size: int = 20,
) -> JSONAPIResponse[RecordTypeResource]:
    """
    List record types for the configured community with pagination.

    Record types define the configuration templates for different types of
    permits, licenses, and records in the system.

    Args:
        department_id: Filter by department ID
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)

    Returns:
        JSONAPIResponse containing RecordTypeResource objects with pagination info

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>>
        >>> # List all record types
        >>> response = opengov_api.list_record_types()
        >>>
        >>> # Access records
        >>> for record_type in response.data:
        ...     print(f"{record_type.attributes.name}: {record_type.attributes.status}")
        >>>
        >>> # Check pagination
        >>> print(f"Page {response.current_page()} of {response.total_pages()}")
    """
    # Build params using ListRecordTypesParams model
    params_model = ListRecordTypesParams(
        filter_department_id=department_id,
        page_number=page_number,
        page_size=page_size,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "record-types")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        # Parse into typed response
        return JSONAPIResponse[RecordTypeResource](
            data=[RecordTypeResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )


@handle_request_errors
def iter_record_types(
    *,
    department_id: str | None = None,
    page_size: int = 100,
) -> Iterator[RecordTypeResource]:
    """
    Iterate through all record types automatically handling pagination.

    This generator function fetches all pages automatically, yielding
    individual record types one at a time.

    Args:
        department_id: Filter by department ID
        page_size: Number of records per page (1-100, default 100 for efficiency)

    Yields:
        RecordTypeResource objects one at a time across all pages

    Example:
        >>> for record_type in opengov_api.iter_record_types():
        ...     print(f"{record_type.attributes.name}")
    """
    page = 1
    while True:
        response = list_record_types(
            department_id=department_id,
            page_number=page,
            page_size=page_size,
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
def get_record_type(record_type_id: str) -> dict[str, Any]:
    """
    Get a specific record type by ID.

    Args:
        record_type_id: The ID of the record type to retrieve

    Returns:
        Dictionary containing record type data from the API

    Raises:
        OpenGovConfigurationError: If API key or community is not configured
        OpenGovAPIConnectionError: If connection fails
        OpenGovAPITimeoutError: If request times out
        OpenGovNotFoundError: If record type is not found (404)
        OpenGovAPIStatusError: If API returns an error status code
        OpenGovResponseParseError: If response cannot be parsed as JSON

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
        >>> opengov_api.set_community("your-community")
        >>> record_type = opengov_api.get_record_type("rt-456789")
        >>> print(record_type)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"record-types/{record_type_id}"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


# Nested resource endpoints


@handle_request_errors
def list_record_type_attachments(
    record_type_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    List attachment templates for a record type.

    Args:
        record_type_id: The ID of the record type
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)

    Returns:
        Dictionary containing attachment templates from the API

    Example:
        >>> attachments = opengov_api.list_record_type_attachments("rt-456789")
        >>> print(attachments)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/attachments",
        )
        params = {"page[number]": page_number, "page[size]": page_size}
        response = client.get(url, params=params)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_type_attachment(attachment_id: str) -> dict[str, Any]:
    """
    Get a specific attachment template by ID.

    Args:
        attachment_id: The ID of the attachment template

    Returns:
        Dictionary containing attachment template data from the API

    Example:
        >>> attachment = opengov_api.get_record_type_attachment("rt-attachment-334455")
        >>> print(attachment)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/attachments/{attachment_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def list_record_type_document_templates(
    record_type_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    List document templates for a record type.

    Args:
        record_type_id: The ID of the record type
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)

    Returns:
        Dictionary containing document templates from the API

    Example:
        >>> docs = opengov_api.list_record_type_document_templates("rt-456789")
        >>> print(docs)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/document-templates",
        )
        params = {"page[number]": page_number, "page[size]": page_size}
        response = client.get(url, params=params)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_type_document_template(document_template_id: str) -> dict[str, Any]:
    """
    Get a specific document template by ID.

    Args:
        document_template_id: The ID of the document template

    Returns:
        Dictionary containing document template data from the API

    Example:
        >>> doc = opengov_api.get_record_type_document_template("rt-document-556677")
        >>> print(doc)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/document-templates/{document_template_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def list_record_type_fees(
    record_type_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    List fee templates for a record type.

    Args:
        record_type_id: The ID of the record type
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)

    Returns:
        Dictionary containing fee templates from the API

    Example:
        >>> fees = opengov_api.list_record_type_fees("rt-456789")
        >>> print(fees)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/fees",
        )
        params = {"page[number]": page_number, "page[size]": page_size}
        response = client.get(url, params=params)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_type_fee(fee_id: str) -> dict[str, Any]:
    """
    Get a specific fee template by ID.

    Args:
        fee_id: The ID of the fee template

    Returns:
        Dictionary containing fee template data from the API

    Example:
        >>> fee = opengov_api.get_record_type_fee("record-type-fees-1000013")
        >>> print(fee)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/fees/{fee_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_type_form(record_type_id: str) -> dict[str, Any]:
    """
    Get the form fields for a record type.

    Args:
        record_type_id: The ID of the record type

    Returns:
        Dictionary containing form field definitions from the API

    Example:
        >>> form = opengov_api.get_record_type_form("rt-456789")
        >>> print(form)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/form",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def list_record_type_workflow(
    record_type_id: str,
    *,
    page_number: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    List workflow step templates for a record type.

    Args:
        record_type_id: The ID of the record type
        page_number: Page number (1-based, default 1)
        page_size: Number of records per page (1-100, default 20)

    Returns:
        Dictionary containing workflow step templates from the API

    Example:
        >>> workflow = opengov_api.list_record_type_workflow("rt-456789")
        >>> print(workflow)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/workflow",
        )
        params = {"page[number]": page_number, "page[size]": page_size}
        response = client.get(url, params=params)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_record_type_workflow_step(
    record_type_id: str, workflow_template_id: str
) -> dict[str, Any]:
    """
    Get a specific workflow step template.

    Args:
        record_type_id: The ID of the record type
        workflow_template_id: The ID of the workflow template step

    Returns:
        Dictionary containing workflow step template data from the API

    Example:
        >>> step = opengov_api.get_record_type_workflow_step("rt-456789", "rt-template-step-101112")
        >>> print(step)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"record-types/{record_type_id}/workflow/{workflow_template_id}",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)
