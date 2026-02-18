---
name: NotebookLM MCP Wrapper
overview: Build a Pythonic wrapper that connects to the notebooklm-mcp server via the MCP protocol, providing typed Pydantic models, resource namespacing, and both sync/async APIs.
todos:
  - id: update-pyproject
    content: "Update pyproject.toml: add mcp>=1.26.0 and notebooklm-mcp-cli>=0.3.0 dependencies, change requires-python to >=3.11"
    status: completed
  - id: create-exceptions
    content: Create src/notebooklm_wrapper/exceptions.py with full exception hierarchy
    status: completed
  - id: create-constants
    content: Create src/notebooklm_wrapper/constants.py with enums for artifact types, source types, formats
    status: completed
  - id: create-models
    content: Create src/notebooklm_wrapper/models.py with all Pydantic models (Notebook, Source, ChatResponse, etc.)
    status: completed
  - id: create-mcp-client
    content: Create src/notebooklm_wrapper/_mcp_client.py with MCPClientManager for server connection
    status: completed
  - id: create-base-resource
    content: Create src/notebooklm_wrapper/resources/base.py with BaseResource class
    status: completed
  - id: create-notebook-resource
    content: Create src/notebooklm_wrapper/resources/notebook.py wrapping 6 notebook tools
    status: completed
  - id: create-source-resource
    content: Create src/notebooklm_wrapper/resources/source.py wrapping 6 source tools
    status: completed
  - id: create-chat-resource
    content: Create src/notebooklm_wrapper/resources/chat.py wrapping 2 chat tools
    status: completed
  - id: create-research-resource
    content: Create src/notebooklm_wrapper/resources/research.py wrapping 3 research tools
    status: completed
  - id: create-studio-resource
    content: Create src/notebooklm_wrapper/resources/studio.py wrapping 3 studio tools
    status: completed
  - id: create-share-resource
    content: Create src/notebooklm_wrapper/resources/share.py wrapping 3 share tools
    status: completed
  - id: create-other-resources
    content: Create download.py, note.py, auth.py, export.py resource modules
    status: completed
  - id: create-async-client
    content: Create src/notebooklm_wrapper/async_client.py with AsyncNotebookLMClient
    status: completed
  - id: create-sync-client
    content: Create src/notebooklm_wrapper/client.py with NotebookLMClient (sync facade)
    status: completed
  - id: create-init
    content: Create src/notebooklm_wrapper/__init__.py with public API exports
    status: completed
  - id: create-tests
    content: "Create test files: test_client.py, test_notebook.py, test_source.py, etc."
    status: completed
  - id: create-conftest
    content: Create tests/conftest.py with MCP session mocking fixtures
    status: completed
  - id: update-readme
    content: Update README.md with installation and usage examples
    status: completed
  - id: verify-mypy
    content: Run mypy --strict and fix any type errors
    status: completed
  - id: verify-tests
    content: Run pytest and ensure >80% coverage
    status: completed
isProject: false
---

# NotebookLM Python Wrapper Implementation Plan

## Architecture Decision: MCP Client Approach

We will connect to the `notebooklm-mcp` server as an MCP client, calling its 28 tools programmatically. This provides:

- **Stable protocol**: MCP is a standardized JSON-RPC protocol
- **Full coverage**: All 28 operations (vs 11 with CLI `--json`)
- **Auth handled by server**: No cookie/CSRF complexity
- **Fast**: ~10ms per call (vs ~100ms CLI subprocess)
- **Type-safe**: Tool schemas define inputs/outputs

```
User Code
    ↓
NotebookLMClient (our wrapper)
    ↓
MCP ClientSession (mcp package)
    ↓
notebooklm-mcp server (subprocess via stdio)
    ↓
Services Layer (internal)
    ↓
Google NotebookLM API
```

## Key Dependencies

- `mcp>=1.26.0` - Official MCP Python SDK (requires Python >=3.10)
- `notebooklm-mcp-cli>=0.3.0` - Provides the MCP server binary
- `pydantic>=2.0` - Our typed models

**Python version**: `>=3.11` (to match `notebooklm-mcp-cli` requirement)

## Implementation Structure

