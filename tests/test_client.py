"""Tests for client configuration and factory."""

import os
from unittest.mock import patch

import httpx
import pytest

from opengov_api.client import (
    set_api_key,
    set_base_url,
    set_community,
    set_timeout,
    get_api_key,
    get_base_url,
    get_community,
    get_timeout,
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

    # Reset to None/defaults
    client._api_key = None
    client._base_url = "https://api.plce.opengov.com/plce/v2"
    client._community = None
    client._timeout = 30.0

    yield

    # Restore original values
    client._api_key = original_api_key
    client._base_url = original_base_url
    client._community = original_community
    client._timeout = original_timeout


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
