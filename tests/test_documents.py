"""
Tests for document-specific endpoint behaviors.

Infrastructure and common endpoint tests are in test_infrastructure.py
and test_common_endpoints.py. This file tests behaviors unique to the
document steps resource.
"""

import re
from datetime import date, datetime

from pytest_httpx import HTTPXMock

import opengov_api
from opengov_api.models import DateRangeFilter, DocumentStepStatus


def make_document_step_attrs(**kwargs):
    """Helper to create valid DocumentStepAttributes with required fields."""
    base = {
        "label": "Test Step",
        "stepType": "DOCUMENT",
        "status": "COMPLETE",
        "documentType": "Permit/License",
    }
    base.update(kwargs)
    return base


class TestDocumentStepsFiltering:
    """Tests for document steps filtering functionality."""

    def test_list_document_steps_with_record_id_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps filtered by record ID."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Generate Certificate", status="COMPLETE"
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        response = opengov_api.list_document_steps(record_id="record-12345")

        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0].id == "doc-step-1"
        assert response.data[0].attributes.label == "Generate Certificate"

        # Verify the filter was sent in the request
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5BrecordID%5D=record-12345" in str(
            request.url
        ) or "filter[recordID]=record-12345" in str(request.url)

    def test_list_document_steps_with_status_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps filtered by status."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Active Step", status="ACTIVE"
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        response = opengov_api.list_document_steps(status=DocumentStepStatus.ACTIVE)

        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0].attributes.status == "ACTIVE"

        # Verify the filter was sent in the request
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5Bstatus%5D=ACTIVE" in str(
            request.url
        ) or "filter[status]=ACTIVE" in str(request.url)

    def test_list_document_steps_with_label_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps filtered by label."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Building Permit", status="COMPLETE"
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        response = opengov_api.list_document_steps(label="Building Permit")

        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0].attributes.label == "Building Permit"

        # Verify the filter was sent in the request
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5Blabel%5D=Building" in str(
            request.url
        ) or "filter[label]=Building" in str(request.url)

    def test_list_document_steps_with_date_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps with simple date filter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Certificate",
                            status="COMPLETE",
                            completedAt="2025-03-15T10:00:00Z",
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        filter_date = date(2025, 3, 1)
        response = opengov_api.list_document_steps(completed_at=filter_date)

        assert isinstance(response.data, list)
        assert len(response.data) == 1

        # Verify the filter was sent in the request
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5BcompletedAt%5D=2025-03-01" in str(
            request.url
        ) or "filter[completedAt]=2025-03-01" in str(request.url)

    def test_list_document_steps_with_date_range_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps with date range filter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Recent Document",
                            status="COMPLETE",
                            activatedAt="2025-03-10T10:00:00Z",
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        date_range = DateRangeFilter(gte=date(2025, 3, 1), lt=date(2025, 4, 1))
        response = opengov_api.list_document_steps(activated_at=date_range)

        assert isinstance(response.data, list)
        assert len(response.data) == 1

        # Verify the filter was sent in the request
        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        # Check for URL-encoded nested brackets %5B%5D
        assert (
            "filter%5BactivatedAt%5D%5Bgte%5D=2025-03-01" in url_str
            or "filter[activatedAt][gte]=2025-03-01" in url_str
        )
        assert (
            "filter%5BactivatedAt%5D%5Blt%5D=2025-04-01" in url_str
            or "filter[activatedAt][lt]=2025-04-01" in url_str
        )

    def test_list_document_steps_with_multiple_filters(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps with multiple filters."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Certificate", status="COMPLETE"
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        response = opengov_api.list_document_steps(
            record_id="record-12345",
            status=DocumentStepStatus.COMPLETE,
            label="Certificate",
        )

        assert isinstance(response.data, list)
        assert len(response.data) == 1

        # Verify all filters were sent
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5BrecordID%5D=record-12345" in str(
            request.url
        ) or "filter[recordID]=record-12345" in str(request.url)
        assert "filter%5Bstatus%5D=COMPLETE" in str(
            request.url
        ) or "filter[status]=COMPLETE" in str(request.url)
        assert "filter%5Blabel%5D=Certificate" in str(
            request.url
        ) or "filter[label]=Certificate" in str(request.url)


class TestDocumentStepsPagination:
    """Tests for document steps pagination."""

    def test_list_document_steps_with_pagination(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps with pagination parameters."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": f"doc-step-{i}",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label=f"Step {i}", status="COMPLETE"
                        ),
                    }
                    for i in range(1, 6)
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps",
                    "next": "https://api.example.com/v2/testcommunity/document-steps?page[number]=2",
                    "last": "https://api.example.com/v2/testcommunity/document-steps?page[number]=3",
                },
                "meta": {"page": 1, "size": 5, "totalPages": 3, "totalRecords": 15},
            },
        )

        response = opengov_api.list_document_steps(page_number=1, page_size=5)

        assert isinstance(response.data, list)
        assert len(response.data) == 5
        assert response.current_page() == 1
        assert response.total_pages() == 3
        assert response.total_records() == 15
        assert response.has_next_page()
        assert not response.has_prev_page()

        # Verify pagination params
        request = httpx_mock.get_request()
        assert request is not None
        assert "page%5Bnumber%5D=1" in str(request.url) or "page[number]=1" in str(
            request.url
        )
        assert "page%5Bsize%5D=5" in str(request.url) or "page[size]=5" in str(
            request.url
        )


