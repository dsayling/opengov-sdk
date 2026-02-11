---
name: api-endpoint
description: |
  Add new API endpoints to the OpenGov SDK from an OpenAPI specification. Use when:
  (1) Adding a new resource module (e.g., fees.py, transactions.py)
  (2) Adding endpoints to an existing module
  (3) User provides an OpenAPI spec file path or asks to "add endpoints" or "implement API methods"

  Creates: endpoint module, Pydantic models (params, response, enums), tests, and exports.
---

# OpenGov API Endpoint Generator

Generate SDK endpoints from OpenAPI specifications following project conventions.

## Workflow

1. **Read the OpenAPI spec** at the provided file path
2. **Extract attribute schemas** - Use the schema extraction guide in [references/schema-extraction.md](references/schema-extraction.md) to:
   - Locate the schema in the OpenAPI spec for each resource
   - Extract using jq command or Python script
   - Document all fields in a mapping table
   - Verify field types, required/optional status, and nullable flags
   - Verify field mappings before generating code
3. **Identify endpoints** to implement from the spec
4. **Check existing code** to understand current patterns and avoid duplicates
5. **Generate code** following patterns in [references/patterns.md](references/patterns.md)
6. **Run tests and type checks** to verify

## Quick Reference

### Files to Create/Modify

| Component | Location | When |
|-----------|----------|------|
| Endpoint module | `src/opengov_api/{resource}.py` | Always |
| Response models | `src/opengov_api/models/{resource}.py` | If typed responses needed |
| Params model | `src/opengov_api/models/params.py` | If list endpoint has filters |
| Enums | `src/opengov_api/models/enums.py` | If status/type enums needed |
| Model exports | `src/opengov_api/models/__init__.py` | When adding models |
| SDK exports | `src/opengov_api/__init__.py` | Always |
| Tests | `tests/test_{resource}.py` | Always |
| Common tests | `tests/test_common_endpoints.py` | Add to parametrized lists |

### OpenAPI to SDK Mapping

| OpenAPI | SDK |
|---------|-----|
| `GET /{resource}` | `list_{resource}()` returning `JSONAPIResponse[{Resource}Resource]` |
| `GET /{resource}/{id}` | `get_{resource}(id)` returning `dict[str, Any]` |
| `POST /{resource}` | `create_{resource}(data)` returning `dict[str, Any]` |
| `PATCH /{resource}/{id}` | `update_{resource}(id, data)` returning `dict[str, Any]` |
| `DELETE /{resource}/{id}` | `delete_{resource}(id)` or `archive_{resource}(id)` |
| Nested `GET /{parent}/{id}/{child}` | `list_{parent}_{child}(parent_id)` |
| Nested `POST /{parent}/{id}/{child}` | `add_{parent}_{child}(parent_id, data)` |

### Filter Parameter Translation

| OpenAPI Parameter | SDK Param Name | Model Field |
|-------------------|----------------|-------------|
| `filter[status]` | `status` | `filter_status` |
| `filter[createdAt]` | `created_at` | `filter_created_at` |
| `filter[isEnabled]` | `is_enabled` | `filter_is_enabled` |
| `page[number]` | `page_number` | `page_number` |
| `page[size]` | `page_size` | `page_size` |

## Detailed Patterns

See [references/patterns.md](references/patterns.md) for complete code examples including:
- Full list endpoint with typed params/response
- Iterator function pattern
- Simple CRUD endpoints
- Nested resource endpoints
- Model definitions
- Test patterns

## Checklist

Before completing, verify:

**Schema Extraction & Validation:**
- [ ] Schema extracted using jq/Python from OpenAPI spec (not inferred from memory)
- [ ] All OpenAPI fields documented in mapping table
- [ ] Field types match OpenAPI spec exactly (string/integer/number/boolean/array/object)
- [ ] Required vs optional status matches spec (check `required` array)
- [ ] Nullable fields handled correctly (`nullable: true` → `| None`)
- [ ] All camelCase fields have proper `Field(alias=...)` with exact casing
- [ ] Field validators added only when needed (empty string → None, type coercion)
- [ ] No extra fields beyond spec (unless intentionally added for SDK convenience)

**Code Generation:**
- [ ] All endpoint functions have `@handle_request_errors` decorator
- [ ] All functions use `with _get_client() as client:` pattern
- [ ] List endpoints return `JSONAPIResponse[{Resource}Resource]`
- [ ] Response models use `Field(alias="camelCase")` for JSON field mapping
- [ ] Params model has `to_query_params()` method
- [ ] `model_config = {"populate_by_name": True}` present in all attribute models

**Integration:**
- [ ] Functions exported in `__init__.py`
- [ ] Models exported in `models/__init__.py`
- [ ] Tests created in `tests/test_{resource}.py`
- [ ] List/Get endpoints added to `test_common_endpoints.py` parametrized lists

**Verification:**
- [ ] `uv run pytest` passes
- [ ] `uv run pyright` passes
