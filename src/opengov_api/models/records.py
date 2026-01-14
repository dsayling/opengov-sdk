"""Record models for OpenGov API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .enums import RecordStatus


class RecordAttributes(BaseModel):
    """Record attributes."""

    name: str | None = None
    number: str | None = None
    status: RecordStatus | None = None
    hist_id: str | None = Field(None, alias="histID")
    hist_number: str | None = Field(None, alias="histNumber")
    description: str | None = None
    is_enabled: bool | None = Field(None, alias="isEnabled")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    expires_at: datetime | None = Field(None, alias="expiresAt")
    renewal_submitted: bool | None = Field(None, alias="renewalSubmitted")
    submitted_online: bool | None = Field(None, alias="submittedOnline")
    renewal_number: str | None = Field(None, alias="renewalNumber")

    model_config = {"populate_by_name": True}


class RecordResource(BaseModel):
    """Record resource object."""

    id: str
    type: str
    attributes: RecordAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


class RecordCreateAttributes(BaseModel):
    """Attributes for creating a record."""

    name: str
    description: str | None = None
    # Add other required/optional fields based on your API needs


class RecordCreateData(BaseModel):
    """Data wrapper for creating a record."""

    type: str = "records"
    attributes: RecordCreateAttributes
    relationships: dict[str, Any] | None = None


class RecordCreateRequest(BaseModel):
    """Request body for creating a record."""

    data: RecordCreateData


class RecordUpdateAttributes(BaseModel):
    """Attributes for updating a record."""

    name: str | None = None
    description: str | None = None
    status: RecordStatus | None = None
    # Add other updatable fields


class RecordUpdateData(BaseModel):
    """Data wrapper for updating a record."""

    type: str = "records"
    attributes: RecordUpdateAttributes


class RecordUpdateRequest(BaseModel):
    """Request body for updating a record."""

    data: RecordUpdateData


# Guest models
class GuestAttributes(BaseModel):
    """Guest attributes."""

    email: str | None = None
    name: str | None = None
    user_id: str | None = Field(None, alias="userID")
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True}


class GuestResource(BaseModel):
    """Guest resource object."""

    id: str
    type: str
    attributes: GuestAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Location models
class LocationAttributes(BaseModel):
    """Location attributes."""

    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class LocationResource(BaseModel):
    """Location resource object."""

    id: str
    type: str
    attributes: LocationAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Attachment models
class AttachmentAttributes(BaseModel):
    """Attachment attributes."""

    filename: str | None = None
    content_type: str | None = Field(None, alias="contentType")
    size: int | None = None
    url: str | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    created_by: str | None = Field(None, alias="createdBy")

    model_config = {"populate_by_name": True}


class AttachmentResource(BaseModel):
    """Attachment resource object."""

    id: str
    type: str
    attributes: AttachmentAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Workflow Step models
class WorkflowStepAttributes(BaseModel):
    """Workflow step attributes."""

    name: str | None = None
    status: str | None = None
    step_type: str | None = Field(None, alias="stepType")
    assigned_to: str | None = Field(None, alias="assignedTo")
    due_date: datetime | None = Field(None, alias="dueDate")
    completed_at: datetime | None = Field(None, alias="completedAt")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class WorkflowStepResource(BaseModel):
    """Workflow step resource object."""

    id: str
    type: str
    attributes: WorkflowStepAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Workflow Step Comment models
class WorkflowStepCommentAttributes(BaseModel):
    """Workflow step comment attributes."""

    text: str | None = None
    created_by: str | None = Field(None, alias="createdBy")
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True}


class WorkflowStepCommentResource(BaseModel):
    """Workflow step comment resource object."""

    id: str
    type: str
    attributes: WorkflowStepCommentAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Collection models
class CollectionAttributes(BaseModel):
    """Collection attributes."""

    name: str | None = None
    collection_type: str | None = Field(None, alias="collectionType")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class CollectionResource(BaseModel):
    """Collection resource object."""

    id: str
    type: str
    attributes: CollectionAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Form models
class FormResource(BaseModel):
    """Form resource object. Note: Forms use a non-standard API response format."""

    fields: list[dict[str, Any]]


# Applicant models
class ApplicantAttributes(BaseModel):
    """Applicant attributes."""

    user_id: str | None = Field(None, alias="userID")
    name: str | None = None
    email: str | None = None
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True}


class ApplicantResource(BaseModel):
    """Applicant resource object."""

    id: str
    type: str
    attributes: ApplicantAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Change Request models
class ChangeRequestAttributes(BaseModel):
    """Change request attributes."""

    status: str | None = None
    requested_by: str | None = Field(None, alias="requestedBy")
    requested_at: datetime | None = Field(None, alias="requestedAt")
    approved_by: str | None = Field(None, alias="approvedBy")
    approved_at: datetime | None = Field(None, alias="approvedAt")
    changes: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


class ChangeRequestResource(BaseModel):
    """Change request resource object."""

    id: str
    type: str
    attributes: ChangeRequestAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None


# Collection Entry models
class CollectionEntryAttributes(BaseModel):
    """Collection entry attributes."""

    data: dict[str, Any] | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class CollectionEntryResource(BaseModel):
    """Collection entry resource object."""

    id: str
    type: str
    attributes: CollectionEntryAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None
