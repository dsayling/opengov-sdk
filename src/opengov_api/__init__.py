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

# Endpoint functions
from .records import (
    list_records,
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
    # Records
    "list_records",
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
