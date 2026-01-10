"""Tests for base utility functions."""

import httpx
import pytest

from opengov_api.base import (
    build_url,
    make_status_error,
    parse_json_response,
    handle_request_errors,
)
from opengov_api.exceptions import (
    OpenGovBadRequestError,
    OpenGovAuthenticationError,
    OpenGovPermissionDeniedError,
    OpenGovNotFoundError,
    OpenGovRateLimitError,
    OpenGovInternalServerError,
    OpenGovAPIStatusError,
    OpenGovResponseParseError,
    OpenGovAPIConnectionError,
    OpenGovAPITimeoutError,
)


class TestBuildUrl:
    """Tests for build_url function."""

    def test_build_basic_url(self):
        """Test basic URL construction."""
        url = build_url(
            "https://api.plce.opengov.com/plce/v2", "your-community", "records"
        )
        assert url == "https://api.plce.opengov.com/plce/v2/your-community/records"

    def test_build_url_strips_trailing_slash(self):
        """Test that trailing slashes are handled."""
        url = build_url(
            "https://api.plce.opengov.com/plce/v2/", "your-community", "records"
        )
        assert url == "https://api.plce.opengov.com/plce/v2/your-community/records"

    def test_build_url_strips_leading_slash(self):
        """Test that leading slashes are handled."""
        url = build_url(
            "https://api.plce.opengov.com/plce/v2", "your-community", "/records"
        )
        assert url == "https://api.plce.opengov.com/plce/v2/your-community/records"

    def test_build_url_with_nested_endpoint(self):
        """Test URL construction with nested paths."""
        url = build_url(
            "https://api.plce.opengov.com/plce/v2",
            "your-community",
            "records/12345",
        )
        assert (
            url == "https://api.plce.opengov.com/plce/v2/your-community/records/12345"
        )


class TestMakeStatusError:
    """Tests for make_status_error function."""

    def test_400_bad_request(self):
        """Test 400 status code maps to OpenGovBadRequestError."""
        response = httpx.Response(400, json={"message": "Invalid input"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovBadRequestError)
        assert "Invalid input" in str(error)
        assert error.status_code == 400

    def test_401_authentication(self):
        """Test 401 status code maps to OpenGovAuthenticationError."""
        response = httpx.Response(401, json={"message": "Unauthorized"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovAuthenticationError)
        assert error.status_code == 401

    def test_403_permission_denied(self):
        """Test 403 status code maps to OpenGovPermissionDeniedError."""
        response = httpx.Response(403, json={"message": "Forbidden"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovPermissionDeniedError)
        assert error.status_code == 403

    def test_404_not_found(self):
        """Test 404 status code maps to OpenGovNotFoundError."""
        response = httpx.Response(404, json={"message": "Not found"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovNotFoundError)
        assert error.status_code == 404

    def test_429_rate_limit(self):
        """Test 429 status code maps to OpenGovRateLimitError."""
        response = httpx.Response(429, json={"message": "Too many requests"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovRateLimitError)
        assert error.status_code == 429

    def test_500_internal_server_error(self):
        """Test 500+ status codes map to OpenGovInternalServerError."""
        for status_code in [500, 502, 503, 504]:
            response = httpx.Response(status_code, json={"message": "Server error"})
            error = make_status_error(response)
            assert isinstance(error, OpenGovInternalServerError)
            assert error.status_code == status_code

    def test_other_status_codes(self):
        """Test other status codes map to base OpenGovAPIStatusError."""
        response = httpx.Response(418, json={"message": "I'm a teapot"})
        error = make_status_error(response)
        assert isinstance(error, OpenGovAPIStatusError)
        assert error.status_code == 418

    def test_error_message_from_message_field(self):
        """Test error extraction from 'message' field."""
        response = httpx.Response(400, json={"message": "Custom error"})
        error = make_status_error(response)
        assert "Custom error" in str(error)

    def test_error_message_from_error_field(self):
        """Test error extraction from 'error' field."""
        response = httpx.Response(400, json={"error": "Custom error"})
        error = make_status_error(response)
        assert "Custom error" in str(error)

    def test_error_message_from_detail_field(self):
        """Test error extraction from 'detail' field."""
        response = httpx.Response(400, json={"detail": "Custom error"})
        error = make_status_error(response)
        assert "Custom error" in str(error)

    def test_error_with_non_json_response(self):
        """Test error handling when response is not JSON."""
        response = httpx.Response(500, text="Internal Server Error")
        error = make_status_error(response)
        assert isinstance(error, OpenGovInternalServerError)
        assert error.body == "Internal Server Error"

    def test_error_preserves_response(self):
        """Test that response object is preserved in error."""
        response = httpx.Response(404, json={"message": "Not found"})
        error = make_status_error(response)
        assert error.response == response


class TestParseJsonResponse:
    """Tests for parse_json_response function."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        response = httpx.Response(200, json={"data": "value"})
        result = parse_json_response(response)
        assert result == {"data": "value"}

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises OpenGovResponseParseError."""
        response = httpx.Response(200, text="not valid json")
        with pytest.raises(OpenGovResponseParseError) as exc_info:
            parse_json_response(response)
        assert "Failed to parse JSON" in str(exc_info.value)
        assert exc_info.value.response == response
        assert exc_info.value.body == "not valid json"

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        response = httpx.Response(200, text="")
        with pytest.raises(OpenGovResponseParseError):
            parse_json_response(response)


class TestHandleRequestErrors:
    """Tests for handle_request_errors decorator."""

    def test_successful_request(self):
        """Test decorator doesn't interfere with successful requests."""

        @handle_request_errors
        def successful_func():
            return {"success": True}

        result = successful_func()
        assert result == {"success": True}

    def test_handles_timeout_exception(self):
        """Test decorator converts httpx.TimeoutException."""

        @handle_request_errors
        def timeout_func():
            raise httpx.TimeoutException("Timeout")

        with pytest.raises(OpenGovAPITimeoutError) as exc_info:
            timeout_func()
        assert "Request timed out" in str(exc_info.value)

    def test_handles_connect_error(self):
        """Test decorator converts httpx.ConnectError."""

        @handle_request_errors
        def connect_error_func():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(OpenGovAPIConnectionError) as exc_info:
            connect_error_func()
        assert "Connection failed" in str(exc_info.value)

    def test_handles_network_error(self):
        """Test decorator converts httpx.NetworkError."""

        @handle_request_errors
        def network_error_func():
            raise httpx.NetworkError("Network error")

        with pytest.raises(OpenGovAPIConnectionError) as exc_info:
            network_error_func()
        assert "Network error" in str(exc_info.value)

    def test_handles_http_status_error(self):
        """Test decorator converts httpx.HTTPStatusError."""

        @handle_request_errors
        def status_error_func():
            response = httpx.Response(404, json={"message": "Not found"})
            raise httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", "http://test"),
                response=response,
            )

        with pytest.raises(OpenGovNotFoundError):
            status_error_func()

    def test_preserves_other_exceptions(self):
        """Test decorator doesn't catch non-httpx exceptions."""

        @handle_request_errors
        def other_error_func():
            raise ValueError("Some other error")

        with pytest.raises(ValueError):
            other_error_func()
