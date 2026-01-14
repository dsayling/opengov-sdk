"""
Custom exceptions for OpenGov API SDK.

All exceptions inherit from OpenGovAPIError, allowing users to catch
all SDK errors with a single except clause.

Exception hierarchy mirrors OpenAI SDK pattern:
- Connection/network errors separate from HTTP status errors
- Specific subclasses for common status codes
- Rich context (status_code, request_id, response body)
"""

from typing import Any

import httpx


class OpenGovAPIError(Exception):
    """Base exception for all OpenGov API errors."""

    pass


class OpenGovConfigurationError(OpenGovAPIError):
    """SDK misconfiguration (missing API key, community, etc)."""

    pass


class OpenGovAPIConnectionError(OpenGovAPIError):
    """Network/connection failures."""

    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request | None = None,
        attempts: int = 1,
    ) -> None:
        super().__init__(message)
        self.request = request
        self.attempts = attempts


class OpenGovAPITimeoutError(OpenGovAPIConnectionError):
    """Request timeouts."""

    pass


class OpenGovResponseParseError(OpenGovAPIError):
    """Failed to parse API response."""

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response | None = None,
        body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.response = response
        self.body = body


class OpenGovAPIStatusError(OpenGovAPIError):
    """HTTP 4xx/5xx responses."""

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: dict[str, Any] | str | None = None,
    ) -> None:
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")
        self.body = body
        self.attempts = 1  # Default to 1, can be overridden by retry logic

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={str(self)!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )


class OpenGovBadRequestError(OpenGovAPIStatusError):
    """HTTP 400 Bad Request."""

    pass


class OpenGovAuthenticationError(OpenGovAPIStatusError):
    """HTTP 401 Unauthorized."""

    pass


class OpenGovPermissionDeniedError(OpenGovAPIStatusError):
    """HTTP 403 Forbidden."""

    pass


class OpenGovNotFoundError(OpenGovAPIStatusError):
    """HTTP 404 Not Found."""

    pass


class OpenGovRateLimitError(OpenGovAPIStatusError):
    """HTTP 429 Too Many Requests."""

    pass


class OpenGovInternalServerError(OpenGovAPIStatusError):
    """HTTP 500+ Server Errors."""

    pass
