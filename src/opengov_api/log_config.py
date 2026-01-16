"""
Logging configuration and utilities for OpenGov API SDK.

This module provides:
- Human-readable log formatting
- Sensitive data sanitization (API keys, auth tokens, PII)
- Helper function to enable logging at desired levels
"""

import logging
import re
from typing import Any


# Fields that should be redacted from logs (common PII and sensitive data)
_SENSITIVE_FIELDS = {
    "password",
    "api_key",
    "apiKey",
    "token",
    "authorization",
    "secret",
    "ssn",
    "social_security_number",
    "credit_card",
    "creditCard",
    "cvv",
    "pin",
}


class OpenGovFormatter(logging.Formatter):
    """
    Human-readable formatter for OpenGov SDK logs.

    Format: YYYY-MM-DD HH:MM:SS LEVEL [logger_name] message
    Example: 2024-01-16 10:30:45 INFO [opengov_api.records] GET /records/123 -> 200 OK
    """

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def sanitize_api_key(api_key: str | None) -> str:
    """
    Sanitize API key to show only the last 4 characters.

    Args:
        api_key: The API key to sanitize

    Returns:
        Sanitized string like "***xyz123" or "None" if api_key is None

    Examples:
        >>> sanitize_api_key("my-secret-api-key-12345")
        "***2345"
        >>> sanitize_api_key(None)
        "None"
    """
    if api_key is None:
        return "None"

    if len(api_key) <= 4:
        return "***"

    return f"***{api_key[-4:]}"


def sanitize_auth_header(header_value: str) -> str:
    """
    Sanitize authorization header to hide sensitive tokens.

    Args:
        header_value: The authorization header value

    Returns:
        Sanitized string like "Token ***xyz123" or "Bearer ***xyz123"

    Examples:
        >>> sanitize_auth_header("Token my-secret-token-12345")
        "Token ***2345"
        >>> sanitize_auth_header("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        "Bearer ***VCJ9"
    """
    # Match patterns like "Token <value>" or "Bearer <value>"
    match = re.match(r"^(Token|Bearer)\s+(.+)$", header_value, re.IGNORECASE)

    if match:
        auth_type = match.group(1)
        token = match.group(2)
        return f"{auth_type} {sanitize_api_key(token)}"

    # Fallback: just sanitize the whole value
    return sanitize_api_key(header_value)


def sanitize_dict(data: dict[str, Any], max_depth: int = 5) -> dict[str, Any]:
    """
    Recursively sanitize a dictionary by redacting sensitive fields.

    Args:
        data: Dictionary to sanitize
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Sanitized dictionary with sensitive fields redacted

    Examples:
        >>> sanitize_dict({"email": "user@example.com", "password": "secret123"})
        {"email": "user@example.com", "password": "***REDACTED***"}
    """
    if max_depth <= 0:
        return data

    if not isinstance(data, dict):
        return data

    sanitized = {}

    for key, value in data.items():
        # Check if this field should be redacted
        if key.lower() in _SENSITIVE_FIELDS or "password" in key.lower():
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            # Sanitize lists of dictionaries
            sanitized[key] = [
                sanitize_dict(item, max_depth - 1) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Sanitize HTTP headers to redact authorization tokens.

    Args:
        headers: Dictionary of HTTP headers

    Returns:
        Sanitized headers dictionary

    Examples:
        >>> sanitize_headers({"Authorization": "Token secret123", "Content-Type": "application/json"})
        {"Authorization": "Token ***t123", "Content-Type": "application/json"}
    """
    sanitized = {}

    for key, value in headers.items():
        if key.lower() in ("authorization", "x-api-key", "api-key"):
            sanitized[key] = sanitize_auth_header(value)
        else:
            sanitized[key] = value

    return sanitized


def enable_logging(level: str | int = logging.INFO) -> None:
    """
    Enable logging for the OpenGov SDK at the specified level.

    This configures all loggers under 'opengov_api' with a human-readable
    formatter and sets the logging level. Call this once at the start of
    your application to see SDK logs.

    Args:
        level: Logging level (can be string like 'INFO', 'DEBUG' or int constant)
               Defaults to INFO.

    Levels:
        - DEBUG: Detailed information including request/response bodies
        - INFO: General informational messages (requests, config changes)
        - WARNING: Warning messages (retries, deprecations)
        - ERROR: Error messages only

    Examples:
        >>> import opengov_api
        >>> opengov_api.enable_logging('INFO')  # Show INFO and above
        >>> opengov_api.enable_logging('DEBUG')  # Show everything
        >>> opengov_api.enable_logging(logging.WARNING)  # Warnings and errors only

    Note:
        - Request/response JSON bodies are only logged at DEBUG level
        - Sensitive data (API keys, passwords) are automatically redacted
        - This affects all loggers under the 'opengov_api' namespace
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Get the root logger for opengov_api
    logger = logging.getLogger("opengov_api")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with our formatter
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(OpenGovFormatter())

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False
