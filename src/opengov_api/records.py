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

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_records() -> dict[str, Any]:
    """
    List all records for the configured community.

    Returns:
        Dictionary containing records data from the API

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
        >>> records = opengov_api.list_records()
        >>> print(records)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "records")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_guests(record_id: str) -> dict[str, Any]:
    """
    List guests for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing guests data from the API

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
        >>> guests = opengov_api.list_record_guests("12345")
        >>> print(guests)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"records/{record_id}/guests")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_additional_locations(record_id: str) -> dict[str, Any]:
    """
    List additional locations for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing additional locations data from the API

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
        >>> locations = opengov_api.list_record_additional_locations("12345")
        >>> print(locations)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/additional-locations"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_attachments(record_id: str) -> dict[str, Any]:
    """
    List attachments for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing attachments data from the API

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
        >>> attachments = opengov_api.list_record_attachments("12345")
        >>> print(attachments)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/attachments"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_workflow_steps(record_id: str) -> dict[str, Any]:
    """
    List workflow steps for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing workflow steps data from the API

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
        >>> steps = opengov_api.list_record_workflow_steps("12345")
        >>> print(steps)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/workflow-steps"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_workflow_step_comments(record_id: str, step_id: str) -> dict[str, Any]:
    """
    List comments for a workflow step on a record.

    Args:
        record_id: The ID of the record
        step_id: The ID of the workflow step

    Returns:
        Dictionary containing comments data from the API

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
        >>> comments = opengov_api.list_record_workflow_step_comments("12345", "step-123")
        >>> print(comments)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(),
            get_community(),
            f"records/{record_id}/workflow-steps/{step_id}/comments",
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
def list_record_collections(record_id: str) -> dict[str, Any]:
    """
    List collections for a record.

    Args:
        record_id: The ID of the record

    Returns:
        Dictionary containing collections data from the API

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
        >>> collections = opengov_api.list_record_collections("12345")
        >>> print(collections)
    """
    with _get_client() as client:
        url = build_url(
            get_base_url(), get_community(), f"records/{record_id}/collections"
        )
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


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
