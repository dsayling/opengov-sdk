"""
Base utilities for OpenGov API SDK.

Provides:
- URL construction helpers
- Error handling and exception mapping
- Response parsing with validation
- Request execution wrapper
- Automatic retry with exponential backoff for transient errors
"""

import functools
import json
import random
import time
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


def _calculate_retry_delay(attempt: int, retry_after: float | None = None) -> float:
    """
    Calculate retry delay with exponential backoff and jitter.

    Args:
        attempt: Current retry attempt (0-indexed)
        retry_after: Optional Retry-After header value in seconds

    Returns:
        Delay in seconds before next retry
    """
    from .client import get_retry_config

    config = get_retry_config()

    if retry_after is not None:
        # Respect Retry-After header if provided
        return min(retry_after, config.max_delay)

    # Exponential backoff: delay = initial * (multiplier ^ attempt)
    delay = config.initial_delay * (config.backoff_multiplier**attempt)
    delay = min(delay, config.max_delay)

    # Add random jitter to avoid thundering herd
    jitter = delay * config.jitter_factor * (2 * random.random() - 1)
    return delay + jitter


def _is_retryable_error(
    exception: Exception,
) -> tuple[bool, float | None]:
    """
    Determine if an error is retryable and extract Retry-After if available.

    Args:
        exception: The exception to check

    Returns:
        Tuple of (is_retryable, retry_after_seconds)
    """
    # Timeout errors are retryable
    if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError)):
        return (True, None)

    # Network errors are retryable
    if isinstance(exception, httpx.NetworkError):
        return (True, None)

    # HTTP status errors - check status code
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code

        # 429 Rate Limit - retryable, check Retry-After header
        if status_code == 429:
            retry_after = None
            retry_after_header = exception.response.headers.get("retry-after")
            if retry_after_header:
                try:
                    retry_after = float(retry_after_header)
                except ValueError:
                    pass  # Ignore if not a number
            return (True, retry_after)

        # 500+ Server Errors - retryable
        if status_code >= 500:
            return (True, None)

    # Not retryable
    return (False, None)


def handle_request_errors(
    func: Callable[P, R],
) -> Callable[P, R]:
    """
    Decorator to wrap httpx exceptions with automatic retry and exponential backoff.

    Retries transient errors:
    - 429 Rate Limit (respects Retry-After header)
    - 500+ Server Errors
    - Timeout errors
    - Connection/network errors

    Does NOT retry client errors (400, 401, 403, 404).

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling and retry logic
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        from .client import get_retry_config

        config = get_retry_config()
        last_exception: Exception | None = None
        attempt = 0

        while attempt <= config.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                is_retryable, retry_after = _is_retryable_error(e)

                # If not retryable or out of retries, convert and raise
                if not is_retryable or attempt >= config.max_retries:
                    # Convert to custom exceptions
                    if isinstance(e, httpx.TimeoutException):
                        request = None
                        try:
                            request = e.request
                        except (RuntimeError, AttributeError):
                            pass
                        raise OpenGovAPITimeoutError(
                            f"Request timed out after {attempt} attempts: {e}",
                            request=request,
                            attempts=attempt + 1,
                        ) from e
                    elif isinstance(e, httpx.ConnectError):
                        request = None
                        try:
                            request = e.request
                        except (RuntimeError, AttributeError):
                            pass
                        raise OpenGovAPIConnectionError(
                            f"Connection failed after {attempt} attempts: {e}",
                            request=request,
                            attempts=attempt + 1,
                        ) from e
                    elif isinstance(e, httpx.NetworkError):
                        request = None
                        try:
                            request = e.request
                        except (RuntimeError, AttributeError):
                            pass
                        raise OpenGovAPIConnectionError(
                            f"Network error after {attempt} attempts: {e}",
                            request=request,
                            attempts=attempt + 1,
                        ) from e
                    elif isinstance(e, httpx.HTTPStatusError):
                        # Create status error with attempt count
                        status_error = make_status_error(e.response)
                        status_error.attempts = attempt + 1
                        raise status_error from e
                    else:
                        # Unknown exception, re-raise
                        raise

                # Calculate delay and retry
                delay = _calculate_retry_delay(attempt, retry_after)
                attempt += 1
                time.sleep(delay)

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected error in retry loop")

    return wrapper
