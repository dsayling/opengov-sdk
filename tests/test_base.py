"""Tests for base utility functions."""

from unittest.mock import patch

import httpx
import pytest

from opengov_api.base import (
    build_url,
    make_status_error,
    parse_json_response,
    handle_request_errors,
    _calculate_retry_delay,
    _is_retryable_error,
)
from opengov_api.client import get_retry_config
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

    @patch("time.sleep")
    def test_handles_timeout_exception(self, mock_sleep):
        """Test decorator converts httpx.TimeoutException."""

        @handle_request_errors
        def timeout_func():
            raise httpx.TimeoutException("Timeout")

        with pytest.raises(OpenGovAPITimeoutError) as exc_info:
            timeout_func()
        assert "Request timed out" in str(exc_info.value)

    @patch("time.sleep")
    def test_handles_connect_error(self, mock_sleep):
        """Test decorator converts httpx.ConnectError."""

        @handle_request_errors
        def connect_error_func():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(OpenGovAPIConnectionError) as exc_info:
            connect_error_func()
        assert "Connection failed" in str(exc_info.value)

    @patch("time.sleep")
    def test_handles_network_error(self, mock_sleep):
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


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    def test_calculate_retry_delay_exponential(self):
        """Test exponential backoff calculation."""
        # First retry should be around 1 second
        delay0 = _calculate_retry_delay(0)
        assert 0.9 <= delay0 <= 1.1  # 1s +/- 10% jitter

        # Second retry should be around 2 seconds
        delay1 = _calculate_retry_delay(1)
        assert 1.8 <= delay1 <= 2.2  # 2s +/- 10% jitter

        # Third retry should be around 4 seconds
        delay2 = _calculate_retry_delay(2)
        assert 3.6 <= delay2 <= 4.4  # 4s +/- 10% jitter

    def test_calculate_retry_delay_respects_max(self):
        """Test that retry delay doesn't exceed maximum."""
        # Very large attempt number should cap at MAX_RETRY_DELAY
        delay = _calculate_retry_delay(100)
        assert delay <= 60.0 + 6.0  # MAX_RETRY_DELAY + max jitter

    def test_calculate_retry_delay_respects_retry_after(self):
        """Test that Retry-After header is respected."""
        delay = _calculate_retry_delay(0, retry_after=5.0)
        assert delay == 5.0

        # Retry-After capped at MAX_RETRY_DELAY
        delay = _calculate_retry_delay(0, retry_after=100.0)
        assert delay == 60.0

    def test_is_retryable_timeout(self):
        """Test timeout errors are retryable."""
        exc = httpx.TimeoutException("Timeout")
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is True
        assert retry_after is None

    def test_is_retryable_connect_error(self):
        """Test connection errors are retryable."""
        exc = httpx.ConnectError("Connection failed")
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is True
        assert retry_after is None

    def test_is_retryable_network_error(self):
        """Test network errors are retryable."""
        exc = httpx.NetworkError("Network error")
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is True
        assert retry_after is None

    def test_is_retryable_429_with_retry_after(self):
        """Test 429 is retryable and extracts Retry-After."""
        response = httpx.Response(
            429,
            json={"message": "Rate limited"},
            headers={"retry-after": "10"},
        )
        exc = httpx.HTTPStatusError(
            "Rate limited",
            request=httpx.Request("GET", "http://test"),
            response=response,
        )
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is True
        assert retry_after == 10.0

    def test_is_retryable_429_without_retry_after(self):
        """Test 429 is retryable even without Retry-After."""
        response = httpx.Response(429, json={"message": "Rate limited"})
        exc = httpx.HTTPStatusError(
            "Rate limited",
            request=httpx.Request("GET", "http://test"),
            response=response,
        )
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is True
        assert retry_after is None

    def test_is_retryable_500_errors(self):
        """Test 500+ errors are retryable."""
        for status_code in [500, 502, 503, 504]:
            response = httpx.Response(status_code, json={"message": "Server error"})
            exc = httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "http://test"),
                response=response,
            )
            is_retryable, retry_after = _is_retryable_error(exc)
            assert is_retryable is True, f"Status {status_code} should be retryable"
            assert retry_after is None

    def test_is_not_retryable_4xx_errors(self):
        """Test 4xx client errors are NOT retryable (except 429)."""
        for status_code in [400, 401, 403, 404]:
            response = httpx.Response(status_code, json={"message": "Client error"})
            exc = httpx.HTTPStatusError(
                "Client error",
                request=httpx.Request("GET", "http://test"),
                response=response,
            )
            is_retryable, retry_after = _is_retryable_error(exc)
            assert is_retryable is False, (
                f"Status {status_code} should NOT be retryable"
            )

    def test_is_not_retryable_other_exceptions(self):
        """Test non-httpx exceptions are NOT retryable."""
        exc = ValueError("Some error")
        is_retryable, retry_after = _is_retryable_error(exc)
        assert is_retryable is False

    @patch("time.sleep")
    def test_retry_succeeds_after_transient_failure(self, mock_sleep):
        """Test successful retry after transient failure."""
        call_count = 0

        @handle_request_errors
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails with 500
                response = httpx.Response(500, json={"message": "Server error"})
                raise httpx.HTTPStatusError(
                    "Server error",
                    request=httpx.Request("GET", "http://test"),
                    response=response,
                )
            # Second call succeeds
            return {"success": True}

        result = flaky_func()
        assert result == {"success": True}
        assert call_count == 2
        assert mock_sleep.call_count == 1  # One retry delay

    @patch("time.sleep")
    def test_retry_exhausted_raises_error(self, mock_sleep):
        """Test that max retries are respected and error is raised."""
        call_count = 0

        @handle_request_errors
        def always_fails():
            nonlocal call_count
            call_count += 1
            response = httpx.Response(500, json={"message": "Server error"})
            raise httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("GET", "http://test"),
                response=response,
            )

        with pytest.raises(OpenGovInternalServerError) as exc_info:
            always_fails()

        # Should try initial + max_retries times
        config = get_retry_config()
        assert call_count == config.max_retries + 1
        assert mock_sleep.call_count == config.max_retries
        # Check attempts are tracked
        assert exc_info.value.attempts == config.max_retries + 1

    @patch("time.sleep")
    def test_non_retryable_error_fails_immediately(self, mock_sleep):
        """Test that non-retryable errors fail immediately without retry."""
        call_count = 0

        @handle_request_errors
        def non_retryable_error():
            nonlocal call_count
            call_count += 1
            response = httpx.Response(404, json={"message": "Not found"})
            raise httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", "http://test"),
                response=response,
            )

        with pytest.raises(OpenGovNotFoundError):
            non_retryable_error()

        # Should only try once (no retries)
        assert call_count == 1
        assert mock_sleep.call_count == 0

    @patch("time.sleep")
    def test_retry_429_with_retry_after(self, mock_sleep):
        """Test that Retry-After header is respected for 429 errors."""
        call_count = 0

        @handle_request_errors
        def rate_limited():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                response = httpx.Response(
                    429,
                    json={"message": "Rate limited"},
                    headers={"retry-after": "5"},
                )
                raise httpx.HTTPStatusError(
                    "Rate limited",
                    request=httpx.Request("GET", "http://test"),
                    response=response,
                )
            return {"success": True}

        result = rate_limited()
        assert result == {"success": True}
        assert call_count == 2
        # Should respect Retry-After header
        mock_sleep.assert_called_once_with(5.0)

    @patch("time.sleep")
    def test_retry_timeout_error(self, mock_sleep):
        """Test that timeout errors are retried."""
        call_count = 0

        @handle_request_errors
        def timeout_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.TimeoutException("Timeout")
            return {"success": True}

        result = timeout_func()
        assert result == {"success": True}
        assert call_count == 3
        assert mock_sleep.call_count == 2

    @patch("time.sleep")
    def test_retry_connection_error(self, mock_sleep):
        """Test that connection errors are retried."""
        call_count = 0

        @handle_request_errors
        def connection_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ConnectError("Connection failed")
            return {"success": True}

        result = connection_func()
        assert result == {"success": True}
        assert call_count == 2
        assert mock_sleep.call_count == 1

    @patch("time.sleep")
    def test_timeout_exhausted_includes_attempts(self, mock_sleep):
        """Test that timeout error includes attempt count when exhausted."""

        @handle_request_errors
        def always_timeout():
            raise httpx.TimeoutException("Timeout")

        with pytest.raises(OpenGovAPITimeoutError) as exc_info:
            always_timeout()

        config = get_retry_config()
        assert exc_info.value.attempts == config.max_retries + 1
        assert "after" in str(exc_info.value)  # Should mention attempts in message

    @patch("time.sleep")
    def test_connection_exhausted_includes_attempts(self, mock_sleep):
        """Test that connection error includes attempt count when exhausted."""

        @handle_request_errors
        def always_fails():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(OpenGovAPIConnectionError) as exc_info:
            always_fails()

        config = get_retry_config()
        assert exc_info.value.attempts == config.max_retries + 1
        assert "after" in str(exc_info.value)  # Should mention attempts in message


