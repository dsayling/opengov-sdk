"""
Files API endpoints for OpenGov API SDK.

## Usage Example

```python
import opengov_api

# Configure
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# List all files
files = opengov_api.list_files()
print(files)

# Get a specific file (includes pre-signed download URL)
file = opengov_api.get_file("file-12345")
print(file)

# Create a file upload (returns pre-signed upload URL)
# Step 1: Create file entry
upload_info = opengov_api.create_file_upload({
    "data": {
        "type": "files",
        "attributes": {
            "fileName": "document.pdf",
            "contentType": "application/pdf",
            "fileSize": 1024000
        }
    }
})

# Step 2: Upload to the pre-signed URL (use requests or httpx separately)
# PUT upload_info["data"]["attributes"]["uploadUrl"]
# with file content and headers:
#   Content-Type: application/pdf
#   x-ms-blob-type: BlockBlob

# Step 3: Associate with an entity (e.g., record attachment)
# opengov_api.add_record_attachment(record_id, {
#     "data": {
#         "type": "record-attachments",
#         "relationships": {
#             "file": {"data": {"id": upload_info["data"]["id"]}}
#         }
#     }
# })
```
"""

from typing import Any


from .base import build_url, handle_request_errors, parse_json_response
from .client import _get_client, get_base_url, get_community


@handle_request_errors
def list_files() -> dict[str, Any]:
    """
    List all files for the configured community.

    Note: Download URLs are not included in list responses.
    Use get_file() to retrieve a specific file with its download URL.

    Returns:
        Dictionary containing files data from the API

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
        >>> files = opengov_api.list_files()
        >>> print(files)
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "files")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def get_file(file_id: str) -> dict[str, Any]:
    """
    Get a specific file by ID.

    Returns file information including a pre-signed Azure Blob Storage URL
    for downloading. The pre-signed URL is valid for 1 hour.

    Args:
        file_id: The ID of the file to retrieve

    Returns:
        Dictionary containing file data from the API, including download URL

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
        >>> file = opengov_api.get_file("file-12345")
        >>> download_url = file["data"]["attributes"]["downloadUrl"]
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), f"files/{file_id}")
        response = client.get(url)
        response.raise_for_status()
        return parse_json_response(response)


@handle_request_errors
def create_file_upload(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new file entry and receive a pre-signed upload URL.

    This is the first step in the file upload process:
    1. Call this function to create a file entry and get an upload URL
    2. Use the returned pre-signed URL to upload your file to Azure Blob Storage
    3. Associate the uploaded file with an entity (e.g., record attachment)

    The pre-signed URL expires after 1 hour.

    Args:
        data: Dictionary containing file metadata in JSON:API format

    Returns:
        Dictionary containing the file entry with upload URL

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
        >>> upload_info = opengov_api.create_file_upload({
        ...     "data": {
        ...         "type": "files",
        ...         "attributes": {
        ...             "fileName": "document.pdf",
        ...             "contentType": "application/pdf",
        ...             "fileSize": 1024000
        ...         }
        ...     }
        ... })
        >>> upload_url = upload_info["data"]["attributes"]["uploadUrl"]
        >>> file_id = upload_info["data"]["id"]
    """
    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "files")
        response = client.post(url, json=data)
        response.raise_for_status()
        return parse_json_response(response)
