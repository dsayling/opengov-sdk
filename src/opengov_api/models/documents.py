"""Document Step models for OpenGov API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .enums import DocumentStepStatus, DocumentType, StepKind


class DocumentStepAttributes(BaseModel):
    """Document step attributes."""

    label: str | None = None
    step_type: StepKind = Field(..., alias="stepType")
    ordinal: int | None = None
    sequence: bool | None = None
    status: DocumentStepStatus
    activated_at: datetime | None = Field(None, alias="activatedAt")
    completed_at: datetime | None = Field(None, alias="completedAt")
    document_title: str | None = Field(None, alias="documentTitle")
    date_issued: datetime | None = Field(None, alias="dateIssued")
    expires_at: datetime | None = Field(None, alias="expiresAt")
    document_type: DocumentType = Field(..., alias="documentType")
    html: str | None = None
    portrait: bool | None = None
    public_can_print: bool | None = Field(None, alias="publicCanPrint")
    created_at: datetime | None = Field(None, alias="createdAt")
    last_updated_by_user_id: str | None = Field(None, alias="lastUpdatedByUserID")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class DocumentStepResource(BaseModel):
    """Document step resource object."""

    id: str
    type: str
    attributes: DocumentStepAttributes
    relationships: dict[str, Any] | None = None
    links: dict[str, str] | None = None
