"""
Tests for record-types-specific endpoint behaviors.

Infrastructure and common endpoint tests are in test_infrastructure.py
and test_common_endpoints.py. This file only tests behaviors unique to
the record-types endpoint.
"""

from pytest_httpx import HTTPXMock

import opengov_api


class TestRecordTypesEndpoint:
    """Tests specific to the record-types endpoint."""

    def test_list_record_types_returns_typed_response(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test list_record_types returns JSONAPIResponse with typed data."""
        mock_response = {
            "data": [
                {
                    "id": "rt-12345",
                    "type": "recordType",
                    "attributes": {
                        "name": "Building Permit",
                        "status": "Published",
                        "isEnabled": True,
                        "applyAccess": "Public",
                        "viewAccess": "Public",
                    },
                }
            ],
            "links": {
                "self": "http://example.com/record-types?page[number]=1",
                "first": "http://example.com/record-types?page[number]=1",
                "last": "http://example.com/record-types?page[number]=1",
            },
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_types()

        # Verify it's a JSONAPIResponse
        assert hasattr(result, "data")
        assert hasattr(result, "meta")
        assert hasattr(result, "links")

        # Verify data is typed
        assert len(result.data) == 1
        record_type = result.data[0]
        assert record_type.id == "rt-12345"
        assert record_type.type == "recordType"
        assert record_type.attributes.name == "Building Permit"
        assert record_type.attributes.status == "Published"
        assert record_type.attributes.is_enabled is True

        # Verify pagination methods
        assert result.current_page() == 1
        assert result.total_pages() == 1
        assert result.total_records() == 1
        assert not result.has_next_page()

    def test_list_record_types_with_department_filter(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test list_record_types with department_id filter."""
        mock_response = {
            "data": [
                {
                    "id": "rt-67890",
                    "type": "recordType",
                    "attributes": {
                        "name": "Business License",
                        "status": "Published",
                        "isEnabled": True,
                    },
                }
            ],
            "links": {"self": "http://example.com/record-types"},
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types?filter%5BdepartmentID%5D=dept-123&page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_types(department_id="dept-123")

        assert len(result.data) == 1
        assert result.data[0].attributes.name == "Business License"

    def test_get_record_type(self, httpx_mock: HTTPXMock, configure_client, build_url):
        """Test retrieving a specific record type by ID."""
        mock_response = {
            "data": {
                "id": "rt-12345",
                "type": "recordType",
                "attributes": {
                    "name": "Building Permit",
                    "status": "Published",
                    "isEnabled": True,
                    "applyAccess": "Public",
                    "viewAccess": "Public",
                    "applicant": True,
                    "location": True,
                    "offlinePayments": False,
                    "renews": False,
                },
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/rt-12345"),
            json=mock_response,
        )

        result = opengov_api.get_record_type("rt-12345")

        assert result["data"]["id"] == "rt-12345"
        assert result["data"]["attributes"]["name"] == "Building Permit"
        assert result["data"]["attributes"]["status"] == "Published"
        assert result["data"]["attributes"]["isEnabled"] is True

    def test_iter_record_types_handles_pagination(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test iter_record_types automatically handles pagination."""
        # Page 1
        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types?page%5Bnumber%5D=1&page%5Bsize%5D=100"
            ),
            json={
                "data": [
                    {
                        "id": "rt-1",
                        "type": "recordType",
                        "attributes": {"name": "Type 1", "status": "Published"},
                    }
                ],
                "links": {"next": "http://example.com/record-types?page[number]=2"},
                "meta": {"page": 1, "size": 100, "totalPages": 2, "totalRecords": 101},
            },
        )

        # Page 2
        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types?page%5Bnumber%5D=2&page%5Bsize%5D=100"
            ),
            json={
                "data": [
                    {
                        "id": "rt-2",
                        "type": "recordType",
                        "attributes": {"name": "Type 2", "status": "Published"},
                    }
                ],
                "links": {},
                "meta": {"page": 2, "size": 100, "totalPages": 2, "totalRecords": 101},
            },
        )

        # Collect all record types
        record_types = list(opengov_api.iter_record_types())

        assert len(record_types) == 2
        assert record_types[0].attributes.name == "Type 1"
        assert record_types[1].attributes.name == "Type 2"


class TestRecordTypeNestedEndpoints:
    """Tests for nested record-type endpoints (attachments, fees, etc)."""

    def test_list_record_type_attachments(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing attachment templates for a record type."""
        mock_response = {
            "data": [
                {
                    "id": "rt-attachment-1",
                    "type": "recordTypeAttachment",
                    "attributes": {
                        "name": "Architectural Plans",
                        "description": "Detailed drawings",
                        "required": True,
                        "isEnabled": True,
                    },
                }
            ],
            "links": {},
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types/rt-123/attachments?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_type_attachments("rt-123")
        assert len(result["data"]) == 1
        assert result["data"][0]["attributes"]["name"] == "Architectural Plans"

    def test_get_record_type_attachment(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific attachment template."""
        mock_response = {
            "data": {
                "id": "rt-attachment-1",
                "type": "recordTypeAttachment",
                "attributes": {
                    "name": "Architectural Plans",
                    "required": True,
                },
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/attachments/rt-attachment-1"),
            json=mock_response,
        )

        result = opengov_api.get_record_type_attachment("rt-attachment-1")
        assert result["data"]["attributes"]["name"] == "Architectural Plans"

    def test_list_record_type_document_templates(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing document templates for a record type."""
        mock_response = {
            "data": [
                {
                    "id": "rt-doc-1",
                    "type": "recordTypeDocument",
                    "attributes": {
                        "docTitle": "Building Permit Certificate",
                        "documentType": "Certificate",
                    },
                }
            ],
            "links": {},
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types/rt-123/document-templates?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_type_document_templates("rt-123")
        assert len(result["data"]) == 1
        assert (
            result["data"][0]["attributes"]["docTitle"] == "Building Permit Certificate"
        )

    def test_get_record_type_document_template(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific document template."""
        mock_response = {
            "data": {
                "id": "rt-doc-1",
                "type": "recordTypeDocument",
                "attributes": {"docTitle": "Permit Certificate"},
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/document-templates/rt-doc-1"),
            json=mock_response,
        )

        result = opengov_api.get_record_type_document_template("rt-doc-1")
        assert result["data"]["attributes"]["docTitle"] == "Permit Certificate"

    def test_list_record_type_fees(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing fee templates for a record type."""
        mock_response = {
            "data": [
                {
                    "id": "rt-fee-1",
                    "type": "recordTypeFee",
                    "attributes": {
                        "label": "Processing Fee",
                        "accountNumber": "ACC-123",
                        "isEnabled": True,
                    },
                }
            ],
            "links": {},
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types/rt-123/fees?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_type_fees("rt-123")
        assert len(result["data"]) == 1
        assert result["data"][0]["attributes"]["label"] == "Processing Fee"

    def test_get_record_type_fee(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific fee template."""
        mock_response = {
            "data": {
                "id": "rt-fee-1",
                "type": "recordTypeFee",
                "attributes": {"label": "Processing Fee"},
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/fees/rt-fee-1"),
            json=mock_response,
        )

        result = opengov_api.get_record_type_fee("rt-fee-1")
        assert result["data"]["attributes"]["label"] == "Processing Fee"

    def test_get_record_type_form(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting form fields for a record type."""
        mock_response = {
            "data": {
                "id": "rt-form-1",
                "type": "recordTypeForm",
                "attributes": {
                    "fields": [
                        {
                            "id": "field-1",
                            "label": "Applicant Name",
                            "formFieldType": "SHORT_TEXT",
                            "required": True,
                        }
                    ]
                },
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/rt-123/form"),
            json=mock_response,
        )

        result = opengov_api.get_record_type_form("rt-123")
        assert len(result["data"]["attributes"]["fields"]) == 1
        assert result["data"]["attributes"]["fields"][0]["label"] == "Applicant Name"

    def test_list_record_type_workflow(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test listing workflow step templates for a record type."""
        mock_response = {
            "data": [
                {
                    "id": "rt-step-1",
                    "type": "recordTypeTemplateStep",
                    "attributes": {
                        "label": "Plan Review",
                        "stepType": "APPROVAL",
                        "sequence": True,
                    },
                }
            ],
            "links": {},
            "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
        }

        httpx_mock.add_response(
            url=build_url(
                "testcommunity/record-types/rt-123/workflow?page%5Bnumber%5D=1&page%5Bsize%5D=20"
            ),
            json=mock_response,
        )

        result = opengov_api.list_record_type_workflow("rt-123")
        assert len(result["data"]) == 1
        assert result["data"][0]["attributes"]["label"] == "Plan Review"

    def test_get_record_type_workflow_step(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test getting a specific workflow step template."""
        mock_response = {
            "data": {
                "id": "rt-step-1",
                "type": "recordTypeTemplateStep",
                "attributes": {"label": "Plan Review", "stepType": "APPROVAL"},
            }
        }

        httpx_mock.add_response(
            url=build_url("testcommunity/record-types/rt-123/workflow/rt-step-1"),
            json=mock_response,
        )

        result = opengov_api.get_record_type_workflow_step("rt-123", "rt-step-1")
        assert result["data"]["attributes"]["label"] == "Plan Review"
