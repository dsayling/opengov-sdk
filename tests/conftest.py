"""
Shared pytest fixtures and configuration for all tests.
"""

import pytest
import opengov_api


@pytest.fixture(autouse=True)
def reset_config():
    """
    Reset module-level configuration before each test.

    This fixture runs automatically for all tests to ensure
    test isolation and prevent state leakage.
    """
    from opengov_api import client

    # Store original values
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


@pytest.fixture
def configure_client():
    """
    Configure client with test credentials.

    Use this fixture when you need a properly configured client
    for testing API calls.
    """
    opengov_api.set_api_key("test-api-key")
    opengov_api.set_community("testcommunity")
