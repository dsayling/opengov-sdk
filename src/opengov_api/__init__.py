"""
OpenGov API SDK - Python client for OpenGov APIs.

A functional factory pattern SDK for interacting with OpenGov APIs.

Example:
    >>> import opengov_api
    >>> opengov_api.set_api_key("your-api-key")
    >>> opengov_api.set_community("your-community")
    >>> records = opengov_api.list_records()
    >>> users = opengov_api.list_users()
"""

# Configuration functions
from .client import (
    set_api_key,
    set_base_url,
    set_community,
    set_timeout,
    get_api_key,
    get_base_url,
    get_community,
    get_timeout,
)

# Models
from .models import (
    DateRangeFilter,
    DocumentStepResource,
    DocumentStepStatus,
    DocumentType,
    JSONAPIResponse,
    Links,
    ListDocumentStepsParams,
    Meta,
    RecordAttributes,
    RecordCreateRequest,
    RecordResource,
    RecordStatus,
    RecordUpdateRequest,
    StepKind,
    WorkflowStepStatus,
)

# Endpoint functions
from .records import (
    list_records,
    iter_records,
    iter_record_guests,
    iter_record_additional_locations,
    iter_record_attachments,
    iter_record_workflow_steps,
    iter_record_workflow_step_comments,
    iter_record_collections,
    get_record,
    create_record,
    update_record,
    archive_record,
    get_record_form,
    update_record_form,
    get_record_applicant,
    update_record_applicant,
    remove_record_applicant,
    list_record_guests,
    add_record_guest,
    get_record_guest,
    remove_record_guest,
    get_record_primary_location,
    update_record_primary_location,
    remove_record_primary_location,
    list_record_additional_locations,
    add_record_additional_location,
    get_record_additional_location,
    remove_record_additional_location,
    list_record_attachments,
    add_record_attachment,
    get_record_attachment,
    remove_record_attachment,
    get_record_change_request,
    get_most_recent_record_change_request,
    create_record_change_request,
    cancel_record_change_request,
    list_record_workflow_steps,
    create_record_workflow_step,
    get_record_workflow_step,
    update_record_workflow_step,
    delete_record_workflow_step,
    list_record_workflow_step_comments,
    create_record_workflow_step_comment,
    get_record_workflow_step_comment,
    delete_record_workflow_step_comment,
    list_record_collections,
    get_record_collection,
    create_record_collection_entry,
    get_record_collection_entry,
    update_record_collection_entry,
)
from .users import list_users, get_user, create_user, list_user_flags
from .locations import (
    list_locations,
    get_location,
    create_location,
    update_location,
    delete_location,
    list_location_flags,
)
from .approvals import (
    list_approval_steps,
    get_approval_step,
    update_approval_step,
)
from .documents import (
    list_document_steps,
    iter_document_steps,
    get_document_step,
)
from .inspections import (
    list_inspection_steps,
    get_inspection_step,
    update_inspection_step,
    list_inspection_types,
    create_inspection_type,
)
from .files import (
    list_files,
    get_file,
    create_file_upload,
)
from .projects import (
    list_projects,
    get_project,
)

# Exceptions
from .exceptions import (
    OpenGovAPIError,
    OpenGovConfigurationError,
    OpenGovAPIConnectionError,
    OpenGovAPITimeoutError,
    OpenGovResponseParseError,
    OpenGovAPIStatusError,
    OpenGovBadRequestError,
    OpenGovAuthenticationError,
    OpenGovPermissionDeniedError,
    OpenGovNotFoundError,
    OpenGovRateLimitError,
    OpenGovInternalServerError,
)

__all__ = [
    # Configuration
    "set_api_key",
    "set_base_url",
    "set_community",
    "set_timeout",
    "get_api_key",
    "get_base_url",
    "get_community",
    "get_timeout",
    # Models
    "DateRangeFilter",
    "DocumentStepResource",
    "DocumentStepStatus",
    "DocumentType",
    "JSONAPIResponse",
    "Links",
    "ListDocumentStepsParams",
    "Meta",
    "RecordAttributes",
    "RecordCreateRequest",
    "RecordResource",
    "RecordStatus",
    "RecordUpdateRequest",
    "StepKind",
    "WorkflowStepStatus",
    # Records
    "list_records",
    "iter_records",
    "iter_record_guests",
    "iter_record_additional_locations",
    "iter_record_attachments",
    "iter_record_workflow_steps",
    "iter_record_workflow_step_comments",
    "iter_record_collections",
    "get_record",
    "create_record",
    "update_record",
    "archive_record",
    "get_record_form",
    "update_record_form",
    "get_record_applicant",
    "update_record_applicant",
    "remove_record_applicant",
    "list_record_guests",
    "add_record_guest",
    "get_record_guest",
    "remove_record_guest",
    "get_record_primary_location",
    "update_record_primary_location",
    "remove_record_primary_location",
    "list_record_additional_locations",
    "add_record_additional_location",
    "get_record_additional_location",
    "remove_record_additional_location",
    "list_record_attachments",
    "add_record_attachment",
    "get_record_attachment",
    "remove_record_attachment",
    "get_record_change_request",
    "get_most_recent_record_change_request",
    "create_record_change_request",
    "cancel_record_change_request",
    "list_record_workflow_steps",
    "create_record_workflow_step",
    "get_record_workflow_step",
    "update_record_workflow_step",
    "delete_record_workflow_step",
    "list_record_workflow_step_comments",
    "create_record_workflow_step_comment",
    "get_record_workflow_step_comment",
    "delete_record_workflow_step_comment",
    "list_record_collections",
    "get_record_collection",
    "create_record_collection_entry",
    "get_record_collection_entry",
    "update_record_collection_entry",
    # Users
    "list_users",
    "get_user",
    "create_user",
    "list_user_flags",
    # Locations
    "list_locations",
    "get_location",
    "create_location",
    "update_location",
    "delete_location",
    "list_location_flags",
    # Approval Steps
    "list_approval_steps",
    "get_approval_step",
    "update_approval_step",
    # Document Steps
    "list_document_steps",
    "iter_document_steps",
    "get_document_step",
    # Inspection Steps
    "list_inspection_steps",
    "get_inspection_step",
    "update_inspection_step",
    "list_inspection_types",
    "create_inspection_type",
    # Files
    "list_files",
    "get_file",
    "create_file_upload",
    # Projects
    "list_projects",
    "get_project",
    # Exceptions
    "OpenGovAPIError",
    "OpenGovConfigurationError",
    "OpenGovAPIConnectionError",
    "OpenGovAPITimeoutError",
    "OpenGovResponseParseError",
    "OpenGovAPIStatusError",
    "OpenGovBadRequestError",
    "OpenGovAuthenticationError",
    "OpenGovPermissionDeniedError",
    "OpenGovNotFoundError",
    "OpenGovRateLimitError",
    "OpenGovInternalServerError",
]
