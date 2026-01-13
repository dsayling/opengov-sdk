"""Record Type models for OpenGov API."""

from datetime import datetime
from pydantic import BaseModel, Field


class RecordTypeAttributes(BaseModel):
    """Record Type attributes."""

    name: str | None = None
    apply_access: str | None = Field(None, alias="applyAccess")
    is_enabled: bool | None = Field(None, alias="isEnabled")
    applicant: bool | None = None
    location: bool | None = None
    offline_payments: bool | None = Field(None, alias="offlinePayments")
    view_access: str | None = Field(None, alias="viewAccess")
    allow_projects: bool | None = Field(None, alias="allowProjects")
    htmlcontent: str | None = None
    status: str | None = None
    renews: bool | None = None
    order_no: int | None = Field(None, alias="orderNo")
    ad_hoc_attachment_view_access: str | None = Field(
        None, alias="adHocAttachmentViewAccess"
    )
    cloned_date: datetime | None = Field(None, alias="clonedDate")
    parent_record_type_id: str | None = Field(None, alias="parentRecordTypeID")
    allow_point_locations: bool | None = Field(None, alias="allowPointLocations")
    allow_address_locations: bool | None = Field(None, alias="allowAddressLocations")
    allow_segment_locations: bool | None = Field(None, alias="allowSegmentLocations")
    max_locations: int | None = Field(None, alias="maxLocations")
    point_locations_help_text: str | None = Field(None, alias="pointLocationsHelpText")
    address_locations_help_text: str | None = Field(
        None, alias="addressLocationsHelpText"
    )
    segment_locations_help_text: str | None = Field(
        None, alias="segmentLocationsHelpText"
    )
    allow_additional_locations: bool | None = Field(
        None, alias="allowAdditionalLocations"
    )
    automatic_expiration_date_extension: bool | None = Field(
        None, alias="automaticExpirationDateExtension"
    )
    automatic_project_records_expiration_date_extension: bool | None = Field(
        None, alias="automaticProjectRecordsExpirationDateExtension"
    )
    disable_record_attachments: bool | None = Field(
        None, alias="disableRecordAttachments"
    )
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    created_by: str | None = Field(None, alias="createdBy")
    updated_by: str | None = Field(None, alias="updatedBy")

    model_config = {"populate_by_name": True}


class RecordTypeResource(BaseModel):
    """Record Type resource object."""

    id: str
    type: str
    attributes: RecordTypeAttributes
    relationships: dict | None = None
    links: dict[str, str] | None = None
