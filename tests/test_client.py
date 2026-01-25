"""Tests for client configuration and factory."""

import os
from unittest.mock import patch

import httpx
import pytest

from opengov_api.client import (
    RetryConfig,
    set_api_key,
    set_base_url,
    set_community,
    set_timeout,
    set_auth_scheme,
    configure_retries,
    get_api_key,
    get_base_url,
    get_community,
    get_timeout,
    get_auth_scheme,
    get_retry_config,
    _get_client,
)
from opengov_api.exceptions import OpenGovConfigurationError


@pytest.fixture(autouse=True)
def reset_config():
    """Reset module-level configuration before each test."""
    # Store original values
    from opengov_api import client

    original_api_key = client._api_key
    original_base_url = client._base_url
    original_community = client._community
    original_timeout = client._timeout
    original_retry_config = client._retry_config
    original_auth_scheme = client._auth_scheme

    # Reset to None/defaults
    client._api_key = None
    client._base_url = "https://api.plce.opengov.com/plce/v2"
    client._community = None
    client._timeout = 30.0
    client._retry_config = RetryConfig()
    client._auth_scheme = "token"

    yield

    # Restore original values
    client._api_key = original_api_key
    client._base_url = original_base_url
    client._community = original_community
    client._timeout = original_timeout
    client._retry_config = original_retry_config
    client._auth_scheme = original_auth_scheme


class TestConfiguration:
    """Tests for configuration setters and getters."""

    def test_set_and_get_api_key(self):
        """Test setting and getting API key."""
        set_api_key("test-api-key")
        assert get_api_key() == "test-api-key"

    def test_get_api_key_not_set(self):
        """Test getting API key when not set raises error."""
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            get_api_key()
        assert "API key not set" in str(exc_info.value)

    def test_set_and_get_base_url(self):
        """Test setting and getting base URL."""
        set_base_url("https://custom.api.com/v1")
        assert get_base_url() == "https://custom.api.com/v1"

    def test_set_base_url_strips_trailing_slash(self):
        """Test base URL strips trailing slash."""
        set_base_url("https://custom.api.com/v1/")
        assert get_base_url() == "https://custom.api.com/v1"

    def test_get_base_url_default(self):
        """Test getting default base URL."""
        assert get_base_url() == "https://api.plce.opengov.com/plce/v2"

    def test_set_and_get_community(self):
        """Test setting and getting community."""
        set_community("testcommunity")
        assert get_community() == "testcommunity"

    def test_get_community_not_set(self):
        """Test getting community when not set raises error."""
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            get_community()
        assert "Community not set" in str(exc_info.value)

    def test_set_and_get_timeout(self):
        """Test setting and getting timeout."""
        set_timeout(60.0)
        assert get_timeout() == 60.0

    def test_get_timeout_default(self):
        """Test getting default timeout."""
        assert get_timeout() == 30.0

    def test_set_and_get_auth_scheme(self):
        """Test setting and getting auth scheme."""
        set_auth_scheme("bearer")
        assert get_auth_scheme() == "bearer"

    def test_get_auth_scheme_default(self):
        """Test getting default auth scheme."""
        assert get_auth_scheme() == "token"


class TestEnvironmentVariables:
    """Tests for environment variable initialization."""

    @patch.dict(os.environ, {"OPENGOV_API_KEY": "env-api-key"})
    def test_api_key_from_environment(self):
        """Test API key is loaded from environment variable."""
        # Re-import to trigger module initialization
        from importlib import reload
        from opengov_api import client

        reload(client)
        assert client._api_key == "env-api-key"

    @patch.dict(os.environ, {"OPENGOV_COMMUNITY": "env-community"})
    def test_community_from_environment(self):
        """Test community is loaded from environment variable."""
        from importlib import reload
        from opengov_api import client

        reload(client)
        assert client._community == "env-community"

    @patch.dict(os.environ, {}, clear=True)
    def test_no_environment_variables(self):
        """Test module works without environment variables."""
        from importlib import reload
        from opengov_api import client

        reload(client)
        assert client._api_key is None
        assert client._community is None


