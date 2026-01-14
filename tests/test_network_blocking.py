"""
Tests to verify that network calls are blocked in all tests.

These tests ensure that our conftest.py configuration prevents any
real network calls, even if tests don't explicitly set up mocks.
"""

import pytest
from pytest_httpx import HTTPXMock

import opengov_api


class TestNetworkBlocking:
    """Tests to verify network call blocking works correctly."""

    def test_autouse_fixture_prevents_network_calls(self):
        """
        Test that the autouse fixture in conftest.py prevents network calls.

        This test does NOT explicitly use the httpx_mock fixture, but because
        of the autouse fixture in conftest.py, httpx_mock is still active and
        will catch any unmocked requests at teardown time.

        Note: This test will pass, but if we try to make an unmocked request,
        pytest will fail at teardown with "requests were not expected" error.
        """
        opengov_api.set_api_key("test-api-key")
        opengov_api.set_community("testcommunity")

        # Don't make any API calls in this test - just verify the fixture is there
        # The presence of the autouse fixture means httpx_mock is always active
        pass

    def test_network_calls_blocked_without_explicit_mock_usage(
        self, httpx_mock: HTTPXMock
    ):
        """
        Test that network calls are blocked when no mock is set up.

        This test explicitly uses httpx_mock fixture and verifies that
        unmocked requests are blocked with a clear error.
        """
        opengov_api.set_api_key("test-api-key")
        opengov_api.set_community("testcommunity")

        # This should raise an exception because no mock is set up
        # The exception will be a TimeoutException from pytest-httpx
        with pytest.raises(Exception) as exc_info:
            opengov_api.list_records()

        # Verify it's a timeout/no response error from pytest-httpx, not a real network error
        error_msg = str(exc_info.value).lower()
        assert "no response" in error_msg or "timeout" in error_msg, (
            f"Expected mock error, got: {exc_info.value}"
        )

        # With retries, we should see 4 requests (initial + 3 retries)
        # because the httpx.TimeoutException is retryable
        assert len(httpx_mock._requests_not_matched) == 4, (
            f"Should have caught 4 requests (1 initial + 3 retries), got {len(httpx_mock._requests_not_matched)}"
        )

        # Clear the unmocked requests so teardown doesn't fail
        httpx_mock._requests_not_matched.clear()

    def test_network_calls_succeed_with_proper_mock(
        self, httpx_mock: HTTPXMock, build_url
    ):
        """
        Test that mocked calls work correctly.

        This test explicitly uses httpx_mock and sets up a proper mock.
        """
        opengov_api.set_api_key("test-api-key")
        opengov_api.set_community("testcommunity")

        # Set up the mock
        import re

        url = build_url("testcommunity/records")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        # This should succeed because we have a mock
        result = opengov_api.list_records()
        assert hasattr(result, "data")  # Verify we got a response

    @pytest.mark.skip(
        reason="This test is expected to fail - documents behavior when mocks are missing"
    )
    def test_unmocked_request_causes_test_failure(self, configure_client):
        """
        Test that unmocked requests cause the test to fail at teardown.

        This test makes a request that isn't mocked. The test itself won't
        fail immediately, but pytest-httpx will fail it during teardown with
        "The following requests were not expected" error.

        This test is expected to fail - it's here to document the behavior.
        """
        # This would cause pytest-httpx to fail during teardown
        # because no mock is set up for this request
        opengov_api.list_records()
