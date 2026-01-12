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
        "endpoint_func,url_path,response_key",
        [
            (
                opengov_api.list_records,
                "testcommunity/records",
                "records",
            ),
            (
                opengov_api.list_users,
                "testcommunity/users",
                "users",
            ),
            (
                opengov_api.list_locations,
                "testcommunity/locations",
                "locations",
            ),
            (
                opengov_api.list_approval_steps,
                "testcommunity/approval-steps",
                "approval-steps",
            ),
            (
                opengov_api.list_document_steps,
                "testcommunity/document-steps",
                "document-steps",
            ),
            (
                opengov_api.list_inspection_steps,
                "testcommunity/inspection-steps",
                "inspection-steps",
            ),
            (
                opengov_api.list_files,
                "testcommunity/files",
                "files",
            ),
            (
                opengov_api.list_projects,
                "testcommunity/projects",
                "projects",
            ),
        ],
    )
    def test_list_success(
        self,
        endpoint_func,
        url_path,
        response_key,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
        mock_url_with_params,
    ):
        """All list endpoints return collections successfully."""
        mock_items = [
            {
                "id": "1",
                "type": response_key.rstrip("s"),
                "attributes": {"name": "Item 1"},
            },
            {
                "id": "2",
                "type": response_key.rstrip("s"),
                "attributes": {"name": "Item 2"},
            },
        ]
        url = build_url(url_path)
        response_json = {
            "data": mock_items,
            "meta": {"page": 1, "size": 20},
            "links": {"self": url},
        }

        httpx_mock.add_response(url=mock_url_with_params(url), json=response_json)

        result = endpoint_func()
        # list_records returns typed JSONAPIResponse, others return dict
        if (
            hasattr(result, "data")
            and hasattr(result, "meta")
            and hasattr(result, "links")
            and not isinstance(result, dict)
        ):
            # Typed Pydantic response
            assert len(result.data) == 2
            assert result.data[0].id == "1"
        else:
            # Dict response - JSON:API format
            assert "data" in result
            assert len(result["data"]) == 2
            assert result["data"][0]["id"] == "1"

    @pytest.mark.parametrize(
        "endpoint_func,url_path,response_key",
        [
            (
                opengov_api.list_records,
                "testcommunity/records",
                "records",
            ),
            (
                opengov_api.list_users,
                "testcommunity/users",
                "users",
            ),
            (
                opengov_api.list_locations,
                "testcommunity/locations",
                "locations",
            ),
            (
                opengov_api.list_approval_steps,
                "testcommunity/approval-steps",
                "approval-steps",
            ),
            (
                opengov_api.list_document_steps,
                "testcommunity/document-steps",
                "document-steps",
            ),
            (
                opengov_api.list_inspection_steps,
                "testcommunity/inspection-steps",
                "inspection-steps",
            ),
            (
                opengov_api.list_files,
                "testcommunity/files",
                "files",
            ),
            (
                opengov_api.list_projects,
                "testcommunity/projects",
                "projects",
            ),
        ],
    )
    def test_list_empty(
        self,
        endpoint_func,
        url_path,
        response_key,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
    ):
        """All list endpoints handle empty results."""
        import re

        url = build_url(url_path)
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = endpoint_func()
        # list_records returns typed JSONAPIResponse, others return dict
        if (
            hasattr(result, "data")
            and hasattr(result, "meta")
            and hasattr(result, "links")
            and not isinstance(result, dict)
        ):
            # Typed Pydantic response
            assert len(result.data) == 0
        else:
            # Dict response - JSON:API format
            assert "data" in result
            assert len(result["data"]) == 0

    @pytest.mark.parametrize(
        "endpoint_func,url_path,status_code,exception_class",
        [
            # Test 401 for all list endpoints
            (
                opengov_api.list_records,
                "testcommunity/records",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.list_users,
                "testcommunity/users",
                401,
                OpenGovAuthenticationError,
            ),
            # Test 429 for all list endpoints
            (
                opengov_api.list_records,
                "testcommunity/records",
                429,
                OpenGovRateLimitError,
            ),
            (
                opengov_api.list_users,
                "testcommunity/users",
                429,
                OpenGovRateLimitError,
            ),
            # Test 500 for all list endpoints
            (
                opengov_api.list_records,
                "testcommunity/records",
                500,
                OpenGovInternalServerError,
            ),
            (
                opengov_api.list_users,
                "testcommunity/users",
                500,
                OpenGovInternalServerError,
            ),
        ],
    )
    def test_list_error_handling(
        self,
        endpoint_func,
        url_path,
        status_code,
        exception_class,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
    ):
        """All list endpoints handle HTTP errors consistently."""
        import re

        url = build_url(url_path)
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            status_code=status_code,
            json={"message": "Error message"},
        )

        with pytest.raises(exception_class) as exc_info:
            endpoint_func()
        assert exc_info.value.status_code == status_code


