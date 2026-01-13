"""
Example usage of the record-types API endpoints.

This demonstrates how to use the new record-types functionality.
"""

import opengov_api

# Configure the SDK (would normally use real credentials)
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# Example 1: List all record types
print("Example 1: List all record types")
record_types = opengov_api.list_record_types()
for record_type in record_types.data:
    print(f"  - {record_type.attributes.name} (ID: {record_type.id})")
    print(f"    Status: {record_type.attributes.status}")
    print(f"    Enabled: {record_type.attributes.is_enabled}")

# Example 2: Filter by department
print("\nExample 2: Filter by department")
dept_record_types = opengov_api.list_record_types(department_id="dept-123")
print(f"Found {len(dept_record_types.data)} record types in department")

# Example 3: Get a specific record type
print("\nExample 3: Get a specific record type")
record_type = opengov_api.get_record_type("rt-456789")
print(f"Record Type: {record_type['data']['attributes']['name']}")
print(f"Apply Access: {record_type['data']['attributes']['applyAccess']}")
print(f"View Access: {record_type['data']['attributes']['viewAccess']}")

# Example 4: Iterate through all record types (handles pagination automatically)
print("\nExample 4: Iterate through all record types")
count = 0
for record_type in opengov_api.iter_record_types():
    count += 1
    if count <= 5:  # Show first 5
        print(f"  - {record_type.attributes.name}")
print(f"Total: {count} record types")

# Example 5: Check pagination
print("\nExample 5: Pagination info")
response = opengov_api.list_record_types(page_size=10)
print(f"Page {response.current_page()} of {response.total_pages()}")
print(f"Total records: {response.total_records()}")
print(f"Has next page: {response.has_next_page()}")

# Example 6: List attachments for a record type
print("\nExample 6: List attachment templates")
attachments = opengov_api.list_record_type_attachments("rt-456789")
for attachment in attachments["data"]:
    print(f"  - {attachment['attributes']['name']}")
    print(f"    Required: {attachment['attributes'].get('required', False)}")

# Example 7: Get a specific attachment template
print("\nExample 7: Get attachment template")
attachment = opengov_api.get_record_type_attachment("rt-attachment-334455")
print(f"Attachment: {attachment['data']['attributes']['name']}")
print(f"Description: {attachment['data']['attributes'].get('description')}")

# Example 8: List document templates
print("\nExample 8: List document templates")
docs = opengov_api.list_record_type_document_templates("rt-456789")
for doc in docs["data"]:
    print(f"  - {doc['attributes']['docTitle']}")
    print(f"    Type: {doc['attributes'].get('documentType')}")

# Example 9: Get form fields
print("\nExample 9: Get form fields")
form = opengov_api.get_record_type_form("rt-456789")
for field in form["data"]["attributes"]["fields"]:
    print(f"  - {field['label']} ({field['formFieldType']})")
    print(f"    Required: {field['required']}")

# Example 10: List fee templates
print("\nExample 10: List fee templates")
fees = opengov_api.list_record_type_fees("rt-456789")
for fee in fees["data"]:
    print(f"  - {fee['attributes']['label']}")
    print(f"    Account: {fee['attributes'].get('accountNumber')}")

# Example 11: List workflow step templates
print("\nExample 11: List workflow step templates")
workflow = opengov_api.list_record_type_workflow("rt-456789")
for step in workflow["data"]:
    print(f"  - {step['attributes']['label']} ({step['attributes']['stepType']})")
    print(f"    Sequence: {step['attributes'].get('sequence', True)}")

# Example 12: Get a specific workflow step
print("\nExample 12: Get workflow step")
step = opengov_api.get_record_type_workflow_step("rt-456789", "rt-template-step-101112")
print(f"Step: {step['data']['attributes']['label']}")
print(f"Type: {step['data']['attributes']['stepType']}")
