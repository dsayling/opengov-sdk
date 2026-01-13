"""Models for OpenGov API."""

from .base import (
    JSONAPIResponse,
    Links,
    Meta,
    Relationship,
    RelationshipData,
    ResourceObject,
)
from .documents import DocumentStepAttributes, DocumentStepResource
from .enums import (
    DocumentStepStatus,
    DocumentType,
    RecordStatus,
    StepKind,
    WorkflowStepStatus,
)
from .params import (
    BaseListParams,
    DateRangeFilter,
    ListDocumentStepsParams,
    ListRecordAdditionalLocationsParams,
    ListRecordAttachmentsParams,
    ListRecordCollectionsParams,
    ListRecordGuestsParams,
    ListRecordsParams,
    ListRecordTypesParams,
    ListRecordWorkflowStepCommentsParams,
    ListRecordWorkflowStepsParams,
    PageParams,
)
from .records import (
    AttachmentAttributes,
    AttachmentResource,
    CollectionAttributes,
    CollectionResource,
    GuestAttributes,
    GuestResource,
    LocationAttributes,
    LocationResource,
    RecordAttributes,
    RecordCreateAttributes,
    RecordCreateData,
    RecordCreateRequest,
    RecordResource,
    RecordUpdateAttributes,
    RecordUpdateData,
    RecordUpdateRequest,
    WorkflowStepAttributes,
    WorkflowStepCommentAttributes,
    WorkflowStepCommentResource,
    WorkflowStepResource,
)
from .record_types import RecordTypeAttributes, RecordTypeResource

__all__ = [
    # Base JSON:API models
    "JSONAPIResponse",
    "Links",
    "Meta",
    "Relationship",
    "RelationshipData",
    "ResourceObject",
    # Enums
    "DocumentStepStatus",
    "DocumentType",
    "RecordStatus",
    "StepKind",
    "WorkflowStepStatus",
    # Params
    "BaseListParams",
    "DateRangeFilter",
    "ListDocumentStepsParams",
    "ListRecordsParams",
    "ListRecordGuestsParams",
    "ListRecordAdditionalLocationsParams",
    "ListRecordAttachmentsParams",
    "ListRecordWorkflowStepsParams",
    "ListRecordWorkflowStepCommentsParams",
    "ListRecordCollectionsParams",
    "ListRecordTypesParams",
    "PageParams",
    # Documents
    "DocumentStepAttributes",
    "DocumentStepResource",
    # Records
    "RecordAttributes",
    "RecordCreateAttributes",
    "RecordCreateData",
    "RecordCreateRequest",
    "RecordResource",
    "RecordUpdateAttributes",
    "RecordUpdateData",
    "RecordUpdateRequest",
    # Nested resources
    "GuestAttributes",
    "GuestResource",
    "LocationAttributes",
    "LocationResource",
    "AttachmentAttributes",
    "AttachmentResource",
    "WorkflowStepAttributes",
    "WorkflowStepResource",
    "WorkflowStepCommentAttributes",
    "WorkflowStepCommentResource",
    "CollectionAttributes",
    "CollectionResource",
    # Record Types
    "RecordTypeAttributes",
    "RecordTypeResource",
]
