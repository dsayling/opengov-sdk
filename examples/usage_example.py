"""
Example usage of the OpenGov API SDK.

This example demonstrates how to use the SDK with environment variables
and programmatic configuration.
"""

import os
import opengov_api
from opengov_api import OpenGovAPIError, OpenGovNotFoundError

# Option 1: Use environment variables (recommended for production)
# export OPENGOV_API_KEY="your-api-key"
# export OPENGOV_COMMUNITY="your-community"

# Option 2: Programmatic configuration
if not os.getenv("OPENGOV_API_KEY"):
    opengov_api.set_api_key("your-api-key-here")
    opengov_api.set_community("your-community")

# Optional: Customize timeout
opengov_api.set_timeout(60.0)  # 60 seconds


def example_list_records():
    """Example: List all records."""
    print("\n=== Listing Records ===")
    try:
        records = opengov_api.list_records()
        if isinstance(records.data, list):
            print(f"Found {len(records.data)} records")
            # Print first record if available
            if records.data:
                first_record = records.data[0]
                print(f"First record: {first_record}")
    except OpenGovAPIError as e:
        print(f"Error listing records: {e}")


def example_get_record():
    """Example: Get a specific record by ID."""
    print("\n=== Getting Specific Record ===")
    record_id = "12345"
    try:
        record = opengov_api.get_record(record_id)
        print(f"Record {record_id}: {record}")
    except OpenGovNotFoundError:
        print(f"Record {record_id} not found")
    except OpenGovAPIError as e:
        print(f"Error getting record: {e}")


def example_list_users():
    """Example: List all users."""
    print("\n=== Listing Users ===")
    try:
        users = opengov_api.list_users()
        print(f"Found {len(users.get('users', []))} users")
        # Print first user if available
        if users.get("users"):
            first_user = users["users"][0]
            print(f"First user: {first_user}")
    except OpenGovAPIError as e:
        print(f"Error listing users: {e}")


def example_error_handling():
    """Example: Comprehensive error handling."""
    print("\n=== Error Handling Example ===")
    from opengov_api import (
        OpenGovAuthenticationError,
        OpenGovPermissionDeniedError,
        OpenGovRateLimitError,
        OpenGovAPITimeoutError,
    )

    try:
        records = opengov_api.list_records()
        print("Success!")
        print(f"Records: {records}")
    except OpenGovAuthenticationError:
        print("Authentication failed - check your API key")
    except OpenGovPermissionDeniedError:
        print("Permission denied - check your access rights")
    except OpenGovRateLimitError:
        print("Rate limit exceeded - wait before retrying")
    except OpenGovAPITimeoutError:
        print("Request timed out - try increasing timeout")
    except OpenGovAPIError as e:
        print(f"Other API error: {e}")


if __name__ == "__main__":
    print("OpenGov API SDK Example")
    print("=" * 50)

    # Note: These examples will fail without valid credentials
    # Uncomment the examples you want to run:

    # example_list_records()
    # example_get_record()
    # example_list_users()
    # example_error_handling()

    print("\nNote: Set OPENGOV_API_KEY and OPENGOV_COMMUNITY to run examples")
    print("Example:")
    print("  export OPENGOV_API_KEY='your-api-key'")
    print("  export OPENGOV_COMMUNITY='your-community'")
    print("  python examples/usage_example.py")