```
src/notebooklm_wrapper/
├── __init__.py              # Public exports
├── client.py                # NotebookLMClient (sync facade)
├── async_client.py          # AsyncNotebookLMClient
├── _mcp_client.py           # Internal MCP connection management
├── models.py                # Pydantic models for all data types
├── exceptions.py            # Exception hierarchy
├── constants.py             # Enums for artifact types, formats, etc.
├── resources/
│   ├── __init__.py
│   ├── base.py              # BaseResource with MCP tool calling
│   ├── notebook.py          # NotebookResource (6 tools)
│   ├── source.py            # SourceResource (6 tools)
│   ├── chat.py              # ChatResource (2 tools)
│   ├── research.py          # ResearchResource (3 tools)
│   ├── studio.py            # StudioResource (3 tools)
│   ├── share.py             # ShareResource (3 tools)
│   ├── download.py          # DownloadResource (1 tool)
│   ├── note.py              # NoteResource (1 tool, 4 actions)
│   └── auth.py              # AuthResource (2 tools)
└── _converters.py           # MCP result → Pydantic model converters
```

## Core Components

### 1. MCP Client Manager (`_mcp_client.py`)

Manages the MCP server subprocess and ClientSession:

```python
class MCPClientManager:
    def __init__(self, profile: str | None = None):
        self.profile = profile
        self._session: ClientSession | None = None
    
    async def connect(self) -> ClientSession:
        """Start MCP server and establish session."""
        server_params = StdioServerParameters(
            command="notebooklm-mcp",
            args=["--profile", self.profile] if self.profile else [],
        )
        # ... setup stdio_client and ClientSession
    
    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call an MCP tool and return parsed result."""
        result = await self._session.call_tool(name, arguments)
        return self._parse_result(result)
```

### 2. Resource Base Class (`resources/base.py`)

```python
class BaseResource:
    def __init__(self, mcp_manager: MCPClientManager):
        self._mcp = mcp_manager
    
    async def _call(self, tool_name: str, **kwargs) -> dict:
        """Call MCP tool with error handling."""
        try:
            return await self._mcp.call_tool(tool_name, kwargs)
        except MCPError as e:
            raise self._map_exception(e)
```

### 3. Notebook Resource (`resources/notebook.py`)

Maps to 6 MCP tools: `notebook_list`, `notebook_get`, `notebook_describe`, `notebook_create`, `notebook_rename`, `notebook_delete`

```python
class NotebookResource(BaseResource):
    async def list(self, max_results: int = 100) -> list[Notebook]:
        result = await self._call("notebook_list", max_results=max_results)
        return [Notebook.model_validate(nb) for nb in result["notebooks"]]
    
    async def create(self, title: str = "") -> Notebook:
        result = await self._call("notebook_create", title=title)
        return Notebook.model_validate(result["notebook"])
    
    async def delete(self, notebook_id: str, *, confirm: bool = False) -> None:
        if not confirm:
            raise ValueError("Must set confirm=True to delete")
        await self._call("notebook_delete", notebook_id=notebook_id, confirm=True)
```

### 4. Pydantic Models (`models.py`)

Based on MCP tool return schemas:

```python
class Notebook(BaseModel):
    id: str
    title: str
    source_count: int = Field(alias="sources_count", default=0)
    url: str | None = None
    created_at: datetime | None = None

class Source(BaseModel):
    id: str
    title: str
    type: SourceType
    is_stale: bool = False

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str | None = None
    citations: list[Citation] = []

class ResearchTask(BaseModel):
    task_id: str
    notebook_id: str
    status: Literal["pending", "running", "completed", "failed"]
    sources_found: int = 0
    report: str | None = None

class StudioArtifact(BaseModel):
    id: str
    type: ArtifactType
    status: Literal["pending", "generating", "completed", "failed"]
    url: str | None = None
    title: str | None = None
```

### 5. Exception Hierarchy (`exceptions.py`)

```python
class NotebookLMError(Exception): ...
class AuthenticationError(NotebookLMError): ...
class NotFoundError(NotebookLMError): ...
class ValidationError(NotebookLMError): ...
class RateLimitError(NotebookLMError): ...
class GenerationError(NotebookLMError): ...
```

