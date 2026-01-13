"""
Base utilities for OpenGov API SDK.

Provides:
- URL construction helpers
- Error handling and exception mapping
- Response parsing with validation
- Request execution wrapper
"""

import functools
import json
from typing import Any, Callable, ParamSpec, TypeVar

import httpx


from .exceptions import (
    OpenGovAPIConnectionError,
    OpenGovAPIStatusError,
    OpenGovAPITimeoutError,
    OpenGovAuthenticationError,
    OpenGovBadRequestError,
    OpenGovInternalServerError,
    OpenGovNotFoundError,
    OpenGovPermissionDeniedError,
    OpenGovRateLimitError,
    OpenGovResponseParseError,
)

# Type variables for preserving function signatures in decorators
P = ParamSpec("P")
R = TypeVar("R")


def build_url(base_url: str, community: str, endpoint: str) -> str:
    """
    Construct full API URL for endpoint.

    Args:
        base_url: Base API URL (e.g., "https://api.plce.opengov.com/plce/v2")
        community: Community identifier (e.g., "your-community")
        endpoint: API endpoint path (e.g., "records", "users")

    Returns:
        Full URL path
    """
    base_url = base_url.rstrip("/")
    endpoint = endpoint.lstrip("/")
    return f"{base_url}/{community}/{endpoint}"


def make_status_error(response: httpx.Response) -> OpenGovAPIStatusError:
    """
    Create appropriate exception from HTTP status code.

    Args:
        response: The HTTP response object

    Returns:
        Appropriate OpenGovAPIStatusError subclass
    """
    status_code = response.status_code

    # Try to parse error body
    body: dict[str, Any] | str | None = None
    try:
        body = response.json()
        # Extract error message if available in standard formats
        if isinstance(body, dict):
            error_message = (
                body.get("message")
                or body.get("error")
                or body.get("detail")
                or f"Status {status_code}: {response.reason_phrase}"
            )
        else:
            error_message = f"Status {status_code}: {response.reason_phrase}"
    except Exception:
        # If JSON parsing fails, use response text
        body = response.text
        error_message = f"Status {status_code}: {response.reason_phrase}"

    # Map status code to specific exception
    error_class = OpenGovAPIStatusError
    if status_code == 400:
        error_class = OpenGovBadRequestError
    elif status_code == 401:
        error_class = OpenGovAuthenticationError
    elif status_code == 403:
        error_class = OpenGovPermissionDeniedError
    elif status_code == 404:
        error_class = OpenGovNotFoundError
    elif status_code == 429:
        error_class = OpenGovRateLimitError
    elif status_code >= 500:
        error_class = OpenGovInternalServerError

    return error_class(error_message, response=response, body=body)


def parse_json_response(response: httpx.Response) -> dict[str, Any]:
    """
    Parse and validate JSON response with error handling.

    Args:
        response: The HTTP response object

    Returns:
        Parsed JSON as dictionary

    Raises:
        OpenGovResponseParseError: If JSON parsing fails
    """
    try:
        return response.json()
    except json.JSONDecodeError as e:
        raise OpenGovResponseParseError(
            f"Failed to parse JSON response: {e}",
            response=response,
            body=response.text,
        ) from e


def handle_request_errors(
    func: Callable[P, R],
) -> Callable[P, R]:
    """
    Decorator to wrap httpx exceptions into custom exceptions.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except httpx.TimeoutException as e:
            # Try to get request, but it may not be set
            request = None
            try:
                request = e.request
            except (RuntimeError, AttributeError):
                pass
            raise OpenGovAPITimeoutError(
                f"Request timed out: {e}",
                request=request,
            ) from e
        except httpx.ConnectError as e:
            # Try to get request, but it may not be set
            request = None
            try:
                request = e.request
            except (RuntimeError, AttributeError):
                pass
            raise OpenGovAPIConnectionError(
                f"Connection failed: {e}",
                request=request,
            ) from e
        except httpx.NetworkError as e:
            # Try to get request, but it may not be set
            request = None
            try:
                request = e.request
            except (RuntimeError, AttributeError):
                pass
            raise OpenGovAPIConnectionError(
                f"Network error: {e}",
                request=request,
            ) from e
        except httpx.HTTPStatusError as e:
            # Map to custom status error
            raise make_status_error(e.response) from e

    return wrapper
