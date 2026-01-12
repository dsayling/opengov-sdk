"""Enums for OpenGov API."""

from enum import Enum


class RecordStatus(str, Enum):
    """Record status enum."""

    STOPPED = "STOPPED"
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"


class WorkflowStepStatus(str, Enum):
    """Workflow step status enum."""

    REJECTED = "REJECTED"
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    SKIPPED = "SKIPPED"
    ON_HOLD = "ON_HOLD"


class StepKind(str, Enum):
    """Workflow step kind enum."""

    APPROVAL = "APPROVAL"
    PAYMENT = "PAYMENT"
    INSPECTION = "INSPECTION"
    DOCUMENT = "DOCUMENT"
    API_INTEGRATION = "API_INTEGRATION"
    ASSET_MANAGEMENT = "ASSET_MANAGEMENT"
    RELATED_RECORD = "RELATED_RECORD"
    SHADOW = "SHADOW"
    REVIEW = "REVIEW"