### 6. Sync Client Facade (`client.py`)

Wraps async client for synchronous usage:

```python
class NotebookLMClient:
    def __init__(self, profile: str | None = None):
        self._async_client = AsyncNotebookLMClient(profile)
        self._loop = asyncio.new_event_loop()
    
    @property
    def notebook(self) -> SyncNotebookResource:
        return SyncNotebookResource(self._async_client.notebook, self._loop)
    
    # ... other resources
```

## MCP Tool → Resource Method Mapping


| MCP Tool                | Resource          | Method                                           |
| ----------------------- | ----------------- | ------------------------------------------------ |
| `notebook_list`         | `client.notebook` | `list()`                                         |
| `notebook_get`          | `client.notebook` | `get(id)`                                        |
| `notebook_describe`     | `client.notebook` | `describe(id)`                                   |
| `notebook_create`       | `client.notebook` | `create(title)`                                  |
| `notebook_rename`       | `client.notebook` | `rename(id, title)`                              |
| `notebook_delete`       | `client.notebook` | `delete(id, confirm=True)`                       |
| `source_add`            | `client.source`   | `add(notebook_id, type, ...)`                    |
| `source_list_drive`     | `client.source`   | `list_drive(notebook_id)`                        |
| `source_sync_drive`     | `client.source`   | `sync_drive(source_ids, confirm=True)`           |
| `source_delete`         | `client.source`   | `delete(source_id, confirm=True)`                |
| `source_describe`       | `client.source`   | `describe(source_id)`                            |
| `source_get_content`    | `client.source`   | `get_content(source_id)`                         |
| `notebook_query`        | `client.chat`     | `ask(notebook_id, query)`                        |
| `chat_configure`        | `client.chat`     | `configure(notebook_id, ...)`                    |
| `research_start`        | `client.research` | `start(query, ...)`                              |
| `research_status`       | `client.research` | `status(notebook_id)`                            |
| `research_import`       | `client.research` | `import_sources(notebook_id, task_id)`           |
| `studio_create`         | `client.studio`   | `create(notebook_id, type, ...)`                 |
| `studio_status`         | `client.studio`   | `status(notebook_id)`                            |
| `studio_delete`         | `client.studio`   | `delete(notebook_id, artifact_id, confirm=True)` |
| `notebook_share_status` | `client.share`    | `status(notebook_id)`                            |
| `notebook_share_public` | `client.share`    | `set_public(notebook_id, enabled)`               |
| `notebook_share_invite` | `client.share`    | `invite(notebook_id, email, role)`               |
| `download_artifact`     | `client.download` | `artifact(notebook_id, type, path)`              |
| `note`                  | `client.note`     | `create/list/update/delete()`                    |
| `refresh_auth`          | `client.auth`     | `refresh()`                                      |
| `export_artifact`       | `client.export`   | `to_docs/to_sheets()`                            |


## Testing Strategy

Mock at MCP ClientSession level:

```python
@pytest.fixture
def mock_mcp_session():
    with patch("notebooklm_wrapper._mcp_client.ClientSession") as mock:
        yield mock

async def test_notebook_list(mock_mcp_session):
    mock_mcp_session.call_tool.return_value = CallToolResult(
        content=[TextContent(text='{"notebooks": [...]}')]
    )
    client = AsyncNotebookLMClient()
    notebooks = await client.notebook.list()
    assert len(notebooks) == 1
```

## Files to Update

- `[pyproject.toml](pyproject.toml)` - Add dependencies: `mcp>=1.26.0`, `notebooklm-mcp-cli>=0.3.0`; change `requires-python = ">=3.11"`
- `[README.md](README.md)` - Update with MCP-based usage examples

## Usage Example

```python
from notebooklm_wrapper import NotebookLMClient

# Sync usage
client = NotebookLMClient(profile="work")
notebooks = client.notebook.list()
notebook = client.notebook.create(title="My Research")
response = client.chat.ask(notebook.id, "What are the main points?")

# Async usage
from notebooklm_wrapper import AsyncNotebookLMClient

async def main():
    client = AsyncNotebookLMClient()
    notebooks = await client.notebook.list()
```

