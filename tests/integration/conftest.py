"""
Integration test fixtures and configuration.

These tests run against a Prism mock server that implements the OpenAPI specification.
The server must be running before tests start (fail fast approach).

To start the mock server:
    ./scripts/start-mock-server.sh --daemon

To stop the mock server:
    ./scripts/start-mock-server.sh --stop

Configuration:
- Per-test timeout: 15 seconds (prevents hanging tests)
- HTTP timeout: 5 seconds (fail fast on network issues)
- Retries: Disabled (integration tests should fail immediately)
"""

import os
from typing import Generator
from unittest.mock import MagicMock

import httpx
import pytest

import opengov_api


# Override httpx_mock fixture from parent conftest to allow real HTTP requests
@pytest.fixture
def httpx_mock() -> Generator[MagicMock, None, None]:
    """
    Override httpx_mock to allow real HTTP requests in integration tests.

    The parent conftest.py uses httpx_mock with autouse=True to block all
    network calls in unit tests. For integration tests, we want to make
    real HTTP calls to the mock server, so we override the fixture.
    """
    # Return a mock that won't interfere with real HTTP calls
    mock = MagicMock()
    yield mock


# Override block_network_calls to be a no-op for integration tests
@pytest.fixture(autouse=True)
def block_network_calls(httpx_mock: MagicMock) -> None:
    """
    Override block_network_calls to allow real HTTP requests.

    This is the inverse of the parent conftest's block_network_calls fixture.
    Integration tests need to make real HTTP requests to the mock server.
    """
    pass


# Override mock_sleep from parent conftest since we don't have retries here
@pytest.fixture(autouse=True)
def mock_sleep() -> Generator[None, None, None]:
    """Override mock_sleep to be a no-op for integration tests."""
    yield


# Override reset_config from parent conftest
@pytest.fixture(autouse=True)
def reset_config() -> Generator[None, None, None]:
    """Override reset_config - we handle config in configure_client_for_integration."""
    yield


# Mock server configuration
MOCK_SERVER_HOST = os.environ.get("MOCK_SERVER_HOST", "localhost")
MOCK_SERVER_PORT = os.environ.get("MOCK_SERVER_PORT", "4010")
MOCK_SERVER_BASE_URL = f"http://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}/v2"

# Test community - Prism accepts any value but we use a consistent one
TEST_COMMUNITY = "testcommunity"


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers and configure timeouts for integration tests."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require mock server)"
    )
    # Set timeout for integration tests to 15 seconds per test
    # This allows enough time for network calls but prevents hanging
    config.option.timeout = 15


@pytest.fixture(scope="session", autouse=True)
def verify_mock_server_running() -> None:
    """
    Verify the mock server is running before any tests execute.

    This fixture runs once at the start of the test session and fails fast
    if the mock server is not available. This prevents wasting time running
    tests that will all fail due to connection errors.
    """
    health_check_url = f"http://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}"

    try:
        response = httpx.get(health_check_url, timeout=5.0)
        # Prism returns 200 on root path
        if response.status_code not in (200, 404):
            pytest.fail(
                f"Mock server returned unexpected status: {response.status_code}\n"
                f"URL: {health_check_url}\n"
                "Ensure the mock server is running: ./scripts/start-mock-server.sh --daemon"
            )
    except httpx.ConnectError:
        pytest.fail(
            f"Cannot connect to mock server at {health_check_url}\n"
            "Please start the mock server first:\n"
            "  ./scripts/start-mock-server.sh --daemon"
        )
    except httpx.TimeoutException:
        pytest.fail(
            f"Mock server at {health_check_url} timed out\n"
            "The server may be starting up. Try again in a few seconds."
        )


@pytest.fixture(scope="session")
def mock_server_url() -> str:
    """Return the base URL for the mock server."""
    return MOCK_SERVER_BASE_URL


@pytest.fixture(scope="session")
def test_community() -> str:
    """Return the test community name."""
    return TEST_COMMUNITY


@pytest.fixture(autouse=True)
def configure_client_for_integration(
    mock_server_url: str, test_community: str
) -> Generator[None, None, None]:
    """
    Configure the SDK client to use the mock server.

    This fixture runs before each test and configures the SDK to point
    to the mock server instead of the real API.
    """
    # Store original values
    from opengov_api import client
    from opengov_api.client import RetryConfig

    original_api_key = client._api_key
    original_base_url = client._base_url
    original_community = client._community
    original_timeout = client._timeout
    original_auth_scheme = client._auth_scheme
    original_retry_config = client._retry_config

    # Configure for mock server
    # Use a test API key - Prism doesn't validate auth by default
    opengov_api.set_api_key("test-integration-key")
    opengov_api.set_base_url(mock_server_url)
    opengov_api.set_community(test_community)
    opengov_api.set_timeout(5.0)  # Shorter timeout for integration tests
    opengov_api.set_auth_scheme("bearer")  # Use spec-compliant auth for Prism

    # Disable retries for integration tests to avoid long waits
    # Integration tests should fail fast since mock server responses are predictable
    client._retry_config = RetryConfig(
        max_retries=0,  # No retries - fail fast
        initial_delay=0.0,
        max_delay=0.0,
        backoff_multiplier=1.0,
        jitter_factor=0.0,
    )

    yield

    # Restore original values
    client._api_key = original_api_key
    client._base_url = original_base_url
    client._community = original_community
    client._timeout = original_timeout
    client._auth_scheme = original_auth_scheme
    client._retry_config = original_retry_config


# Test data IDs - Prism generates responses based on OpenAPI examples
# These IDs are used consistently across tests


@pytest.fixture
def record_id() -> str:
    """A valid record ID for testing."""
    return "rec-123"


@pytest.fixture
def record_type_id() -> str:
    """A valid record type ID for testing."""
    return "rt-456"


@pytest.fixture
def user_id() -> str:
    """A valid user ID for testing."""
    return "user-789"


@pytest.fixture
def location_id() -> str:
    """A valid location ID for testing."""
    return "loc-101"


@pytest.fixture
def file_id() -> str:
    """A valid file ID for testing."""
    return "file-202"


@pytest.fixture
def project_id() -> str:
    """A valid project ID for testing."""
    return "proj-303"


@pytest.fixture
def step_id() -> str:
    """A valid workflow step ID for testing."""
    return "step-404"


@pytest.fixture
def comment_id() -> str:
    """A valid comment ID for testing."""
    return "comment-505"


@pytest.fixture
def collection_id() -> str:
    """A valid collection ID for testing."""
    return "collection-606"


@pytest.fixture
def entry_id() -> str:
    """A valid collection entry ID for testing."""
    return "entry-707"


@pytest.fixture
def attachment_id() -> str:
    """A valid attachment ID for testing."""
    return "attachment-808"


@pytest.fixture
def guest_id() -> str:
    """A valid guest ID for testing."""
    return "guest-909"