class TestGetEndpoints:
    """Tests for common behaviors of all get-by-id endpoints."""

    @pytest.mark.parametrize(
        "endpoint_func,url_path_template,resource_id",
        [
            (
                opengov_api.get_record,
                "testcommunity/records/{}",
                "12345",
            ),
            (
                opengov_api.get_user,
                "testcommunity/users/{}",
                "12345",
            ),
            (
                opengov_api.list_user_flags,
                "testcommunity/users/{}/flags",
                "12345",
            ),
            (
                opengov_api.get_location,
                "testcommunity/locations/{}",
                "12345",
            ),
            (
                opengov_api.list_location_flags,
                "testcommunity/locations/{}/flags",
                "12345",
            ),
            (
                opengov_api.get_approval_step,
                "testcommunity/approval-steps/{}",
                "12345",
            ),
            (
                opengov_api.get_document_step,
                "testcommunity/document-steps/{}",
                "12345",
            ),
            (
                opengov_api.get_inspection_step,
                "testcommunity/inspection-steps/{}",
                "12345",
            ),
            (
                opengov_api.list_inspection_types,
                "testcommunity/inspection-steps/{}/inspection-types",
                "12345",
            ),
            (
                opengov_api.get_file,
                "testcommunity/files/{}",
                "12345",
            ),
            (
                opengov_api.get_project,
                "testcommunity/projects/{}",
                "12345",
            ),
        ],
    )
    def test_get_success(
        self,
        endpoint_func,
        url_path_template,
        resource_id,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
    ):
        """All get endpoints return single resources successfully."""
        url = build_url(url_path_template.format(resource_id))
        mock_resource = {"id": resource_id, "name": "Test Resource"}
        httpx_mock.add_response(url=url, json=mock_resource)

        result = endpoint_func(resource_id)
        assert result["id"] == resource_id
        assert result["name"] == "Test Resource"

    @pytest.mark.parametrize(
        "endpoint_func,url_path_template,resource_id",
        [
            (
                opengov_api.get_record,
                "testcommunity/records/{}",
                "99999",
            ),
            (
                opengov_api.get_user,
                "testcommunity/users/{}",
                "99999",
            ),
            (
                opengov_api.list_user_flags,
                "testcommunity/users/{}/flags",
                "99999",
            ),
            (
                opengov_api.get_location,
                "testcommunity/locations/{}",
                "99999",
            ),
            (
                opengov_api.list_location_flags,
                "testcommunity/locations/{}/flags",
                "99999",
            ),
            (
                opengov_api.get_approval_step,
                "testcommunity/approval-steps/{}",
                "99999",
            ),
            (
                opengov_api.get_document_step,
                "testcommunity/document-steps/{}",
                "99999",
            ),
            (
                opengov_api.get_inspection_step,
                "testcommunity/inspection-steps/{}",
                "99999",
            ),
            (
                opengov_api.list_inspection_types,
                "testcommunity/inspection-steps/{}/inspection-types",
                "99999",
            ),
            (
                opengov_api.get_file,
                "testcommunity/files/{}",
                "99999",
            ),
            (
                opengov_api.get_project,
                "testcommunity/projects/{}",
                "99999",
            ),
        ],
    )
    def test_get_not_found(
        self,
        endpoint_func,
        url_path_template,
        resource_id,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
    ):
        """All get endpoints handle 404 errors consistently."""
        url = build_url(url_path_template.format(resource_id))
        httpx_mock.add_response(url=url, status_code=404, json={"message": "Not found"})

        with pytest.raises(OpenGovNotFoundError) as exc_info:
            endpoint_func(resource_id)
        assert exc_info.value.status_code == 404

    @pytest.mark.parametrize(
        "endpoint_func,url_path_template,resource_id,status_code,exception_class",
        [
            # Test various error codes for get endpoints
            (
                opengov_api.get_record,
                "testcommunity/records/{}",
                "12345",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.get_record,
                "testcommunity/records/{}",
                "12345",
                429,
                OpenGovRateLimitError,
            ),
            (
                opengov_api.get_record,
                "testcommunity/records/{}",
                "12345",
                500,
                OpenGovInternalServerError,
            ),
            (
                opengov_api.get_user,
                "testcommunity/users/{}",
                "12345",
                401,
                OpenGovAuthenticationError,
            ),
            (
                opengov_api.list_user_flags,
                "testcommunity/users/{}/flags",
                "12345",
                429,
                OpenGovRateLimitError,
            ),
        ],
    )
    def test_get_error_handling(
        self,
        endpoint_func,
        url_path_template,
        resource_id,
        status_code,
        exception_class,
        httpx_mock: HTTPXMock,
        configure_client,
        build_url,
    ):
        """All get endpoints handle HTTP errors consistently."""
        url = build_url(url_path_template.format(resource_id))
        httpx_mock.add_response(
            url=url, status_code=status_code, json={"message": "Error message"}
        )

        with pytest.raises(exception_class) as exc_info:
            endpoint_func(resource_id)
        assert exc_info.value.status_code == status_code
