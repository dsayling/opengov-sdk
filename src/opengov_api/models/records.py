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
