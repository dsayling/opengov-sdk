# CLAUDE.md

AI agent guidance for opengov-sdk repository.

## 📚 Agent Documentation

**Primary Specs** (Read these first - high-density AISP format):
- `docs/agents/llm-spec.md` - Complete SDK architecture, patterns, endpoints
- `docs/agents/test-spec.md` - Test infrastructure, fixtures, parametrization
- `docs/agents/workflow-spec.md` - Commands, workflows, git conventions
- `docs/agents/error-spec.md` - Exception hierarchy, error handling
- `docs/agents/aisp.md` - AISP notation reference (meta-protocol)

**Usage**: Read relevant spec before making changes. AISP format provides ~4x information density vs prose.

**Maintenance**: When adding major features or patterns, update relevant spec. Keep `δ ≥ 0.80` (symbol density).

## Core Principles

**DRY**: Extract patterns → fixtures/functions. No duplication. Single source of truth.

**SOLID**:
- Single Responsibility - One purpose per function/module
- Open/Closed - Extend via parametrization, don't modify
- Liskov Substitution - Consistent interfaces
- Interface Segregation - Minimal parameters
- Dependency Inversion - Depend on abstractions (fixtures, decorators)

## Commands

See `docs/agents/workflow-spec.md` for complete reference.

```bash
uv sync                                    # Install dependencies
uv run pytest                              # All tests
uv run pytest --cov=opengov_api --cov-report=html  # Coverage
uv run pytest tests/test_records.py        # Single file
uv run pytest tests/test_file.py::test_name -v    # Specific test
uv run pyright                             # Type check
uv run ruff format                         # Format
uv run ruff check --fix                    # Lint & fix
```

## Architecture

See `docs/agents/llm-spec.md` for complete specification.

**Pattern**: Functional factory (inspired by OpenAI Agents SDK)

**Module-level config** (`client.py`):
- Global state: API key, community, base URL, timeout
- `set_*()` functions write, `get_*()` functions read

**Client factory** (`_get_client()`):
- Creates fresh `httpx.Client` with auth headers
- Always use as context manager: `with _get_client() as client:`

**Shared utilities** (`base.py`):
- `build_url()` - URL construction
- `@handle_request_errors` - httpx → SDK exception mapping
- `parse_json_response()` - JSON parsing with error handling
- `make_status_error()` - Status code → exception class

## Adding Endpoints

**Use the `api-endpoint` skill**: `.claude/skills/api-endpoint/SKILL.md`

Generates endpoints from OpenAPI specs. Handles: endpoint modules, Pydantic models, tests, exports.

**Specs**: `docs/agents/llm-spec.md` ⟦Λ:*⟧, `docs/agents/test-spec.md` ⟦Γ:NewEndpoint⟧

**Quick workflow**:
1. Provide OpenAPI spec file path
2. Skill generates: endpoint module, models, tests
3. Verify: `uv run pytest && uv run pyright`

**OpenAPI → SDK mapping**:
- `GET /{resource}` → `list_{resource}()` (typed response)
- `GET /{resource}/{id}` → `get_{resource}(id)`
- `POST /{resource}` → `create_{resource}(data)`
- `PATCH /{resource}/{id}` → `update_{resource}(id, data)`
- `DELETE /{resource}/{id}` → `delete_{resource}(id)` or `archive_{resource}(id)`

## Test Structure

See `docs/agents/test-spec.md` for complete specification.

**Framework**: pytest + pytest-httpx (mocking)

**Auto-use Fixtures** (all tests):
- `block_network_calls` - Prevents real HTTP (pytest-httpx)
- `reset_config` - Isolation between tests

**Config Fixtures**:
- `configure_client` - Sets test API key + community
- `test_base_url` - Returns test base URL

**Helper Fixtures** (DRY):
- `build_url(path)` - Constructs full URL
- `mock_url_with_params(url)` - Regex for pagination tests
- `assert_request_method(method)` - Verifies HTTP method

**Organization**:
- `test_infrastructure.py` - Client behaviors (auth, config, URLs)
- `test_common_endpoints.py` - REST patterns (parametrized)
- `test_*.py` - Module-specific behaviors

**Pattern**:
```python
# ✅ Use fixtures + parametrization
@pytest.mark.parametrize("func,url", [
    (list_records, "testcommunity/records"),
    (list_users, "testcommunity/users"),
])
def test_list_endpoints(httpx_mock, configure_client, build_url, func, url):
    httpx_mock.add_response(url=build_url(url), json={"data": []})
    result = func()
    assert "data" in result
```

## Coverage Target

`Coverage ≥ 98%` - Enforced. Add tests before merging.
