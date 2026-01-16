"""Record models for OpenGov API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator

from .enums import ChangeRequestStatus, RecordStatus, WorkflowStepStatus


class RecordAttributes(BaseModel):
    """Record attributes."""

    number: str | None = None
    hist_id: str | None = Field(None, alias="histID")
    hist_number: str | None = Field(None, alias="histNumber")
    type_description: str | None = Field(None, alias="typeDescription")
    status: RecordStatus | None = None
    is_enabled: bool | None = Field(None, alias="isEnabled")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    expires_at: datetime | None = Field(None, alias="expiresAt")
    renewal_of_record_id: str | None = Field(None, alias="renewalOfRecordID")
    renewal_number: float | None = Field(None, alias="renewalNumber")
    submitted_online: bool | None = Field(None, alias="submittedOnline")
    renewal_submitted: bool | None = Field(None, alias="renewalSubmitted")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    created_by: str | None = Field(None, alias="createdBy")
    updated_by: str | None = Field(None, alias="updatedBy")

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

    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None
    phone_no: str | None = Field(None, alias="phoneNo")
    address: str | None = None
    address_2: str | None = Field(None, alias="address2")
    city: str | None = None
    state: str | None = None
    zip_code: str | None = Field(None, alias="zip")

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

    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_type: str | None = Field(None, alias="locationType")
    owner_name: str | None = Field(None, alias="ownerName")
    owner_street_number: str | None = Field(None, alias="ownerStreetNumber")
    owner_street_name: str | None = Field(None, alias="ownerStreetName")
    owner_unit: str | None = Field(None, alias="ownerUnit")
    owner_city: str | None = Field(None, alias="ownerCity")
    owner_state: str | None = Field(None, alias="ownerState")
    owner_postal_code: str | None = Field(None, alias="ownerPostalCode")
    owner_country: str | None = Field(None, alias="ownerCountry")
    owner_phone_no: str | None = Field(None, alias="ownerPhoneNo")
    owner_email: str | None = Field(None, alias="ownerEmail")
    street_no: str | None = Field(None, alias="streetNo")
    street_name: str | None = Field(None, alias="streetName")
    unit: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = Field(None, alias="postalCode")
    country: str | None = None
    secondary_latitude: float | None = Field(None, alias="secondaryLatitude")
    secondary_longitude: float | None = Field(None, alias="secondaryLongitude")
    segment_primary_label: str | None = Field(None, alias="segmentPrimaryLabel")
    segment_secondary_label: str | None = Field(None, alias="segmentSecondaryLabel")
    segment_label: str | None = Field(None, alias="segmentLabel")
    segment_length: float | None = Field(None, alias="segmentLength")
    lot_area: float | None = Field(None, alias="lotArea")
    mat_id: str | None = Field(None, alias="matID")
    mbl: str | None = None
    occupancy_type: str | None = Field(None, alias="occupancyType")
    property_use: str | None = Field(None, alias="propertyUse")
    sewage: str | None = None
    water: str | None = None
    year_built: float | None = Field(None, alias="yearBuilt")
    zoning: str | None = None
    building_type: str | None = Field(None, alias="buildingType")
    notes: str | None = None
    subdivision: str | None = None
    archived: bool | None = None
    updated_at: datetime | None = Field(None, alias="updatedAt")
    gis_id: str | None = Field(None, alias="gisID")

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
    """Record attachment attributes."""

    name: str | None = None
    description: str | None = None
    attachment_template_id: str | None = Field(None, alias="attachmentTemplateID")
    record_id: str | None = Field(None, alias="recordID")
    required: bool | None = None
    order_number: float | None = Field(None, alias="orderNumber")
    url: str | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    created_by: str | None = Field(None, alias="createdBy")
    updated_by: str | None = Field(None, alias="updatedBy")

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

    label: str
    step_type: str = Field(..., alias="stepType")
    ordinal: int | None = None
    sequence: bool | None = None
    status: WorkflowStepStatus
    activated_at: datetime | None = Field(None, alias="activatedAt")
    completed_at: datetime | None = Field(None, alias="completedAt")

    model_config = {"populate_by_name": True}

    @field_validator("activated_at", "completed_at", mode="before")
    @classmethod
    def set_empty_datetime_to_none(cls, v):
        if v == "":
            return None
        return v


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

    comment_type: str | None = Field(None, alias="commentType")
    comment: str | None = None
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

    label: str | None = None
    ordinal: int | None = None

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

    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")

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

    overall_note: str | None = Field(None, alias="overallNote")
    version: str | None = None
    requested_by: str | None = Field(None, alias="requestedBy")
    responded_by: str | None = Field(None, alias="respondedBy")
    status: ChangeRequestStatus | None = None
    created_at: datetime | None = Field(None, alias="createdAt")
    completed_at: datetime | None = Field(None, alias="completedAt")
    form_fields: list[dict[str, Any]] | None = Field(None, alias="formFields")
    attachments: list[dict[str, Any]] | None = None

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

    fields: list[dict[str, Any]] | None = None

    model_config = {"populate_by_name": True}


class CollectionEntryResource(BaseModel):
    """Collection entry resource object."""

    id: str
    type: str
    attributes: CollectionEntryAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None
