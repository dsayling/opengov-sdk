# OpenAPI to SDK Mapping Guide

How to translate OpenAPI specification elements to SDK code.

## Table of Contents

1. [Reading the OpenAPI Spec](#reading-the-openapi-spec)
2. [Path to Function Name](#path-to-function-name)
3. [Schema to Pydantic Model](#schema-to-pydantic-model)
4. [Parameters to Function Args](#parameters-to-function-args)
5. [Response Schema to Return Type](#response-schema-to-return-type)

---

## Reading the OpenAPI Spec

The spec file is typically at `opengov-plc-api.json`. Key sections:

```json
{
  "paths": {
    "/v2/{communityId}/records": {
      "get": { ... },
      "post": { ... }
    },
    "/v2/{communityId}/records/{recordId}": {
      "get": { ... },
      "patch": { ... },
      "delete": { ... }
    }
  },
  "components": {
    "schemas": {
      "RecordResource": { ... },
      "RecordAttributes": { ... }
    }
  }
}
```

---

## Path to Function Name

### Standard CRUD Patterns

| OpenAPI Path | HTTP Method | SDK Function |
|--------------|-------------|--------------|
| `/{resource}` | GET | `list_{resource}()` |
| `/{resource}` | POST | `create_{resource}(data)` |
| `/{resource}/{id}` | GET | `get_{resource}(id)` |
| `/{resource}/{id}` | PATCH | `update_{resource}(id, data)` |
| `/{resource}/{id}` | DELETE | `delete_{resource}(id)` or `archive_{resource}(id)` |

### Nested Resources

| OpenAPI Path | HTTP Method | SDK Function |
|--------------|-------------|--------------|
| `/{parent}/{parentId}/{child}` | GET | `list_{parent}_{child}(parent_id)` |
| `/{parent}/{parentId}/{child}` | POST | `add_{parent}_{child}(parent_id, data)` |
| `/{parent}/{parentId}/{child}/{childId}` | GET | `get_{parent}_{child}(parent_id, child_id)` |
| `/{parent}/{parentId}/{child}/{childId}` | PATCH | `update_{parent}_{child}(parent_id, child_id, data)` |
| `/{parent}/{parentId}/{child}/{childId}` | DELETE | `remove_{parent}_{child}(parent_id, child_id)` |

### Naming Conventions

- **Kebab-case to snake_case**: `approval-steps` -> `approval_steps`
- **Singular child in nested**: `records/{id}/applicant` -> `get_record_applicant(record_id)`
- **Plural child in nested**: `records/{id}/guests` -> `list_record_guests(record_id)`

---

## Schema to Pydantic Model

### Basic Schema Translation

OpenAPI Schema:
```json
{
  "RecordAttributes": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "number": { "type": "string" },
      "status": { "$ref": "#/components/schemas/RecordStatus" },
      "histID": { "type": "string" },
      "isEnabled": { "type": "boolean" },
      "createdAt": { "type": "string", "format": "date-time" },
      "description": { "type": "string", "nullable": true }
    },
    "required": ["name"]
  }
}
```

Pydantic Model:
```python
from datetime import datetime
from pydantic import BaseModel, Field

class RecordAttributes(BaseModel):
    name: str  # required field
    number: str | None = None
    status: RecordStatus | None = None
    hist_id: str | None = Field(None, alias="histID")  # camelCase -> snake_case with alias
    is_enabled: bool | None = Field(None, alias="isEnabled")
    created_at: datetime | None = Field(None, alias="createdAt")
    description: str | None = None

    model_config = {"populate_by_name": True}
```

### Type Mapping

| OpenAPI Type | OpenAPI Format | Python Type |
|--------------|----------------|-------------|
| `string` | - | `str` |
| `string` | `date` | `date` |
| `string` | `date-time` | `datetime` |
| `string` | `uuid` | `str` |
| `integer` | - | `int` |
| `number` | - | `float` |
| `boolean` | - | `bool` |
| `array` | - | `list[T]` |
| `object` | - | `dict[str, Any]` |
| `$ref` | - | Referenced model class |

### Nullable and Optional

- `nullable: true` -> `Type | None`
- Not in `required` list -> `Type | None = None`
- Required field -> `Type` (no default)

### Enum Schemas

OpenAPI:
```json
{
  "RecordStatus": {
    "type": "string",
    "enum": ["DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"]
  }
}
```

Python:
```python
from enum import Enum

class RecordStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
```

---

## Parameters to Function Args

### Query Parameters

OpenAPI:
```json
{
  "parameters": [
    {
      "name": "filter[status]",
      "in": "query",
      "schema": { "$ref": "#/components/schemas/RecordStatus" }
    },
    {
      "name": "filter[createdAt][gt]",
      "in": "query",
      "schema": { "type": "string", "format": "date-time" }
    },
    {
      "name": "filter[isEnabled]",
      "in": "query",
      "schema": { "type": "boolean" }
    },
    {
      "name": "page[number]",
      "in": "query",
      "schema": { "type": "integer", "default": 1 }
    },
    {
      "name": "page[size]",
      "in": "query",
      "schema": { "type": "integer", "default": 20, "maximum": 100 }
    }
  ]
}
```

Function Args:
```python
def list_records(
    *,
    status: RecordStatus | None = None,  # filter[status]
    created_at: date | datetime | DateRangeFilter | None = None,  # filter[createdAt]
    is_enabled: bool | None = None,  # filter[isEnabled]
    page_number: int = 1,  # page[number]
    page_size: int = 20,  # page[size]
) -> JSONAPIResponse[RecordResource]:
```

### Path Parameters

OpenAPI:
```json
{
  "parameters": [
    {
      "name": "recordId",
      "in": "path",
      "required": true,
      "schema": { "type": "string" }
    }
  ]
}
```

Function Args:
```python
def get_record(record_id: str) -> dict[str, Any]:  # recordId -> record_id
```

### Date Range Parameters

When you see `filter[fieldName][gt]`, `filter[fieldName][gte]`, `filter[fieldName][lt]`, `filter[fieldName][lte]`:

SDK Pattern:
```python
# Accept date, datetime, or DateRangeFilter
created_at: date | datetime | DateRangeFilter | None = None,
```

DateRangeFilter handles the `[gt]`, `[gte]`, `[lt]`, `[lte]` suffixes automatically.

---

## Response Schema to Return Type

### List Endpoint Response

OpenAPI:
```json
{
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "type": "object",
            "properties": {
              "data": {
                "type": "array",
                "items": { "$ref": "#/components/schemas/RecordResource" }
              },
              "meta": { "$ref": "#/components/schemas/PaginationMeta" },
              "links": { "$ref": "#/components/schemas/PaginationLinks" }
            }
          }
        }
      }
    }
  }
}
```

SDK Return Type:
```python
def list_records(...) -> JSONAPIResponse[RecordResource]:
```

### Single Resource Response

OpenAPI:
```json
{
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": { "$ref": "#/components/schemas/RecordResource" }
        }
      }
    }
  }
}
```

SDK Return Type:
```python
def get_record(record_id: str) -> dict[str, Any]:
```

Note: Simple get/create/update/delete endpoints return `dict[str, Any]` rather than typed models for flexibility.

---

## Example: Complete Translation

### OpenAPI Spec Section

```json
{
  "paths": {
    "/v2/{communityId}/fees": {
      "get": {
        "operationId": "listFees",
        "parameters": [
          { "name": "filter[status]", "in": "query", "schema": { "type": "string", "enum": ["PENDING", "PAID", "WAIVED"] } },
          { "name": "filter[amount][gte]", "in": "query", "schema": { "type": "number" } },
          { "name": "page[number]", "in": "query", "schema": { "type": "integer", "default": 1 } },
          { "name": "page[size]", "in": "query", "schema": { "type": "integer", "default": 20 } }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "properties": {
                    "data": { "type": "array", "items": { "$ref": "#/components/schemas/FeeResource" } }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "FeeStatus": {
        "type": "string",
        "enum": ["PENDING", "PAID", "WAIVED"]
      },
      "FeeAttributes": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "amount": { "type": "number" },
          "status": { "$ref": "#/components/schemas/FeeStatus" },
          "createdAt": { "type": "string", "format": "date-time" }
        }
      },
      "FeeResource": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string" },
          "attributes": { "$ref": "#/components/schemas/FeeAttributes" }
        }
      }
    }
  }
}
```

### Generated SDK Code

**enums.py:**
```python
class FeeStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    WAIVED = "WAIVED"
```

**models/fees.py:**
```python
class FeeAttributes(BaseModel):
    name: str | None = None
    amount: float | None = None
    status: FeeStatus | None = None
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True}


class FeeResource(BaseModel):
    id: str
    type: str
    attributes: FeeAttributes
```

**params.py:**
```python
class ListFeesParams(BaseModel):
    filter_status: FeeStatus | None = None
    filter_amount_gte: float | None = None
    page_number: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    def to_query_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if self.filter_status:
            params["filter[status]"] = self.filter_status.value
        if self.filter_amount_gte is not None:
            params["filter[amount][gte]"] = self.filter_amount_gte
        params["page[number]"] = self.page_number
        params["page[size]"] = self.page_size
        return params
```

**fees.py:**
```python
@handle_request_errors
def list_fees(
    *,
    status: FeeStatus | None = None,
    amount_gte: float | None = None,
    page_number: int = 1,
    page_size: int = 20,
) -> JSONAPIResponse[FeeResource]:
    params_model = ListFeesParams(
        filter_status=status,
        filter_amount_gte=amount_gte,
        page_number=page_number,
        page_size=page_size,
    )

    with _get_client() as client:
        url = build_url(get_base_url(), get_community(), "fees")
        response = client.get(url, params=params_model.to_query_params())
        response.raise_for_status()
        data = parse_json_response(response)

        return JSONAPIResponse[FeeResource](
            data=[FeeResource(**item) for item in data["data"]],
            included=data.get("included"),
            links=Links(**data["links"]) if data.get("links") else None,
            meta=Meta(**data["meta"]) if data.get("meta") else None,
        )
```
