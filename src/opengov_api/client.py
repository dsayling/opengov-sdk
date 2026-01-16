"""
Client factory and configuration for OpenGov API SDK.

Provides module-level configuration management and client factory.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

from .exceptions import OpenGovConfigurationError
from .log_config import sanitize_api_key

_log = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """
    Configuration for automatic retry with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        backoff_multiplier: Exponential backoff multiplier (default: 2.0)
        jitter_factor: Random jitter as fraction of delay, 0-1 (default: 0.1 = 10%)
    """

    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1


# Module-level configuration
_api_key: Optional[str] = os.getenv("OPENGOV_API_KEY")
_base_url: str = "https://api.plce.opengov.com/plce/v2"
_community: Optional[str] = os.getenv("OPENGOV_COMMUNITY")
_timeout: float = 30.0
_retry_config: RetryConfig = RetryConfig()


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
    _log.info(f"API key configured: {sanitize_api_key(key)}")


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
    _log.info(f"Base URL configured: {_base_url}")


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
    _log.info(f"Community configured: {_community}")


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
    _log.info(f"Timeout configured: {_timeout}s")


def configure_retries(
    max_retries: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    backoff_multiplier: Optional[float] = None,
    jitter_factor: Optional[float] = None,
) -> None:
    """
    Configure automatic retry behavior for transient errors.

    Retries are automatically applied to:
    - 429 Rate Limit errors (respects Retry-After header)
    - 500+ Server errors
    - Timeout errors
    - Connection/Network errors

    Non-retryable errors (400, 401, 403, 404) fail immediately.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        backoff_multiplier: Exponential backoff multiplier (default: 2.0)
        jitter_factor: Random jitter as fraction of delay, 0-1 (default: 0.1)

    Example:
        >>> import opengov_api
        >>> # Increase max retries and initial delay
        >>> opengov_api.configure_retries(max_retries=5, initial_delay=2.0)
        >>>
        >>> # Disable retries
        >>> opengov_api.configure_retries(max_retries=0)
    """
    global _retry_config

    # Update only the specified fields
    if max_retries is not None:
        _retry_config.max_retries = max_retries
    if initial_delay is not None:
        _retry_config.initial_delay = initial_delay
    if max_delay is not None:
        _retry_config.max_delay = max_delay
    if backoff_multiplier is not None:
        _retry_config.backoff_multiplier = backoff_multiplier
    if jitter_factor is not None:
        _retry_config.jitter_factor = jitter_factor

    _log.info(
        f"Retry config updated: max_retries={_retry_config.max_retries}, "
        f"initial_delay={_retry_config.initial_delay}s, "
        f"max_delay={_retry_config.max_delay}s"
    )


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


def get_retry_config() -> RetryConfig:
    """
    Get the current retry configuration.

    Returns:
        The configured RetryConfig instance
    """
    return _retry_config


def _get_client() -> httpx.Client:
    """
    Create configured httpx.Client with authentication and defaults.

    Returns:
        Configured httpx.Client instance

    Raises:
        OpenGovConfigurationError: If API key is not configured
    """
    api_key = get_api_key()  # This will raise if not configured

    _log.debug(
        f"Creating HTTP client: auth={sanitize_api_key(api_key)}, timeout={_timeout}s"
    )

    return httpx.Client(
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        timeout=_timeout,
    )
