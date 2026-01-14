"""
Shared pytest fixtures and configuration for all tests.
"""

import pytest
from pytest_httpx import HTTPXMock
from unittest.mock import patch

import opengov_api


@pytest.fixture(autouse=True)
def mock_sleep():
    """
    Automatically mock time.sleep to prevent actual sleeping during retries.

    This fixture runs automatically for all tests to ensure tests run quickly
    even when retry logic is triggered. Without this, tests with retries would
    sleep for actual delays (1s, 2s, 4s, etc.).
    """
    with patch("time.sleep"):
        yield


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


@pytest.fixture
def test_base_url():
    """
    Provide the base URL used in tests.

    Using example.com makes it clear these are test URLs
    and not real API endpoints.
    """
    return "https://api.example.com/v2"


@pytest.fixture
def build_url(test_base_url):
    """
    Build a test URL from a path.

    Example:
        build_url("/testcommunity/records")
        -> "https://api.example.com/v2/testcommunity/records"
    """

    def _build(path: str) -> str:
        # Remove leading slash if present to avoid double slashes
        path = path.lstrip("/")
        return f"{test_base_url}/{path}"

    return _build


@pytest.fixture
def mock_url_with_params():
    """
    Create a regex pattern that matches a URL with any query parameters.

    This is useful for mocking endpoints that accept pagination or other query params.

    Example:
        pattern = mock_url_with_params(build_url("testcommunity/records"))
        httpx_mock.add_response(url=pattern, json={"data": []})
        # Matches both /records and /records?page[number]=1&page[size]=20
    """
    import re

    def _pattern(url: str):
        return re.compile(re.escape(url) + r"(\?.*)?$")

    return _pattern


@pytest.fixture
def assert_request_method(httpx_mock: HTTPXMock):
    """
    Assert that the most recent request used the expected HTTP method.

    Example:
        assert_request_method("POST")
        assert_request_method("PATCH")
    """

    def _assert(expected_method: str):
        request = httpx_mock.get_request()
        assert request is not None, "No request was made"
        assert request.method == expected_method, (
            f"Expected {expected_method}, got {request.method}"
        )

    return _assert


@pytest.fixture(autouse=True)
def reset_config(test_base_url):
    """
    Reset module-level configuration before each test.

    This fixture runs automatically for all tests to ensure
    test isolation and prevent state leakage.
    """
    from opengov_api import client
    from opengov_api.client import RetryConfig

    # Store original values
    original_api_key = client._api_key
    original_base_url = client._base_url
    original_community = client._community
    original_timeout = client._timeout
    original_retry_config = client._retry_config

    # Reset to None/defaults
    client._api_key = None
    client._base_url = test_base_url
    client._community = None
    client._timeout = 30.0
    client._retry_config = RetryConfig()  # Reset to default

    yield

    # Restore original values
    client._api_key = original_api_key
    client._base_url = original_base_url
    client._community = original_community
    client._timeout = original_timeout
    client._retry_config = original_retry_config


@pytest.fixture
def configure_client():
    """
    Configure client with test credentials.

    Use this fixture when you need a properly configured client
    for testing API calls.
    """
    opengov_api.set_api_key("test-api-key")
    opengov_api.set_community("testcommunity")
