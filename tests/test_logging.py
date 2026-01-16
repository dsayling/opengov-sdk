"""
Tests for logging configuration and sanitization.
"""

import logging

from opengov_api.log_config import (
    sanitize_api_key,
    sanitize_auth_header,
    sanitize_dict,
    sanitize_headers,
    enable_logging,
    OpenGovFormatter,
)


class TestSanitizeApiKey:
    """Tests for sanitize_api_key function."""

    def test_sanitize_long_key(self):
        """Long API keys show last 4 characters."""
        result = sanitize_api_key("my-super-secret-api-key-123456")
        assert result == "***3456"

    def test_sanitize_short_key(self):
        """Short keys are completely redacted."""
        result = sanitize_api_key("abc")
        assert result == "***"

    def test_sanitize_four_char_key(self):
        """Four character keys are completely redacted."""
        result = sanitize_api_key("abcd")
        assert result == "***"

    def test_sanitize_five_char_key(self):
        """Five character keys show last 4."""
        result = sanitize_api_key("abcde")
        assert result == "***bcde"

    def test_sanitize_none(self):
        """None returns 'None' string."""
        result = sanitize_api_key(None)
        assert result == "None"

    def test_sanitize_empty_string(self):
        """Empty string is completely redacted."""
        result = sanitize_api_key("")
        assert result == "***"


