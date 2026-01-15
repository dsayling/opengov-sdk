# Schema Extraction from OpenAPI Spec

This guide provides systematic instructions for extracting attribute schemas from the OpenAPI specification to ensure Pydantic models match the API exactly.

## Overview

The OpenAPI spec at `docs/opengov-plc-api.json` defines schemas inline within response objects. To create accurate Pydantic models, you must extract these schemas directly from the spec rather than inferring from examples or memory.

## Step 1: Locate the Schema in OpenAPI Spec

Schemas are embedded in the OpenAPI spec at:
```
spec.paths["{path}"].{method}.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes
```

### Common Paths by Resource

| Resource | GET Path | Attributes Location |
|----------|----------|---------------------|
| Records | `/v2/{community}/records/{recordID}` | `.paths["/v2/{community}/records/{recordID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Locations | `/v2/{community}/locations/{locationID}` | `.paths["/v2/{community}/locations/{locationID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Workflow Steps | `/v2/{community}/records/{recordID}/workflow-steps/{stepID}` | `.paths["/v2/{community}/records/{recordID}/workflow-steps/{stepID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Guests | `/v2/{community}/records/{recordID}/guests/{userID}` | `.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Files/Attachments | `/v2/{community}/files/{fileID}` | `.paths["/v2/{community}/files/{fileID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Change Requests | `/v2/{community}/records/{recordID}/change-requests/{changeRequestID}` | `.paths["/v2/{community}/records/{recordID}/change-requests/{changeRequestID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Collections | `/v2/{community}/records/{recordID}/collections/{collectionID}` | `.paths["/v2/{community}/records/{recordID}/collections/{collectionID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |
| Collection Entries | `/v2/{community}/records/{recordID}/collections/{collectionID}/entries/{entryID}` | `.paths["/v2/{community}/records/{recordID}/collections/{collectionID}/entries/{entryID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes` |

## Step 2: Extract Schema Using jq Command

Use `jq` to extract the attributes schema from the OpenAPI spec:

```bash
# Example: Extract LocationAttributes
jq '.paths["/v2/{community}/locations/{locationID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes' docs/opengov-plc-api.json

# Example: Extract WorkflowStepAttributes
jq '.paths["/v2/{community}/records/{recordID}/workflow-steps/{stepID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes' docs/opengov-plc-api.json

# Example: Extract GuestAttributes
jq '.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes' docs/opengov-plc-api.json
```

### Python Script Alternative

If you prefer Python over jq:

```python
import json

# Load the OpenAPI spec
with open('docs/opengov-plc-api.json', 'r') as f:
    spec = json.load(f)

# Extract attributes schema for a resource
# Example: LocationAttributes
path = '/v2/{community}/locations/{locationID}'
method = 'get'

path_obj = spec['paths'][path][method]
response_schema = path_obj['responses']['200']['content']['application/vnd.api+json']['schema']
attributes_schema = response_schema['properties']['data']['properties']['attributes']

# Print the schema in readable format
print(json.dumps(attributes_schema, indent=2))

# Access individual properties
properties = attributes_schema.get('properties', {})
required_fields = attributes_schema.get('required', [])

print(f"\nTotal fields: {len(properties)}")
print(f"Required fields: {required_fields}")
```

## Step 3: Document All Fields in a Mapping Table

Create a comprehensive field mapping table to track all OpenAPI fields and their Pydantic equivalents:

### Template

| OpenAPI Field | Type | Format | Required | Nullable | Pydantic Field | Pydantic Type | Notes |
|---------------|------|--------|----------|----------|----------------|---------------|-------|
| name | string | - | No | Yes | name | str \| None = None | |
| createdAt | string | date-time | Yes | No | created_at | datetime = Field(..., alias="createdAt") | Required field |
| histID | string | - | No | No | hist_id | str \| None = Field(None, alias="histID") | Preserve camelCase in alias |
| isEnabled | boolean | - | Yes | No | is_enabled | bool = Field(..., alias="isEnabled") | Required, needs alias |
| phoneNo | string | - | No | Yes | phone_no | str \| None = Field(None, alias="phoneNo") | |

### Example: GuestAttributes Mapping

| OpenAPI Field | Type | Required | Nullable | Pydantic Field | Pydantic Type |
|---------------|------|----------|----------|----------------|---------------|
| firstName | string | Yes | No | first_name | str = Field(..., alias="firstName") |
| lastName | string | Yes | No | last_name | str = Field(..., alias="lastName") |
| email | string | Yes | No | email | str |
| phoneNo | string | No | Yes | phone_no | str \| None = Field(None, alias="phoneNo") |
| address | string | No | Yes | address | str \| None = None |
| address2 | string | No | Yes | address_2 | str \| None = Field(None, alias="address2") |
| city | string | No | Yes | city | str \| None = None |
| state | string | No | Yes | state | str \| None = None |
| zip | string | No | Yes | zip_code | str \| None = Field(None, alias="zip") |

## Step 4: Field Type Mapping Rules

### Basic Type Mapping

| OpenAPI Type | OpenAPI Format | Nullable | Required | Pydantic Type |
|--------------|----------------|----------|----------|---------------|
| string | - | false | true | str |
| string | - | false | false | str \| None = None |
| string | - | true | true | str \| None |
| string | - | true | false | str \| None = None |
| string | date-time | false | false | datetime \| None = Field(None, alias="...") |
| string | date-time | true | false | datetime \| None = Field(None, alias="...") |
| string | date | false | false | date \| None = Field(None, alias="...") |
| integer | - | false | true | int |
| integer | - | false | false | int \| None = None |
| number | - | false | true | float |
| number | - | false | false | float \| None = None |
| boolean | - | false | true | bool |
| boolean | - | false | false | bool \| None = None |
| array | - | false | false | list[T] \| None = None |
| object | - | false | false | dict[str, Any] \| None = None |

### Required Field Syntax

```python
# Required field (no default)
name: str = Field(..., alias="fieldName")

# Required but nullable (unusual, but possible)
name: str | None = Field(..., alias="fieldName")

# Optional field (has default)
name: str | None = Field(None, alias="fieldName")

# Optional field, no alias needed
description: str | None = None
```

### Field Alias Rules

```python
# camelCase → snake_case with alias
createdAt → created_at: datetime | None = Field(None, alias="createdAt")
isEnabled → is_enabled: bool | None = Field(None, alias="isEnabled")
phoneNo → phone_no: str | None = Field(None, alias="phoneNo")

# ALL CAPS IDs preserve casing in alias
histID → hist_id: str | None = Field(None, alias="histID")
userID → user_id: str | None = Field(None, alias="userID")
matID → mat_id: str | None = Field(None, alias="matID")

# Numbers in field names
address2 → address_2: str | None = Field(None, alias="address2")

# No alias needed for already snake_case
name → name: str | None = None
description → description: str | None = None
```

## Step 5: Handle Special Cases

### Empty String to None Validator

When the API returns empty strings `""` that should be `None`:

```python
@field_validator("activated_at", "completed_at", mode="before")
@classmethod
def set_empty_datetime_to_none(cls, v):
    if v == "":
        return None
    return v
```

### Type Coercion Validator

When the API returns inconsistent types (e.g., int as string):

```python
@field_validator("renewal_number", mode="before")
@classmethod
def coerce_renewal_number(cls, v):
    if v is None:
        return v
    return str(v)
```

### Multiple Fields, Same Validator

```python
@field_validator("field1", "field2", "field3", mode="before")
@classmethod
def handle_empty_strings(cls, v):
    return None if v == "" else v
```

### Arrays of Objects

```python
# OpenAPI: "formFields": { "type": "array", "items": { "type": "object", "properties": {...} } }
# Pydantic:
form_fields: list[dict[str, Any]] | None = Field(None, alias="formFields")

# Or with nested model for type safety:
form_fields: list[FormField] | None = Field(None, alias="formFields")
```

### Nested Objects

```python
# Simple nested object - use dict
metadata: dict[str, Any] | None = None

# Structured nested object - create Pydantic model
class OwnerInfo(BaseModel):
    name: str | None = None
    email: str | None = None

owner: OwnerInfo | None = None
```

### Enum Fields

```python
# OpenAPI: "status": { "type": "string", "enum": ["DRAFT", "ACTIVE", "COMPLETE"] }
# Pydantic:
from .enums import RecordStatus

status: RecordStatus | None = None
```

## Step 6: Verification Checklist

Before considering the model complete, verify:

- [ ] All fields from OpenAPI spec `properties` are included in model
- [ ] No extra fields beyond spec (unless intentionally added for SDK convenience)
- [ ] Required fields (in OpenAPI `required` array) use `...` or no default value
- [ ] Optional fields (not in OpenAPI `required`) use `| None = None`
- [ ] Nullable fields (OpenAPI `nullable: true`) use `| None` in type
- [ ] All camelCase fields have proper `Field(alias=...)`
- [ ] Date/datetime fields use correct type (`date` or `datetime`)
- [ ] Enum fields reference the correct enum class from `enums.py`
- [ ] Array fields have correct item type (`list[T]`)
- [ ] `model_config = {"populate_by_name": True}` is present at end of class
- [ ] Field validators added only when needed (empty string, type coercion)

## Step 7: Test Model Deserialization

Create a test to verify the model deserializes spec-compliant JSON:

```python
import pytest
from opengov_api.models import GuestAttributes

def test_guest_attributes_full():
    """Test GuestAttributes deserializes all fields from OpenAPI spec."""
    data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phoneNo": "555-1234",
        "address": "123 Main St",
        "address2": "Apt 4B",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701"
    }

    guest = GuestAttributes(**data)

    assert guest.first_name == "John"
    assert guest.last_name == "Doe"
    assert guest.email == "john.doe@example.com"
    assert guest.phone_no == "555-1234"
    assert guest.address == "123 Main St"
    assert guest.address_2 == "Apt 4B"
    assert guest.city == "Springfield"
    assert guest.state == "IL"
    assert guest.zip_code == "62701"

def test_guest_attributes_minimal():
    """Test GuestAttributes with only required fields."""
    data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane@example.com"
    }

    guest = GuestAttributes(**data)

    assert guest.first_name == "Jane"
    assert guest.last_name == "Smith"
    assert guest.email == "jane@example.com"
    assert guest.phone_no is None
    assert guest.address is None
```

## Complete Example: From Schema to Model

### Step 1: Extract schema

```bash
jq '.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes' docs/opengov-plc-api.json
```

### Step 2: Document fields

| OpenAPI Field | Type | Required | Nullable | Pydantic |
|---------------|------|----------|----------|----------|
| firstName | string | Yes | No | first_name: str = Field(..., alias="firstName") |
| lastName | string | Yes | No | last_name: str = Field(..., alias="lastName") |
| email | string | Yes | No | email: str |
| phoneNo | string | No | Yes | phone_no: str \| None = Field(None, alias="phoneNo") |
| address | string | No | Yes | address: str \| None = None |

### Step 3: Generate model

```python
from pydantic import BaseModel, Field

class GuestAttributes(BaseModel):
    """Guest attributes matching OpenAPI spec."""

    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: str
    phone_no: str | None = Field(None, alias="phoneNo")
    address: str | None = None
    address_2: str | None = Field(None, alias="address2")
    city: str | None = None
    state: str | None = None
    zip_code: str | None = Field(None, alias="zip")

    model_config = {"populate_by_name": True}
```

### Step 4: Verify

- ✅ All 9 fields from spec included
- ✅ No extra fields
- ✅ Required fields (firstName, lastName, email) use `...`
- ✅ Optional fields use `| None = None`
- ✅ camelCase fields have aliases
- ✅ model_config present

## Quick Reference Commands

```bash
# Extract all paths in the spec
jq '.paths | keys | .[]' docs/opengov-plc-api.json

# Find paths containing a specific resource
jq '.paths | keys | .[]' docs/opengov-plc-api.json | grep -i guests

# Extract full response schema (not just attributes)
jq '.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"]' docs/opengov-plc-api.json

# Check if a field is in the required array
jq '.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes.required' docs/opengov-plc-api.json

# List all properties (field names)
jq '.paths["/v2/{community}/records/{recordID}/guests/{userID}"].get.responses["200"].content["application/vnd.api+json"].schema.properties.data.properties.attributes.properties | keys' docs/opengov-plc-api.json
```

## Common Pitfalls to Avoid

1. **Don't infer from examples** - Always extract from spec
2. **Don't guess field names** - Use exact OpenAPI property names
3. **Don't assume required/optional** - Check the `required` array
4. **Don't forget aliases** - camelCase must have `Field(alias=...)`
5. **Don't add validators unnecessarily** - Only when API behavior requires it
6. **Don't skip model_config** - Always include `{"populate_by_name": True}`
7. **Don't forget to test** - Verify deserialization with spec-compliant data

## Summary Workflow

1. **Extract** - Use jq/Python to get attributes schema from OpenAPI spec
2. **Document** - Create field mapping table
3. **Generate** - Write Pydantic model matching spec exactly
4. **Validate** - Use verification checklist
5. **Test** - Verify deserialization with mock data
6. **Commit** - Only after all checks pass
