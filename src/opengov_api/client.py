"""
Client factory and configuration for OpenGov API SDK.

Provides module-level configuration management and client factory.
"""

import os
from typing import Optional

import httpx

from .exceptions import OpenGovConfigurationError

# Module-level configuration
_api_key: Optional[str] = os.getenv("OPENGOV_API_KEY")
_base_url: str = "https://api.plce.opengov.com/plce/v2"
_community: Optional[str] = os.getenv("OPENGOV_COMMUNITY")
_timeout: float = 30.0


def set_api_key(key: str) -> None:
    """
    Set the API key for authentication.

    Args:
        key: OpenGov API key

    Example:
        >>> import opengov_api
        >>> opengov_api.set_api_key("your-api-key")
    """
    global _api_key
    _api_key = key


def set_base_url(url: str) -> None:
    """
    Set the base API URL.

    Args:
        url: Base API URL (will be stripped of trailing slashes)

    Example:
        >>> import opengov_api
        >>> opengov_api.set_base_url("https://api.plce.opengov.com/plce/v2")
    """
    global _base_url
    _base_url = url.rstrip("/")


def set_community(community: str) -> None:
    """
    Set the community identifier.

    Args:
        community: Community identifier (e.g., "your-community")

    Example:
        >>> import opengov_api
        >>> opengov_api.set_community("your-community")
    """
    global _community
    _community = community


def set_timeout(timeout: float) -> None:
    """
    Set the request timeout in seconds.

    Args:
        timeout: Timeout in seconds (default: 30.0)

    Example:
        >>> import opengov_api
        >>> opengov_api.set_timeout(60.0)
    """
    global _timeout
    _timeout = timeout


def get_api_key() -> str:
    """
    Get the current API key.

    Returns:
        The configured API key

    Raises:
        OpenGovConfigurationError: If API key is not set
    """
    if not _api_key:
        raise OpenGovConfigurationError(
            "API key not set. Call set_api_key() or set OPENGOV_API_KEY environment variable."
        )
    return _api_key


def get_base_url() -> str:
    """
    Get the current base URL.

    Returns:
        The configured base URL
    """
    return _base_url


def get_community() -> str:
    """
    Get the current community identifier.

    Returns:
        The configured community identifier

    Raises:
        OpenGovConfigurationError: If community is not set
    """
    if not _community:
        raise OpenGovConfigurationError(
            "Community not set. Call set_community() or set OPENGOV_COMMUNITY environment variable."
        )
    return _community


def get_timeout() -> float:
    """
    Get the current timeout setting.

    Returns:
        The configured timeout in seconds
    """
    return _timeout


def _get_client() -> httpx.Client:
    """
    Create configured httpx.Client with authentication and defaults.

    Returns:
        Configured httpx.Client instance

    Raises:
        OpenGovConfigurationError: If API key is not configured
    """
    api_key = get_api_key()  # This will raise if not configured

    return httpx.Client(
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        timeout=_timeout,
    )
