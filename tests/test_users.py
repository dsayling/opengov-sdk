"""
Tests for users-specific endpoint behaviors.

Infrastructure and common endpoint tests are in test_infrastructure.py
and test_common_endpoints.py. This file only tests behaviors unique to
the users endpoint.
"""

from pytest_httpx import HTTPXMock

import opengov_api


class TestUsersEndpoint:
    """Tests specific to the users endpoint."""

    def test_list_users_with_pagination_data(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test list_users with pagination metadata."""
        mock_response = {
            "users": [{"id": "1", "name": "User 1"}],
            "pagination": {"page": 1, "total_pages": 5, "total_items": 50},
        }
        httpx_mock.add_response(
            url="https://api.plce.opengov.com/plce/v2/testcommunity/users",
            json=mock_response,
        )

        result = opengov_api.list_users()
        assert result == mock_response
        assert "pagination" in result
        assert result["pagination"]["total_pages"] == 5
        assert result["pagination"]["total_items"] == 50

    def test_create_user(self, httpx_mock: HTTPXMock, configure_client):
        """Test creating a new user."""
        request_data = {
            "data": {
                "type": "user",
                "attributes": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com"
                }
            }
        }
        
        mock_response = {
            "data": {
                "id": "user-12345",
                "type": "user",
                "attributes": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com"
                }
            }
        }
        
        httpx_mock.add_response(
            url="https://api.plce.opengov.com/plce/v2/testcommunity/users",
            method="POST",
            json=mock_response,
        )
        
        result = opengov_api.create_user(request_data)
        assert result == mock_response
        assert result["data"]["id"] == "user-12345"
        assert result["data"]["attributes"]["email"] == "john.doe@example.com"
