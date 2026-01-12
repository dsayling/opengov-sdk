"""
Shared pytest fixtures and configuration for all tests.
"""

import pytest
from pytest_httpx import HTTPXMock

import opengov_api


@pytest.fixture(autouse=True)
def block_network_calls(httpx_mock: HTTPXMock):
    """
    Automatically block all network calls in tests.

    This fixture runs automatically for all tests by depending on httpx_mock.
    It ensures that even if a test doesn't explicitly use httpx_mock or set up
    mocks correctly, network calls will be blocked and the test will fail with
    a clear error message instead of making real API calls.

    The httpx_mock fixture (from pytest-httpx) automatically:
    - Intercepts all httpx requests
    - Raises an error if a request is made without a matching mock
    - Prevents tests from making real network calls

    This protects against:
    - Accidental API calls in tests
    - Flaky tests due to network issues
    - Unintended costs or rate limiting
    - Tests passing with incorrect mocks
    """
    # Simply depend on httpx_mock to force it to be active for all tests
    # No additional logic needed - the fixture itself blocks unmocked requests
    pass


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