class TestGetClient:
    """Tests for _get_client factory function."""

    def test_get_client_requires_api_key(self):
        """Test _get_client raises error when API key not set."""
        with pytest.raises(OpenGovConfigurationError):
            _get_client()

    def test_get_client_creates_client_with_auth(self):
        """Test _get_client creates httpx.Client with auth header."""
        set_api_key("test-key")
        client = _get_client()
        assert isinstance(client, httpx.Client)
        assert client.headers["Authorization"] == "Token test-key"
        assert client.headers["Content-Type"] == "application/json"
        client.close()

    def test_get_client_uses_timeout(self):
        """Test _get_client respects timeout setting."""
        set_api_key("test-key")
        set_timeout(45.0)
        client = _get_client()
        # httpx.Client.timeout is a Timeout object, not a float
        assert (
            client.timeout.connect == 45.0
            or str(client.timeout) == "Timeout(timeout=45.0)"
        )
        client.close()

    def test_get_client_context_manager(self):
        """Test _get_client can be used as context manager."""
        set_api_key("test-key")
        with _get_client() as client:
            assert isinstance(client, httpx.Client)
            assert not client.is_closed
        # Client should be closed after context
        assert client.is_closed

    def test_get_client_creates_new_instance(self):
        """Test _get_client creates new client instance each time."""
        set_api_key("test-key")
        client1 = _get_client()
        client2 = _get_client()
        assert client1 is not client2
        client1.close()
        client2.close()

    def test_get_client_updates_with_new_api_key(self):
        """Test _get_client uses updated API key."""
        set_api_key("first-key")
        client1 = _get_client()
        assert client1.headers["Authorization"] == "Token first-key"
        client1.close()

        set_api_key("second-key")
        client2 = _get_client()
        assert client2.headers["Authorization"] == "Token second-key"
        client2.close()

    def test_get_client_uses_token_scheme_by_default(self):
        """Test _get_client uses Token prefix by default."""
        set_api_key("test-key")
        client = _get_client()
        assert client.headers["Authorization"] == "Token test-key"
        client.close()

    def test_get_client_uses_bearer_scheme(self):
        """Test _get_client uses Bearer prefix when scheme is bearer."""
        set_api_key("test-key")
        set_auth_scheme("bearer")
        client = _get_client()
        assert client.headers["Authorization"] == "Bearer test-key"
        client.close()

    def test_get_client_switches_auth_scheme(self):
        """Test _get_client updates auth header when scheme changes."""
        set_api_key("test-key")

        # Default is token
        client1 = _get_client()
        assert client1.headers["Authorization"] == "Token test-key"
        client1.close()

        # Switch to bearer
        set_auth_scheme("bearer")
        client2 = _get_client()
        assert client2.headers["Authorization"] == "Bearer test-key"
        client2.close()

        # Switch back to token
        set_auth_scheme("token")
        client3 = _get_client()
        assert client3.headers["Authorization"] == "Token test-key"
        client3.close()


class TestRetryConfiguration:
    """Tests for retry configuration."""

    def test_default_retry_config(self):
        """Test default retry configuration."""
        config = get_retry_config()
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.jitter_factor == 0.1

    def test_configure_max_retries(self):
        """Test configuring max retries."""
        configure_retries(max_retries=5)
        config = get_retry_config()
        assert config.max_retries == 5
        # Other settings unchanged
        assert config.initial_delay == 1.0

    def test_configure_initial_delay(self):
        """Test configuring initial delay."""
        configure_retries(initial_delay=2.5)
        config = get_retry_config()
        assert config.initial_delay == 2.5
        # Other settings unchanged
        assert config.max_retries == 3

    def test_configure_max_delay(self):
        """Test configuring max delay."""
        configure_retries(max_delay=120.0)
        config = get_retry_config()
        assert config.max_delay == 120.0

    def test_configure_backoff_multiplier(self):
        """Test configuring backoff multiplier."""
        configure_retries(backoff_multiplier=3.0)
        config = get_retry_config()
        assert config.backoff_multiplier == 3.0

    def test_configure_jitter_factor(self):
        """Test configuring jitter factor."""
        configure_retries(jitter_factor=0.2)
        config = get_retry_config()
        assert config.jitter_factor == 0.2

    def test_configure_multiple_settings(self):
        """Test configuring multiple settings at once."""
        configure_retries(
            max_retries=10,
            initial_delay=0.5,
            max_delay=30.0,
            backoff_multiplier=1.5,
            jitter_factor=0.05,
        )
        config = get_retry_config()
        assert config.max_retries == 10
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.backoff_multiplier == 1.5
        assert config.jitter_factor == 0.05

    def test_disable_retries(self):
        """Test disabling retries."""
        configure_retries(max_retries=0)
        config = get_retry_config()
        assert config.max_retries == 0
