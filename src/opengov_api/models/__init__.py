"""Models for OpenGov API."""

from .base import (
    JSONAPIResponse,
    Links,
    Meta,
    Relationship,
    RelationshipData,
    ResourceObject,
)
from .enums import RecordStatus, StepKind, WorkflowStepStatus
from .params import DateRangeFilter, ListRecordsParams, PageParams
from .records import (
    RecordAttributes,
    RecordCreateAttributes,
    RecordCreateData,
    RecordCreateRequest,
    RecordResource,
    RecordUpdateAttributes,
    RecordUpdateData,
    RecordUpdateRequest,
)

__all__ = [
    # Base JSON:API models
    "JSONAPIResponse",
    "Links",
    "Meta",
    "Relationship",
    "RelationshipData",
    "ResourceObject",
    # Enums
    "RecordStatus",
    "StepKind",
    "WorkflowStepStatus",
    # Params
    "DateRangeFilter",
    "ListRecordsParams",
    "PageParams",
    # Records
    "RecordAttributes",
    "RecordCreateAttributes",
    "RecordCreateData",
    "RecordCreateRequest",
    "RecordResource",
    "RecordUpdateAttributes",
    "RecordUpdateData",
    "RecordUpdateRequest",
]
