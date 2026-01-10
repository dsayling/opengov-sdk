"""
Common endpoint behavior tests.

These tests verify consistent REST API patterns across all endpoints
(list, get, error handling). Using parametrization ensures all endpoints
behave consistently.
"""

import pytest
from pytest_httpx import HTTPXMock

import opengov_api
from opengov_api.exceptions import (
    OpenGovNotFoundError,
    OpenGovAuthenticationError,
    OpenGovRateLimitError,
    OpenGovInternalServerError,
)


class TestListEndpoints:
    """Tests for common behaviors of all list-style endpoints."""

    @pytest.mark.parametrize(
        "endpoint_func,url,response_key",
        [
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
                "records",
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
                "users",
            ),
        ],
    )
    def test_list_success(
        self, endpoint_func, url, response_key, httpx_mock: HTTPXMock, configure_client
    ):
        """All list endpoints return collections successfully."""
        mock_items = [{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}]
        httpx_mock.add_response(url=url, json={response_key: mock_items})

        result = endpoint_func()
        assert response_key in result
        assert len(result[response_key]) == 2
        assert result[response_key][0]["id"] == "1"

    @pytest.mark.parametrize(
        "endpoint_func,url,response_key",
        [
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
                "records",
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
                "users",
            ),
        ],
    )
    def test_list_empty(
        self, endpoint_func, url, response_key, httpx_mock: HTTPXMock, configure_client
    ):
        """All list endpoints handle empty results."""
        httpx_mock.add_response(url=url, json={response_key: []})

        result = endpoint_func()
        assert result == {response_key: []}

    @pytest.mark.parametrize(
        "endpoint_func,url,status_code,exception_class",
        [
            # Test 401 for all list endpoints
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
                401,
                OpenGovAuthenticationError,
            ),
            # Test 429 for all list endpoints
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
                429,
                OpenGovRateLimitError,
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
                429,
                OpenGovRateLimitError,
            ),
            # Test 500 for all list endpoints
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
                500,
                OpenGovInternalServerError,
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
                500,
                OpenGovInternalServerError,
            ),
        ],
    )
    def test_list_error_handling(
        self,
        endpoint_func,
        url,
        status_code,
        exception_class,
        httpx_mock: HTTPXMock,
        configure_client,
    ):
        """All list endpoints handle HTTP errors consistently."""
        httpx_mock.add_response(
            url=url, status_code=status_code, json={"message": "Error message"}
        )

        with pytest.raises(exception_class) as exc_info:
            endpoint_func()
        assert exc_info.value.status_code == status_code


class TestGetEndpoints:
    """Tests for common behaviors of all get-by-id endpoints."""

    @pytest.mark.parametrize(
        "endpoint_func,url_template,resource_id",
        [
            (
                opengov_api.get_record,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/{}",
                "12345",
            ),
            (
                opengov_api.get_user,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}",
                "12345",
            ),
            (
                opengov_api.list_user_flags,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}/flags",
                "12345",
            ),
        ],
    )
    def test_get_success(
        self,
        endpoint_func,
        url_template,
        resource_id,
        httpx_mock: HTTPXMock,
        configure_client,
    ):
        """All get endpoints return single resources successfully."""
        url = url_template.format(resource_id)
        mock_resource = {"id": resource_id, "name": "Test Resource"}
        httpx_mock.add_response(url=url, json=mock_resource)

        result = endpoint_func(resource_id)
        assert result["id"] == resource_id
        assert result["name"] == "Test Resource"

    @pytest.mark.parametrize(
        "endpoint_func,url_template,resource_id",
        [
            (
                opengov_api.get_record,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/{}",
                "99999",
            ),
            (
                opengov_api.get_user,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}",
                "99999",
            ),
            (
                opengov_api.list_user_flags,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}/flags",
                "99999",
            ),
        ],
    )
    def test_get_not_found(
        self,
        endpoint_func,
        url_template,
        resource_id,
        httpx_mock: HTTPXMock,
        configure_client,
    ):
        """All get endpoints handle 404 errors consistently."""
        url = url_template.format(resource_id)
        httpx_mock.add_response(url=url, status_code=404, json={"message": "Not found"})

        with pytest.raises(OpenGovNotFoundError) as exc_info:
            endpoint_func(resource_id)
        assert exc_info.value.status_code == 404

    @pytest.mark.parametrize(
        "endpoint_func,url_template,resource_id,status_code,exception_class",
        [
            # Test various error codes for get endpoints
            (
                opengov_api.get_record,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/{}",
                "12345",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.get_record,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/{}",
                "12345",
                429,
                OpenGovRateLimitError,
            ),
            (
                opengov_api.get_record,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/{}",
                "12345",
                500,
                OpenGovInternalServerError,
            ),
            (
                opengov_api.get_user,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}",
                "12345",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.list_user_flags,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/{}/flags",
                "12345",
                429,
                OpenGovRateLimitError,
            ),
        ],
    )
    def test_get_error_handling(
        self,
        endpoint_func,
        url_template,
        resource_id,
        status_code,
        exception_class,
        httpx_mock: HTTPXMock,
        configure_client,
    ):
        """All get endpoints handle HTTP errors consistently."""
        url = url_template.format(resource_id)
        httpx_mock.add_response(
            url=url, status_code=status_code, json={"message": "Error message"}
        )

        with pytest.raises(exception_class) as exc_info:
            endpoint_func(resource_id)
        assert exc_info.value.status_code == status_code