class TestIterDocumentSteps:
    """Tests for iter_document_steps auto-pagination functionality."""

    def test_iter_document_steps_single_page(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test iterating through document steps with a single page."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": f"doc-step-{i}",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label=f"Step {i}", status="COMPLETE"
                        ),
                    }
                    for i in range(1, 4)
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 100, "totalPages": 1, "totalRecords": 3},
            },
        )

        steps = list(opengov_api.iter_document_steps())

        assert len(steps) == 3
        assert steps[0].id == "doc-step-1"
        assert steps[1].id == "doc-step-2"
        assert steps[2].id == "doc-step-3"

    def test_iter_document_steps_multiple_pages(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test iterating through document steps across multiple pages."""
        # Mock first page
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*page.*number.*=1.*"),
            json={
                "data": [
                    {
                        "id": f"doc-step-{i}",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label=f"Step {i}", status="ACTIVE"
                        ),
                    }
                    for i in range(1, 3)
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps",
                    "next": "https://api.example.com/v2/testcommunity/document-steps?page[number]=2",
                },
                "meta": {"page": 1, "size": 2, "totalPages": 2, "totalRecords": 4},
            },
        )

        # Mock second page
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*page.*number.*=2.*"),
            json={
                "data": [
                    {
                        "id": f"doc-step-{i}",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label=f"Step {i}", status="ACTIVE"
                        ),
                    }
                    for i in range(3, 5)
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps?page[number]=2",
                },
                "meta": {"page": 2, "size": 2, "totalPages": 2, "totalRecords": 4},
            },
        )

        steps = list(opengov_api.iter_document_steps(page_size=2))

        assert len(steps) == 4
        assert steps[0].id == "doc-step-1"
        assert steps[1].id == "doc-step-2"
        assert steps[2].id == "doc-step-3"
        assert steps[3].id == "doc-step-4"

        # Verify both pages were fetched
        requests = httpx_mock.get_requests()
        assert len(requests) == 2

    def test_iter_document_steps_with_filters(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test iterating through document steps with filters applied."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Active Step", status="ACTIVE"
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 100, "totalPages": 1, "totalRecords": 1},
            },
        )

        steps = list(
            opengov_api.iter_document_steps(
                status=DocumentStepStatus.ACTIVE,
                record_id="record-12345",
            )
        )

        assert len(steps) == 1
        assert steps[0].attributes.status == "ACTIVE"

        # Verify filters were applied
        request = httpx_mock.get_request()
        assert request is not None
        assert "filter%5Bstatus%5D=ACTIVE" in str(
            request.url
        ) or "filter[status]=ACTIVE" in str(request.url)
        assert "filter%5BrecordID%5D=record-12345" in str(
            request.url
        ) or "filter[recordID]=record-12345" in str(request.url)

    def test_iter_document_steps_empty_result(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test iterating through document steps with no results."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 100, "totalPages": 0, "totalRecords": 0},
            },
        )

        steps = list(opengov_api.iter_document_steps())

        assert len(steps) == 0


class TestDocumentStepsEdgeCases:
    """Tests for edge cases and special behaviors."""

    def test_get_document_step_with_special_characters(
        self, httpx_mock: HTTPXMock, configure_client, build_url
    ):
        """Test get_document_step handles special characters in IDs."""
        document_step_id = "document-step-123-abc"
        httpx_mock.add_response(
            url=build_url(f"testcommunity/document-steps/{document_step_id}"),
            json={
                "id": document_step_id,
                "type": "documentStep",
                "attributes": make_document_step_attrs(label="Special Document"),
            },
        )

        result = opengov_api.get_document_step(document_step_id)
        assert result["id"] == document_step_id
        assert result["attributes"]["label"] == "Special Document"

    def test_list_document_steps_with_datetime_filter(
        self, httpx_mock: HTTPXMock, configure_client
    ):
        """Test listing document steps with datetime filter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r".*/document-steps.*"),
            json={
                "data": [
                    {
                        "id": "doc-step-1",
                        "type": "documentStep",
                        "attributes": make_document_step_attrs(
                            label="Recent",
                            status="COMPLETE",
                            completedAt="2025-03-15T14:30:00Z",
                        ),
                    }
                ],
                "links": {
                    "self": "https://api.example.com/v2/testcommunity/document-steps"
                },
                "meta": {"page": 1, "size": 20, "totalPages": 1, "totalRecords": 1},
            },
        )

        filter_datetime = datetime(2025, 3, 15, 10, 0, 0)
        response = opengov_api.list_document_steps(completed_at=filter_datetime)

        assert isinstance(response.data, list)
        assert len(response.data) == 1

        # Verify datetime was formatted correctly
        request = httpx_mock.get_request()
        assert request is not None
        # Colons are URL-encoded as %3A
        url_str = str(request.url)
        assert (
            "filter%5BcompletedAt%5D=2025-03-15T10%3A00%3A00" in url_str
            or "filter[completedAt]=2025-03-15T10:00:00" in url_str
        )
