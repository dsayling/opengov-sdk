"""
Example usage of the typed OpenGov API SDK with pagination support.

This demonstrates how to use the SDK with typed parameters and responses.
"""

import opengov_api
from opengov_api.models import RecordStatus, DateRangeFilter
from datetime import date

# Configure the SDK
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("your-community")

# Example 1: Simple filtered query
print("Example 1: List active records")
print("=" * 50)
response = opengov_api.list_records(
    filter_status=RecordStatus.ACTIVE, filter_is_enabled=True, page_size=10
)

print(f"Page {response.current_page()} of {response.total_pages()}")
print(f"Total records: {response.total_records()}")
print(f"Records on this page: {len(response.data)}")

for record in response.data:
    print(f"  - {record.attributes.name} ({record.attributes.number})")

# Example 2: Date range filtering
print("\nExample 2: Records created after March 1, 2025")
print("=" * 50)
response = opengov_api.list_records(
    filter_created_at=DateRangeFilter(gt=date(2025, 3, 1)),
    filter_status=RecordStatus.ACTIVE,
)

for record in response.data:
    print(f"  - {record.attributes.name} created {record.attributes.created_at}")

# Example 3: Complex date range (Q1 2025)
print("\nExample 3: Records from Q1 2025")
print("=" * 50)
response = opengov_api.list_records(
    filter_created_at=DateRangeFilter(gte=date(2025, 1, 1), lt=date(2025, 4, 1))
)

print(f"Found {response.total_records()} records in Q1 2025")

# Example 4: Pagination - fetch next page
print("\nExample 4: Manual pagination")
print("=" * 50)
response = opengov_api.list_records(
    filter_status=RecordStatus.ACTIVE, page_number=1, page_size=20
)

print(f"First page: {len(response.data)} records")

if response.has_next_page():
    next_response = opengov_api.list_records(
        filter_status=RecordStatus.ACTIVE,
        page_number=response.current_page() + 1,
        page_size=20,
    )
    print(f"Second page: {len(next_response.data)} records")

# Example 5: Auto-pagination with iterator
print("\nExample 5: Auto-pagination with iterator")
print("=" * 50)
count = 0
for record in opengov_api.iter_records(
    filter_status=RecordStatus.ACTIVE, filter_is_enabled=True
):
    count += 1
    print(f"  Processing record {count}: {record.attributes.name}")
    if count >= 5:  # Just show first 5 for demo
        print("  ... (and more)")
        break

# Example 6: Multiple filters
print("\nExample 6: Complex filtering")
print("=" * 50)
response = opengov_api.list_records(
    filter_status=RecordStatus.COMPLETE,
    filter_type_id="building-permit-type-id",
    filter_submitted_online=True,
    filter_created_at=DateRangeFilter(gte=date(2025, 1, 1)),
    sort="-createdAt",  # Sort by creation date descending
    page_size=50,
)

print(f"Found {response.total_records()} completed online building permits since 2025")

# Example 7: Sparse fieldsets and includes (JSON:API features)
print("\nExample 7: JSON:API features")
print("=" * 50)
response = opengov_api.list_records(
    filter_status=RecordStatus.ACTIVE,
    include=["applicant", "primaryLocation"],
    fields={"records": ["name", "number", "status"]},
    page_size=10,
)

for record in response.data:
    # Only name, number, and status will be in attributes
    print(f"  - {record.attributes.name}: {record.attributes.number}")

# Included resources are available in response.included
if response.included:
    print(f"\nIncluded {len(response.included)} related resources")
