"""
Infrastructure tests for HTTP client behaviors.

These tests verify that the underlying HTTP client infrastructure works
correctly across ALL endpoints. By using parametrized tests, we test each
behavior once but verify it works for all endpoints, eliminating duplication.
"""

import pytest
from pytest_httpx import HTTPXMock

import opengov_api
from opengov_api.exceptions import (
    OpenGovConfigurationError,
    OpenGovResponseParseError,
)


class TestInfrastructure:
    """Test HTTP client behaviors that apply to ALL endpoints."""

    @pytest.mark.parametrize(
        "endpoint_func",
        [
            opengov_api.list_records,
            opengov_api.list_users,
            opengov_api.list_locations,
            opengov_api.list_approval_steps,
            opengov_api.list_document_steps,
            opengov_api.list_inspection_steps,
            opengov_api.list_files,
            opengov_api.list_projects,
        ],
    )
    def test_requires_api_key(self, endpoint_func, httpx_mock: HTTPXMock):
        """All endpoints require API key to be set."""
        opengov_api.set_community("testcommunity")
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            endpoint_func()
        assert "API key not set" in str(exc_info.value)

    @pytest.mark.parametrize(
        "endpoint_func",
        [
            opengov_api.list_records,
            opengov_api.list_users,
            opengov_api.list_locations,
            opengov_api.list_approval_steps,
            opengov_api.list_document_steps,
            opengov_api.list_inspection_steps,
            opengov_api.list_files,
            opengov_api.list_projects,
        ],
    )
    def test_requires_community(self, endpoint_func, httpx_mock: HTTPXMock):
        """All endpoints require community to be set."""
        opengov_api.set_api_key("test-api-key")
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            endpoint_func()
        assert "Community not set" in str(exc_info.value)

    @pytest.mark.parametrize(
        "endpoint_func,url_pattern",
        [
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
            ),
            (
                opengov_api.list_locations,
                "https://api.plce.opengov.com/plce/v2/testcommunity/locations",
            ),
            (
                opengov_api.list_approval_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/approval-steps",
            ),
            (
                opengov_api.list_document_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/document-steps",
            ),
            (
                opengov_api.list_inspection_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/inspection-steps",
            ),
            (
                opengov_api.list_files,
                "https://api.plce.opengov.com/plce/v2/testcommunity/files",
            ),
            (
                opengov_api.list_projects,
                "https://api.plce.opengov.com/plce/v2/testcommunity/projects",
            ),
        ],
    )
    def test_sends_auth_header(
        self, endpoint_func, url_pattern, httpx_mock: HTTPXMock, configure_client
    ):
        """All endpoints send correct Authorization header."""
        httpx_mock.add_response(url=url_pattern, json={})
        endpoint_func()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Token test-api-key"

    @pytest.mark.parametrize(
        "endpoint_func,url_pattern",
        [
            (
                opengov_api.list_records,
                "https://api.plce.opengov.com/plce/v2/testcommunity/records",
            ),
            (
                opengov_api.list_users,
                "https://api.plce.opengov.com/plce/v2/testcommunity/users",
            ),
            (
                opengov_api.list_locations,
                "https://api.plce.opengov.com/plce/v2/testcommunity/locations",
            ),
            (
                opengov_api.list_approval_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/approval-steps",
            ),
            (
                opengov_api.list_document_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/document-steps",
            ),
            (
                opengov_api.list_inspection_steps,
                "https://api.plce.opengov.com/plce/v2/testcommunity/inspection-steps",
            ),
            (
                opengov_api.list_files,
                "https://api.plce.opengov.com/plce/v2/testcommunity/files",
            ),
            (
                opengov_api.list_projects,
                "https://api.plce.opengov.com/plce/v2/testcommunity/projects",
            ),
        ],
    )
    def test_handles_invalid_json(
        self, endpoint_func, url_pattern, httpx_mock: HTTPXMock, configure_client
    ):
        """All endpoints handle non-JSON responses correctly."""
        httpx_mock.add_response(url=url_pattern, text="not valid json")
        with pytest.raises(OpenGovResponseParseError) as exc_info:
            endpoint_func()
        assert "Failed to parse JSON" in str(exc_info.value)

    @pytest.mark.parametrize(
        "endpoint_func,custom_url",
        [
            (
                opengov_api.list_records,
                "https://custom.api.com/v3/testcommunity/records",
            ),
            (opengov_api.list_users, "https://custom.api.com/v3/testcommunity/users"),
            (
                opengov_api.list_locations,
                "https://custom.api.com/v3/testcommunity/locations",
            ),
            (
                opengov_api.list_approval_steps,
                "https://custom.api.com/v3/testcommunity/approval-steps",
            ),
            (
                opengov_api.list_document_steps,
                "https://custom.api.com/v3/testcommunity/document-steps",
            ),
            (
                opengov_api.list_inspection_steps,
                "https://custom.api.com/v3/testcommunity/inspection-steps",
            ),
            (opengov_api.list_files, "https://custom.api.com/v3/testcommunity/files"),
            (
                opengov_api.list_projects,
                "https://custom.api.com/v3/testcommunity/projects",
            ),
        ],
    )
    def test_custom_base_url(
        self, endpoint_func, custom_url, httpx_mock: HTTPXMock, configure_client
    ):
        """All endpoints respect custom base URL configuration."""
        opengov_api.set_base_url("https://custom.api.com/v3")
        httpx_mock.add_response(url=custom_url, json={})
        result = endpoint_func()
        assert result == {}  # Should not raise, returns empty dict


