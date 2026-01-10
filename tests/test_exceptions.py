"""Tests for exception classes."""

import httpx
import pytest

from opengov_api.exceptions import (
    OpenGovAPIError,
    OpenGovConfigurationError,
    OpenGovAPIConnectionError,
    OpenGovAPITimeoutError,
    OpenGovResponseParseError,
    OpenGovAPIStatusError,
    OpenGovBadRequestError,
    OpenGovAuthenticationError,
    OpenGovPermissionDeniedError,
    OpenGovNotFoundError,
    OpenGovRateLimitError,
    OpenGovInternalServerError,
)


def test_base_exception():
    """Test base OpenGovAPIError can be raised and caught."""
    with pytest.raises(OpenGovAPIError):
        raise OpenGovAPIError("Test error")


def test_configuration_error():
    """Test configuration error for missing API key."""
    error = OpenGovConfigurationError("API key not set")
    assert str(error) == "API key not set"
    assert isinstance(error, OpenGovAPIError)


def test_connection_error():
    """Test connection error with request context."""
    request = httpx.Request("GET", "https://api.example.com")
    error = OpenGovAPIConnectionError("Connection failed", request=request)
    assert str(error) == "Connection failed"
    assert error.request == request
    assert isinstance(error, OpenGovAPIError)


def test_timeout_error():
    """Test timeout error inherits from connection error."""
    request = httpx.Request("GET", "https://api.example.com")
    error = OpenGovAPITimeoutError("Request timed out", request=request)
    assert str(error) == "Request timed out"
    assert error.request == request
    assert isinstance(error, OpenGovAPIConnectionError)
    assert isinstance(error, OpenGovAPIError)


def test_response_parse_error():
    """Test response parse error with body context."""
    response = httpx.Response(200, text="not json")
    error = OpenGovResponseParseError(
        "Failed to parse JSON", response=response, body="not json"
    )
    assert str(error) == "Failed to parse JSON"
    assert error.response == response
    assert error.body == "not json"
    assert isinstance(error, OpenGovAPIError)


def test_status_error():
    """Test status error with response context."""
    response = httpx.Response(
        400,
        headers={"x-request-id": "test-123"},
        json={"error": "Bad request"},
    )
    error = OpenGovAPIStatusError(
        "Bad request", response=response, body={"error": "Bad request"}
    )
    assert str(error) == "Bad request"
    assert error.status_code == 400
    assert error.request_id == "test-123"
    assert error.body == {"error": "Bad request"}
    assert isinstance(error, OpenGovAPIError)


def test_status_error_repr():
    """Test status error string representation."""
    response = httpx.Response(404, headers={"x-request-id": "req-456"})
    error = OpenGovNotFoundError("Not found", response=response)
    repr_str = repr(error)
    assert "OpenGovNotFoundError" in repr_str
    assert "status_code=404" in repr_str
    assert "request_id='req-456'" in repr_str


def test_bad_request_error():
    """Test 400 Bad Request error."""
    response = httpx.Response(400)
    error = OpenGovBadRequestError("Invalid input", response=response)
    assert error.status_code == 400
    assert isinstance(error, OpenGovAPIStatusError)


def test_authentication_error():
    """Test 401 Authentication error."""
    response = httpx.Response(401)
    error = OpenGovAuthenticationError("Unauthorized", response=response)
    assert error.status_code == 401
    assert isinstance(error, OpenGovAPIStatusError)


def test_permission_denied_error():
    """Test 403 Permission Denied error."""
    response = httpx.Response(403)
    error = OpenGovPermissionDeniedError("Forbidden", response=response)
    assert error.status_code == 403
    assert isinstance(error, OpenGovAPIStatusError)


def test_not_found_error():
    """Test 404 Not Found error."""
    response = httpx.Response(404)
    error = OpenGovNotFoundError("Resource not found", response=response)
    assert error.status_code == 404
    assert isinstance(error, OpenGovAPIStatusError)


def test_rate_limit_error():
    """Test 429 Rate Limit error."""
    response = httpx.Response(429)
    error = OpenGovRateLimitError("Too many requests", response=response)
    assert error.status_code == 429
    assert isinstance(error, OpenGovAPIStatusError)


def test_internal_server_error():
    """Test 500+ Internal Server error."""
    response = httpx.Response(503)
    error = OpenGovInternalServerError("Service unavailable", response=response)
    assert error.status_code == 503
    assert isinstance(error, OpenGovAPIStatusError)


def test_catch_all_sdk_errors():
    """Test that all SDK exceptions can be caught with base exception."""
    exceptions = [
        OpenGovConfigurationError("config"),
        OpenGovAPIConnectionError("connection"),
        OpenGovAPITimeoutError("timeout"),
        OpenGovResponseParseError("parse"),
    ]

    for exc in exceptions:
        with pytest.raises(OpenGovAPIError):
            raise exc