class TestSanitizeAuthHeader:
    """Tests for sanitize_auth_header function."""

    def test_sanitize_token_header(self):
        """Token auth headers are sanitized."""
        result = sanitize_auth_header("Token my-secret-token-12345")
        assert result == "Token ***2345"

    def test_sanitize_bearer_header(self):
        """Bearer auth headers are sanitized."""
        result = sanitize_auth_header("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert result == "Bearer ***VCJ9"

    def test_sanitize_case_insensitive(self):
        """Auth type is case insensitive."""
        result = sanitize_auth_header("token my-secret-123")
        assert result == "token ***-123"

    def test_sanitize_bearer_case_insensitive(self):
        """Bearer is case insensitive."""
        result = sanitize_auth_header("BEARER secret-xyz")
        assert result == "BEARER ***-xyz"

    def test_sanitize_plain_value(self):
        """Plain values without scheme are sanitized."""
        result = sanitize_auth_header("plain-secret-value-789")
        assert result == "***-789"


class TestSanitizeDict:
    """Tests for sanitize_dict function."""

    def test_sanitize_password_field(self):
        """Password fields are redacted."""
        data = {"username": "john", "password": "secret123"}
        result = sanitize_dict(data)
        assert result == {"username": "john", "password": "***REDACTED***"}

    def test_sanitize_api_key_field(self):
        """API key fields are redacted."""
        data = {"name": "test", "api_key": "sk_live_123456"}
        result = sanitize_dict(data)
        assert result == {"name": "test", "api_key": "***REDACTED***"}

    def test_sanitize_multiple_sensitive_fields(self):
        """Multiple sensitive fields are redacted."""
        data = {
            "email": "user@example.com",
            "password": "secret123",
            "token": "abc-xyz",
            "api_key": "key123",
        }
        result = sanitize_dict(data)
        assert result == {
            "email": "user@example.com",
            "password": "***REDACTED***",
            "token": "***REDACTED***",
            "api_key": "***REDACTED***",
        }

    def test_sanitize_nested_dict(self):
        """Nested dictionaries are sanitized recursively."""
        data = {
            "user": {
                "name": "John",
                "credentials": {"password": "secret123", "api_key": "key-xyz"},
            }
        }
        result = sanitize_dict(data)
        assert result == {
            "user": {
                "name": "John",
                "credentials": {
                    "password": "***REDACTED***",
                    "api_key": "***REDACTED***",
                },
            }
        }

    def test_sanitize_list_of_dicts(self):
        """Lists containing dictionaries are sanitized."""
        data = {
            "users": [
                {"name": "John", "password": "secret1"},
                {"name": "Jane", "password": "secret2"},
            ]
        }
        result = sanitize_dict(data)
        assert result == {
            "users": [
                {"name": "John", "password": "***REDACTED***"},
                {"name": "Jane", "password": "***REDACTED***"},
            ]
        }

    def test_sanitize_preserves_non_sensitive_fields(self):
        """Non-sensitive fields are preserved."""
        data = {
            "id": 123,
            "name": "Test User",
            "email": "user@example.com",
            "created_at": "2024-01-01",
        }
        result = sanitize_dict(data)
        assert result == data

    def test_sanitize_ssn_field(self):
        """SSN fields are redacted."""
        data = {"name": "John", "ssn": "123-45-6789"}
        result = sanitize_dict(data)
        assert result == {"name": "John", "ssn": "***REDACTED***"}

    def test_sanitize_credit_card_field(self):
        """Credit card fields are redacted."""
        data = {"name": "John", "credit_card": "4111-1111-1111-1111"}
        result = sanitize_dict(data)
        assert result == {"name": "John", "credit_card": "***REDACTED***"}

    def test_sanitize_case_insensitive_field_names(self):
        """Field name matching is case insensitive."""
        data = {"Password": "secret1", "API_KEY": "key123", "Token": "token-xyz"}
        result = sanitize_dict(data)
        assert result == {
            "Password": "***REDACTED***",
            "API_KEY": "***REDACTED***",
            "Token": "***REDACTED***",
        }

    def test_sanitize_max_depth(self):
        """Maximum recursion depth prevents infinite loops."""
        # Create deeply nested structure
        data = {
            "level1": {
                "level2": {"level3": {"level4": {"level5": {"password": "secret"}}}}
            }
        }
        result = sanitize_dict(data, max_depth=3)
        # After max_depth, inner dicts are not sanitized
        assert (
            result["level1"]["level2"]["level3"]["level4"]["level5"]["password"]
            == "secret"
        )

    def test_sanitize_empty_dict(self):
        """Empty dict returns empty dict."""
        result = sanitize_dict({})
        assert result == {}


class TestSanitizeHeaders:
    """Tests for sanitize_headers function."""

    def test_sanitize_authorization_header(self):
        """Authorization headers are sanitized."""
        headers = {
            "Authorization": "Token my-secret-token-12345",
            "Content-Type": "application/json",
        }
        result = sanitize_headers(headers)
        assert result == {
            "Authorization": "Token ***2345",
            "Content-Type": "application/json",
        }

    def test_sanitize_api_key_header(self):
        """X-API-Key headers are sanitized."""
        headers = {
            "X-API-Key": "secret-key-xyz789",
            "Accept": "application/json",
        }
        result = sanitize_headers(headers)
        assert result == {
            "X-API-Key": "***z789",
            "Accept": "application/json",
        }

    def test_sanitize_case_insensitive_headers(self):
        """Header name matching is case insensitive."""
        headers = {
            "authorization": "Bearer token123",
            "x-api-key": "key456",
        }
        result = sanitize_headers(headers)
        assert result["authorization"] == "Bearer ***n123"
        assert result["x-api-key"] == "***y456"

    def test_sanitize_preserves_non_sensitive_headers(self):
        """Non-sensitive headers are preserved."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "OpenGov-SDK/1.0",
        }
        result = sanitize_headers(headers)
        assert result == headers

    def test_sanitize_empty_headers(self):
        """Empty headers dict returns empty dict."""
        result = sanitize_headers({})
        assert result == {}


class TestOpenGovFormatter:
    """Tests for OpenGovFormatter class."""

    def test_formatter_creates_correct_format(self):
        """Formatter produces expected format."""
        formatter = OpenGovFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="opengov_api.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Should contain timestamp, level, logger name, and message
        assert "[opengov_api.test]" in formatted
        assert "Test message" in formatted
        assert "INFO" in formatted

    def test_formatter_handles_different_levels(self):
        """Formatter handles all log levels."""
        formatter = OpenGovFormatter()

        for level_name, level_value in [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
        ]:
            record = logging.LogRecord(
                name="opengov_api.test",
                level=level_value,
                pathname="test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            formatted = formatter.format(record)
            assert level_name in formatted


class TestEnableLogging:
    """Tests for enable_logging function."""

    def teardown_method(self):
        """Clean up loggers after each test."""
        logger = logging.getLogger("opengov_api")
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)

    def test_enable_logging_info_level(self):
        """Enabling at INFO level sets correct level."""
        enable_logging("INFO")

        logger = logging.getLogger("opengov_api")
        assert logger.level == logging.INFO

    def test_enable_logging_debug_level(self):
        """Enabling at DEBUG level sets correct level."""
        enable_logging("DEBUG")

        logger = logging.getLogger("opengov_api")
        assert logger.level == logging.DEBUG

    def test_enable_logging_warning_level(self):
        """Enabling at WARNING level sets correct level."""
        enable_logging("WARNING")

        logger = logging.getLogger("opengov_api")
        assert logger.level == logging.WARNING

    def test_enable_logging_with_int_level(self):
        """Enabling with integer level works."""
        enable_logging(logging.INFO)

        logger = logging.getLogger("opengov_api")
        assert logger.level == logging.INFO

    def test_enable_logging_adds_handler(self):
        """Enabling logging adds a handler."""
        enable_logging("INFO")

        logger = logging.getLogger("opengov_api")
        assert len(logger.handlers) == 1

    def test_enable_logging_uses_correct_formatter(self):
        """Handler uses OpenGovFormatter."""
        enable_logging("INFO")

        logger = logging.getLogger("opengov_api")
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, OpenGovFormatter)

    def test_enable_logging_prevents_propagation(self):
        """Logger propagate is set to False."""
        enable_logging("INFO")

        logger = logging.getLogger("opengov_api")
        assert logger.propagate is False

    def test_enable_logging_clears_existing_handlers(self):
        """Calling enable_logging multiple times clears old handlers."""
        enable_logging("INFO")
        enable_logging("DEBUG")

        logger = logging.getLogger("opengov_api")
        # Should have only 1 handler (old one cleared)
        assert len(logger.handlers) == 1


class TestLoggingIntegration:
    """Integration tests for logging in actual SDK usage."""

    def setup_method(self):
        """Set up logging for each test."""
        enable_logging("DEBUG")

        # Capture log output
        self.log_capture = []

        class ListHandler(logging.Handler):
            def __init__(self, log_list):
                super().__init__()
                self.log_list = log_list

            def emit(self, record):
                self.log_list.append(self.format(record))

        logger = logging.getLogger("opengov_api")
        self.handler = ListHandler(self.log_capture)
        self.handler.setFormatter(OpenGovFormatter())
        logger.addHandler(self.handler)

    def teardown_method(self):
        """Clean up logging after each test."""
        logger = logging.getLogger("opengov_api")
        logger.removeHandler(self.handler)
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)

    def test_client_config_logging(self, reset_config):
        """Configuration changes are logged."""
        import opengov_api

        opengov_api.set_api_key("test-api-key-123456")

        # Check logs contain sanitized API key
        logs = "\n".join(self.log_capture)
        assert "API key configured" in logs
        assert "***3456" in logs
        assert "test-api-key-123456" not in logs

    def test_community_config_logging(self, reset_config):
        """Community configuration is logged."""
        import opengov_api

        opengov_api.set_community("testcommunity")

        logs = "\n".join(self.log_capture)
        assert "Community configured: testcommunity" in logs

    def test_timeout_config_logging(self, reset_config):
        """Timeout configuration is logged."""
        import opengov_api

        opengov_api.set_timeout(60.0)

        logs = "\n".join(self.log_capture)
        assert "Timeout configured: 60.0s" in logs

    def test_retry_config_logging(self, reset_config):
        """Retry configuration is logged."""
        import opengov_api

        opengov_api.configure_retries(max_retries=5, initial_delay=2.0)

        logs = "\n".join(self.log_capture)
        assert "Retry config updated" in logs
        assert "max_retries=5" in logs
        assert "initial_delay=2.0s" in logs

    def test_url_building_logging(self):
        """URL building is logged at DEBUG level."""
        from opengov_api.base import build_url

        build_url("https://api.example.com/v2", "testcommunity", "records")

        logs = "\n".join(self.log_capture)
        assert "Built URL: https://api.example.com/v2/testcommunity/records" in logs

    def test_error_logging_sanitizes_response(self):
        """Error responses have sensitive data sanitized."""
        import httpx
        from opengov_api.base import make_status_error

        # Create mock response
        response = httpx.Response(
            status_code=401,
            json={"error": "Invalid credentials", "api_key": "secret-key-123"},
        )

        make_status_error(response)

        logs = "\n".join(self.log_capture)
        assert "HTTP 401 error" in logs
        # API key should be redacted in debug logs
        assert "***REDACTED***" in logs or "secret-key-123" not in logs