class TestGetEndpointInfrastructure:
    """Test infrastructure for get-by-id style endpoints."""

    @pytest.mark.parametrize(
        "endpoint_func,resource_id",
        [
            (opengov_api.get_record, "12345"),
            (opengov_api.get_user, "12345"),
            (opengov_api.list_user_flags, "12345"),
            (opengov_api.get_location, "12345"),
            (opengov_api.list_location_flags, "12345"),
            (opengov_api.get_approval_step, "12345"),
            (opengov_api.get_document_step, "12345"),
            (opengov_api.get_inspection_step, "12345"),
            (opengov_api.list_inspection_types, "12345"),
            (opengov_api.get_file, "12345"),
            (opengov_api.get_project, "12345"),
        ],
    )
    def test_get_requires_api_key(
        self, endpoint_func, resource_id, httpx_mock: HTTPXMock
    ):
        """All get endpoints require API key to be set."""
        opengov_api.set_community("testcommunity")
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            endpoint_func(resource_id)
        assert "API key not set" in str(exc_info.value)

    @pytest.mark.parametrize(
        "endpoint_func,resource_id",
        [
            (opengov_api.get_record, "12345"),
            (opengov_api.get_user, "12345"),
            (opengov_api.list_user_flags, "12345"),
            (opengov_api.get_location, "12345"),
            (opengov_api.list_location_flags, "12345"),
            (opengov_api.get_approval_step, "12345"),
            (opengov_api.get_document_step, "12345"),
            (opengov_api.get_inspection_step, "12345"),
            (opengov_api.list_inspection_types, "12345"),
            (opengov_api.get_file, "12345"),
            (opengov_api.get_project, "12345"),
        ],
    )
    def test_get_requires_community(
        self, endpoint_func, resource_id, httpx_mock: HTTPXMock
    ):
        """All get endpoints require community to be set."""
        opengov_api.set_api_key("test-api-key")
        with pytest.raises(OpenGovConfigurationError) as exc_info:
            endpoint_func(resource_id)
        assert "Community not set" in str(exc_info.value)

    @pytest.mark.parametrize(
        "endpoint_func,resource_id,url",
        [
            (
                opengov_api.get_record,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/records/12345",
            ),
            (
                opengov_api.get_user,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/12345",
            ),
            (
                opengov_api.list_user_flags,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/users/12345/flags",
            ),
            (
                opengov_api.get_location,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/locations/12345",
            ),
            (
                opengov_api.list_location_flags,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/locations/12345/flags",
            ),
            (
                opengov_api.get_approval_step,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/approval-steps/12345",
            ),
            (
                opengov_api.get_document_step,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/document-steps/12345",
            ),
            (
                opengov_api.get_inspection_step,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/inspection-steps/12345",
            ),
            (
                opengov_api.list_inspection_types,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/inspection-steps/12345/inspection-types",
            ),
            (
                opengov_api.get_file,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/files/12345",
            ),
            (
                opengov_api.get_project,
                "12345",
                "https://api.plce.opengov.com/plce/v2/testcommunity/projects/12345",
            ),
        ],
    )
    def test_get_sends_auth_header(
        self, endpoint_func, resource_id, url, httpx_mock: HTTPXMock, configure_client
    ):
        """All get endpoints send correct Authorization header."""
        httpx_mock.add_response(url=url, json={"id": resource_id})
        endpoint_func(resource_id)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Token test-api-key"

    @pytest.mark.parametrize(
        "endpoint_func,resource_id,custom_url",
        [
            (
                opengov_api.get_record,
                "12345",
                "https://custom.api.com/v3/testcommunity/records/12345",
            ),
            (
                opengov_api.get_user,
                "12345",
                "https://custom.api.com/v3/testcommunity/users/12345",
            ),
            (
                opengov_api.list_user_flags,
                "12345",
                "https://custom.api.com/v3/testcommunity/users/12345/flags",
            ),
            (
                opengov_api.get_location,
                "12345",
                "https://custom.api.com/v3/testcommunity/locations/12345",
            ),
            (
                opengov_api.list_location_flags,
                "12345",
                "https://custom.api.com/v3/testcommunity/locations/12345/flags",
            ),
            (
                opengov_api.get_approval_step,
                "12345",
                "https://custom.api.com/v3/testcommunity/approval-steps/12345",
            ),
            (
                opengov_api.get_document_step,
                "12345",
                "https://custom.api.com/v3/testcommunity/document-steps/12345",
            ),
            (
                opengov_api.get_inspection_step,
                "12345",
                "https://custom.api.com/v3/testcommunity/inspection-steps/12345",
            ),
            (
                opengov_api.list_inspection_types,
                "12345",
                "https://custom.api.com/v3/testcommunity/inspection-steps/12345/inspection-types",
            ),
            (
                opengov_api.get_file,
                "12345",
                "https://custom.api.com/v3/testcommunity/files/12345",
            ),
            (
                opengov_api.get_project,
                "12345",
                "https://custom.api.com/v3/testcommunity/projects/12345",
            ),
        ],
    )
    def test_get_custom_base_url(
        self,
        endpoint_func,
        resource_id,
        custom_url,
        httpx_mock: HTTPXMock,
        configure_client,
    ):
        """All get endpoints respect custom base URL configuration."""
        opengov_api.set_base_url("https://custom.api.com/v3")
        httpx_mock.add_response(url=custom_url, json={"id": resource_id})
        result = endpoint_func(resource_id)
        assert result["id"] == resource_id
