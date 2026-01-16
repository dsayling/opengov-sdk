"""
Tests for record-specific endpoint behaviors.

Infrastructure and common endpoint tests are in test_infrastructure.py
and test_common_endpoints.py. This file tests behaviors unique to the
records resource including CRUD operations, nested resources, and edge cases.
"""

from pytest_httpx import HTTPXMock

import opengov_api


class TestRecordsEdgeCases:
    """Tests for edge cases and special behaviors."""

    def test_get_record_with_special_characters(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test get_record handles special characters in record IDs."""
        record_id = "rec-123-abc"
        httpx_mock.add_response(
            url=build_url(f"testcommunity/records/{record_id}"),
            json={
                "data": {
                    "id": record_id,
                    "type": "records",
                    "attributes": {"number": "REC-001"},
                }
            },
        )

        result = opengov_api.get_record(record_id)
        assert not isinstance(result.data, list)
        assert result.data.id == record_id
        assert result.data.attributes.number == "REC-001"


class TestRecordCRUD:
    """Tests for basic record CRUD operations."""

    def test_create_record(
        self, httpx_mock: HTTPXMock, configure_client, build_url, assert_request_method
    ):
        """Test creating a record."""
        url = build_url("testcommunity/records")
        record_data = {"data": {"type": "records", "attributes": {"name": "Test"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {"id": "123", "type": "records", "attributes": {"name": "Test"}}
            },
        )

        result = opengov_api.create_record(record_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "123"
        assert_request_method("POST")

    def test_update_record(
        self, httpx_mock: HTTPXMock, configure_client, build_url, assert_request_method
    ):
        """Test updating a record."""
        url = build_url("testcommunity/records/123")
        record_data = {"data": {"type": "records", "attributes": {"name": "Updated"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "123",
                    "type": "records",
                    "attributes": {"name": "Updated"},
                }
            },
        )

        result = opengov_api.update_record("123", record_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "123"
        assert_request_method("PATCH")

    def test_archive_record(
        self, httpx_mock: HTTPXMock, configure_client, build_url, assert_request_method
    ):
        """Test archiving a record."""
        url = build_url("testcommunity/records/123")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.archive_record("123")
        assert result is None
        assert_request_method("DELETE")


class TestRecordForm:
    """Tests for record form operations."""

    def test_get_record_form(self, httpx_mock: HTTPXMock, configure_client, build_url):
        """Test getting record form data."""
        url = build_url("testcommunity/records/123/form")
        httpx_mock.add_response(url=url, json={"data": {"fields": []}})

        result = opengov_api.get_record_form("123")
        assert result.fields == []

    def test_update_record_form(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test updating record form data."""
        url = build_url("testcommunity/records/123/form")
        form_data = {"data": {"fields": []}}
        httpx_mock.add_response(url=url, json={"data": {"fields": []}})

        result = opengov_api.update_record_form("123", form_data)
        assert result.fields == []

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PATCH"


class TestRecordApplicant:
    """Tests for record applicant operations."""

    def test_get_record_applicant(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting record applicant."""
        url = build_url("testcommunity/records/123/applicant")
        httpx_mock.add_response(
            url=url,
            json={"data": {"id": "user-1", "type": "applicants", "attributes": {}}},
        )

        result = opengov_api.get_record_applicant("123")
        assert not isinstance(result.data, list)
        assert result.data.id == "user-1"

    def test_update_record_applicant(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test updating record applicant."""
        url = build_url("testcommunity/records/123/applicant")
        applicant_data = {"data": {"id": "user-1"}}
        httpx_mock.add_response(
            url=url,
            json={"data": {"id": "user-1", "type": "applicants", "attributes": {}}},
        )

        result = opengov_api.update_record_applicant("123", applicant_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "user-1"

    def test_remove_record_applicant(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test removing record applicant."""
        url = build_url("testcommunity/records/123/applicant")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.remove_record_applicant("123")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordGuests:
    """Tests for record guest operations."""

    def test_list_record_guests(
        self, httpx_mock: HTTPXMock, configure_client, build_url, mock_url_with_params
    ):
        """Test listing record guests."""
        url = build_url("testcommunity/records/123/guests")
        httpx_mock.add_response(
            url=mock_url_with_params(url),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_guests("123")
        assert result.data == []

    def test_add_record_guest(self, httpx_mock: HTTPXMock, configure_client, build_url):
        """Test adding a record guest."""
        url = build_url("testcommunity/records/123/guests")
        guest_data = {"data": {"id": "user-1"}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "user-1",
                    "type": "guests",
                    "attributes": {"name": "Test User"},
                }
            },
        )

        result = opengov_api.add_record_guest("123", guest_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "user-1"

    def test_get_record_guest(self, httpx_mock: HTTPXMock, configure_client, build_url):
        """Test getting a specific record guest."""
        url = build_url("testcommunity/records/123/guests/user-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "user-1",
                    "type": "guests",
                    "attributes": {"name": "Test User"},
                }
            },
        )

        result = opengov_api.get_record_guest("123", "user-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "user-1"

    def test_remove_record_guest(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test removing a record guest."""
        url = build_url("testcommunity/records/123/guests/user-1")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.remove_record_guest("123", "user-1")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordLocations:
    """Tests for record location operations."""

    def test_get_record_primary_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting record primary location."""
        url = build_url("testcommunity/records/123/primary-location")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "loc-1",
                    "type": "locations",
                    "attributes": {"address": "123 Main St"},
                }
            },
        )

        result = opengov_api.get_record_primary_location("123")
        assert not isinstance(result.data, list)
        assert result.data.id == "loc-1"

    def test_update_record_primary_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test updating record primary location."""
        url = build_url("testcommunity/records/123/primary-location")
        location_data = {"data": {"id": "loc-1"}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "loc-1",
                    "type": "locations",
                    "attributes": {"address": "123 Main St"},
                }
            },
        )

        result = opengov_api.update_record_primary_location("123", location_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "loc-1"

    def test_remove_record_primary_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test removing record primary location."""
        url = build_url("testcommunity/records/123/primary-location")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.remove_record_primary_location("123")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"

    def test_list_record_additional_locations(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing record additional locations."""
        import re

        url = build_url("testcommunity/records/123/additional-locations")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_additional_locations("123")
        assert result.data == []

    def test_add_record_additional_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test adding an additional location to a record."""
        url = build_url("testcommunity/records/123/additional-locations")
        location_data = {"data": {"id": "loc-1"}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "loc-1",
                    "type": "locations",
                    "attributes": {"address": "456 Oak Ave"},
                }
            },
        )

        result = opengov_api.add_record_additional_location("123", location_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "loc-1"

    def test_get_record_additional_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific additional location on a record."""
        url = build_url("testcommunity/records/123/additional-locations/loc-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "loc-1",
                    "type": "locations",
                    "attributes": {"address": "456 Oak Ave"},
                }
            },
        )

        result = opengov_api.get_record_additional_location("123", "loc-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "loc-1"

    def test_remove_record_additional_location(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test removing an additional location from a record."""
        url = build_url("testcommunity/records/123/additional-locations/loc-1")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.remove_record_additional_location("123", "loc-1")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordAttachments:
    """Tests for record attachment operations."""

    def test_list_record_attachments(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing record attachments."""
        import re

        url = build_url("testcommunity/records/123/attachments")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_attachments("123")
        assert result.data == []

    def test_add_record_attachment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test adding a record attachment."""
        url = build_url("testcommunity/records/123/attachments")
        attachment_data = {"data": {"id": "att-1"}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "att-1",
                    "type": "attachments",
                    "attributes": {"filename": "test.pdf"},
                }
            },
        )

        result = opengov_api.add_record_attachment("123", attachment_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "att-1"

    def test_get_record_attachment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific record attachment."""
        url = build_url("testcommunity/records/123/attachments/att-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "att-1",
                    "type": "attachments",
                    "attributes": {"filename": "test.pdf"},
                }
            },
        )

        result = opengov_api.get_record_attachment("123", "att-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "att-1"

    def test_remove_record_attachment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test removing a record attachment."""
        url = build_url("testcommunity/records/123/attachments/att-1")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.remove_record_attachment("123", "att-1")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordChangeRequests:
    """Tests for record change request operations."""

    def test_get_record_change_request(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific change request."""
        url = build_url("testcommunity/records/123/change-requests/cr-1")
        httpx_mock.add_response(
            url=url,
            json={"data": {"id": "cr-1", "type": "change-requests", "attributes": {}}},
        )

        result = opengov_api.get_record_change_request("123", "cr-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "cr-1"

    def test_get_most_recent_record_change_request(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting the most recent change request."""
        url = build_url("testcommunity/records/123/change-requests")
        httpx_mock.add_response(
            url=url,
            json={"data": {"id": "cr-1", "type": "change-requests", "attributes": {}}},
        )

        result = opengov_api.get_most_recent_record_change_request("123")
        assert not isinstance(result.data, list)
        assert result.data.id == "cr-1"

    def test_create_record_change_request(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test creating a change request."""
        url = build_url("testcommunity/records/123/change-requests")
        change_request_data = {"data": {"attributes": {"reason": "Updates needed"}}}
        httpx_mock.add_response(
            url=url,
            json={"data": {"id": "cr-1", "type": "change-requests", "attributes": {}}},
        )

        result = opengov_api.create_record_change_request("123", change_request_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "cr-1"

    def test_cancel_record_change_request(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test canceling a change request."""
        url = build_url("testcommunity/records/123/change-requests/cr-1")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.cancel_record_change_request("123", "cr-1")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordWorkflowSteps:
    """Tests for record workflow step operations."""

    def test_list_record_workflow_steps(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing record workflow steps."""
        import re

        url = build_url("testcommunity/records/123/workflow-steps")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_workflow_steps("123")
        assert result.data == []

    def test_create_record_workflow_step(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test creating a workflow step."""
        url = build_url("testcommunity/records/123/workflow-steps")
        step_data = {"data": {"type": "workflow-step"}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "step-1",
                    "type": "workflow-steps",
                    "attributes": {
                        "label": "Review",
                        "stepType": "REVIEW",
                        "status": "ACTIVE",
                    },
                }
            },
        )

        result = opengov_api.create_record_workflow_step("123", step_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "step-1"

    def test_get_record_workflow_step(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific workflow step."""
        url = build_url("testcommunity/records/123/workflow-steps/step-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "step-1",
                    "type": "workflow-steps",
                    "attributes": {
                        "label": "Review",
                        "stepType": "REVIEW",
                        "status": "ACTIVE",
                    },
                }
            },
        )

        result = opengov_api.get_record_workflow_step("123", "step-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "step-1"

    def test_update_record_workflow_step(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test updating a workflow step."""
        url = build_url("testcommunity/records/123/workflow-steps/step-1")
        step_data = {"data": {"attributes": {"status": "completed"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "step-1",
                    "type": "workflow-steps",
                    "attributes": {
                        "label": "Review",
                        "stepType": "REVIEW",
                        "status": "COMPLETE",
                    },
                }
            },
        )

        result = opengov_api.update_record_workflow_step("123", "step-1", step_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "step-1"

    def test_delete_record_workflow_step(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test deleting a workflow step."""
        url = build_url("testcommunity/records/123/workflow-steps/step-1")
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.delete_record_workflow_step("123", "step-1")
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordWorkflowStepComments:
    """Tests for workflow step comment operations."""

    def test_list_record_workflow_step_comments(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing workflow step comments."""
        import re

        url = build_url("testcommunity/records/123/workflow-steps/step-1/comments")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_workflow_step_comments("123", "step-1")
        assert result.data == []

    def test_create_record_workflow_step_comment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test creating a workflow step comment."""
        url = build_url("testcommunity/records/123/workflow-steps/step-1/comments")
        comment_data = {"data": {"attributes": {"text": "Test comment"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "comment-1",
                    "type": "comments",
                    "attributes": {"text": "Test comment"},
                }
            },
        )

        result = opengov_api.create_record_workflow_step_comment(
            "123", "step-1", comment_data
        )
        assert not isinstance(result.data, list)
        assert result.data.id == "comment-1"

    def test_get_record_workflow_step_comment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific workflow step comment."""
        url = build_url(
            "testcommunity/records/123/workflow-steps/step-1/comments/comment-1"
        )
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "comment-1",
                    "type": "comments",
                    "attributes": {"text": "Test comment"},
                }
            },
        )

        result = opengov_api.get_record_workflow_step_comment(
            "123", "step-1", "comment-1"
        )
        assert not isinstance(result.data, list)
        assert result.data.id == "comment-1"

    def test_delete_record_workflow_step_comment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test deleting a workflow step comment."""
        url = build_url(
            "testcommunity/records/123/workflow-steps/step-1/comments/comment-1"
        )
        httpx_mock.add_response(url=url, json={})

        result = opengov_api.delete_record_workflow_step_comment(
            "123", "step-1", "comment-1"
        )
        assert result is None

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"


class TestRecordCollections:
    """Tests for record collection operations."""

    def test_list_record_collections(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing record collections."""
        import re

        url = build_url("testcommunity/records/123/collections")
        httpx_mock.add_response(
            url=re.compile(re.escape(url) + r"(\?.*)?$"),
            json={"data": [], "meta": {}, "links": {}},
        )

        result = opengov_api.list_record_collections("123")
        assert result.data == []

    def test_get_record_collection(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific collection."""
        url = build_url("testcommunity/records/123/collections/coll-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "coll-1",
                    "type": "collections",
                    "attributes": {"name": "Test Collection"},
                }
            },
        )

        result = opengov_api.get_record_collection("123", "coll-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "coll-1"

    def test_create_record_collection_entry(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test creating a collection entry."""
        url = build_url("testcommunity/records/123/collections/coll-1")
        entry_data = {"data": {"attributes": {"value": "test"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "entry-1",
                    "type": "collection-entries",
                    "attributes": {},
                }
            },
        )

        result = opengov_api.create_record_collection_entry("123", "coll-1", entry_data)
        assert not isinstance(result.data, list)
        assert result.data.id == "entry-1"

    def test_get_record_collection_entry(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific collection entry."""
        url = build_url("testcommunity/records/123/collections/coll-1/entries/entry-1")
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "entry-1",
                    "type": "collection-entries",
                    "attributes": {},
                }
            },
        )

        result = opengov_api.get_record_collection_entry("123", "coll-1", "entry-1")
        assert not isinstance(result.data, list)
        assert result.data.id == "entry-1"

    def test_update_record_collection_entry(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test updating a collection entry."""
        url = build_url("testcommunity/records/123/collections/coll-1/entries/entry-1")
        entry_data = {"data": {"attributes": {"value": "updated"}}}
        httpx_mock.add_response(
            url=url,
            json={
                "data": {
                    "id": "entry-1",
                    "type": "collection-entries",
                    "attributes": {},
                }
            },
        )

        result = opengov_api.update_record_collection_entry(
            "123", "coll-1", "entry-1", entry_data
        )
        assert not isinstance(result.data, list)
        assert result.data.id == "entry-1"