class TestConfigurableRetries:
    """Tests for configurable retry settings."""

    @patch("time.sleep")
    def test_custom_max_retries(self, mock_sleep):
        """Test that custom max_retries is respected."""
        import opengov_api

        # Save original config
        original_config = opengov_api.get_retry_config()

        try:
            # Set custom max retries
            opengov_api.configure_retries(max_retries=5)

            call_count = 0

            @handle_request_errors
            def always_fails():
                nonlocal call_count
                call_count += 1
                response = httpx.Response(500, json={"message": "Server error"})
                raise httpx.HTTPStatusError(
                    "Server error",
                    request=httpx.Request("GET", "http://test"),
                    response=response,
                )

            with pytest.raises(OpenGovInternalServerError) as exc_info:
                always_fails()

            # Should try initial + 5 retries = 6 times
            assert call_count == 6
            assert mock_sleep.call_count == 5
            assert exc_info.value.attempts == 6
        finally:
            # Restore original config
            opengov_api.configure_retries(
                max_retries=original_config.max_retries,
                initial_delay=original_config.initial_delay,
                max_delay=original_config.max_delay,
                backoff_multiplier=original_config.backoff_multiplier,
                jitter_factor=original_config.jitter_factor,
            )

    @patch("time.sleep")
    def test_disable_retries(self, mock_sleep):
        """Test that retries can be disabled."""
        import opengov_api

        # Save original config
        original_config = opengov_api.get_retry_config()

        try:
            # Disable retries
            opengov_api.configure_retries(max_retries=0)

            call_count = 0

            @handle_request_errors
            def always_fails():
                nonlocal call_count
                call_count += 1
                response = httpx.Response(500, json={"message": "Server error"})
                raise httpx.HTTPStatusError(
                    "Server error",
                    request=httpx.Request("GET", "http://test"),
                    response=response,
                )

            with pytest.raises(OpenGovInternalServerError) as exc_info:
                always_fails()

            # Should only try once with retries disabled
            assert call_count == 1
            assert mock_sleep.call_count == 0
            assert exc_info.value.attempts == 1
        finally:
            # Restore original config
            opengov_api.configure_retries(
                max_retries=original_config.max_retries,
                initial_delay=original_config.initial_delay,
                max_delay=original_config.max_delay,
                backoff_multiplier=original_config.backoff_multiplier,
                jitter_factor=original_config.jitter_factor,
            )

    @patch("time.sleep")
    def test_custom_backoff_settings(self, mock_sleep):
        """Test that custom backoff settings are used."""
        import opengov_api

        # Save original config
        original_config = opengov_api.get_retry_config()

        try:
            # Set custom backoff: 0.5s initial, 3x multiplier
            opengov_api.configure_retries(
                initial_delay=0.5,
                backoff_multiplier=3.0,
                jitter_factor=0.0,  # No jitter for predictable testing
            )

            call_count = 0

            @handle_request_errors
            def fails_twice():
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    response = httpx.Response(500, json={"message": "Server error"})
                    raise httpx.HTTPStatusError(
                        "Server error",
                        request=httpx.Request("GET", "http://test"),
                        response=response,
                    )
                return {"success": True}

            result = fails_twice()
            assert result == {"success": True}
            assert call_count == 3

            # Check delays: 0.5s, 1.5s (0.5 * 3^1)
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list[0][0][0] == pytest.approx(0.5, abs=0.01)
            assert mock_sleep.call_args_list[1][0][0] == pytest.approx(1.5, abs=0.01)
        finally:
            # Restore original config
            opengov_api.configure_retries(
                max_retries=original_config.max_retries,
                initial_delay=original_config.initial_delay,
                max_delay=original_config.max_delay,
                backoff_multiplier=original_config.backoff_multiplier,
                jitter_factor=original_config.jitter_factor,
            )
