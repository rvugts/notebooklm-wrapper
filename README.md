# NotebookLM Wrapper

Pythonic wrapper for Google NotebookLM via the MCP (Model Context Protocol). Connects to the `notebooklm-mcp` server and provides a clean, typed interface to all NotebookLM functionality.

## Features

- **Clean Python API** - No subprocess or CLI calls
- **Full type safety** - Pydantic models for all data
- **Sync + Async** - Use either programming style
- **28 operations** - Notebooks, sources, chat, research, studio, sharing, and more
- **Auth handled by server** - Run `nlm login` once, then use the wrapper

## Requirements

- Python 3.11+
- [notebooklm-mcp-cli](https://pypi.org/project/notebooklm-mcp-cli/) (installed automatically)

## Installation

**From PyPI** (once published):

```bash
pip install notebooklm-wrapper
```

**From source** (development or unreleased):

```bash
pip install git+https://github.com/ai-chitect/notebooklm-wrapper.git
# or, from a local clone:
pip install -e .
```

**Publishing to PyPI**: Run `./scripts/publish.sh` (runs tests, builds, then publishes). Use `./scripts/publish.sh --test` for TestPyPI. Requires [hatch](https://hatch.pypa.io/) and PyPI credentials.

**Prerequisites**: Authenticate with NotebookLM (one-time setup):

```bash
pip install notebooklm-mcp-cli
nlm login  # Opens browser for authentication
```

## Quick Start

```python
from notebooklm_wrapper import NotebookLMClient

# Initialize client (uses default profile from nlm login)
client = NotebookLMClient()

# List notebooks
notebooks = client.notebook.list()
for nb in notebooks:
    print(f"{nb.title} ({nb.id})")

# Create notebook
notebook = client.notebook.create(title="My Research")

# Add sources
client.source.add(
    notebook.id,
    "url",
    url="https://example.com/article",
)

# Ask questions
response = client.chat.ask(notebook.id, "What are the main points?")
print(response.answer)
for citation in response.citations:
    print(f"  - {citation.source_title}")
```

## Async Usage

```python
import asyncio
from notebooklm_wrapper import AsyncNotebookLMClient

async def main():
    client = AsyncNotebookLMClient()
    notebooks = await client.notebook.list()
    print(f"Found {len(notebooks)} notebooks")

    # Create and query
    notebook = await client.notebook.create(title="Async Research")
    response = await client.chat.ask(notebook.id, "Summarize the key findings")
    print(response.answer)

asyncio.run(main())
```

## Multi-Profile

```python
# Use specific profile (set via NOTEBOOKLM_MCP_PROFILE when spawning server)
client = NotebookLMClient(profile="work")
notebooks = client.notebook.list()

# Async with profile
async_client = AsyncNotebookLMClient(profile="personal")
```

## Multi-User / Web App

For multi-tenant apps (e.g. on Google Cloud) where each user has their own NotebookLM credentials stored in your DB (encrypted) and obtained via OAuth, use **`config_dir`** to isolate credentials per user. The wrapper spawns one MCP server process per client; with a unique `config_dir` per user, that process uses a dedicated credential store under `config_dir/.notebooklm-mcp-cli`.

1. **Store credentials:** After OAuth (or user-provided cookies), encrypt and store the cookie string in your DB keyed by user id.
2. **Per request/session:** Create a user-specific directory (or use a persistent path per user), decrypt credentials from your DB, then create a client and inject tokens:

```python
import os
from notebooklm_wrapper import AsyncNotebookLMClient

async def notebooklm_client_for_user(user_id: str, decrypted_cookies: str):
    # Use a dedicated dir per user so the MCP server stores credentials there
    config_dir = f"/app/data/users/{user_id}"
    os.makedirs(config_dir, exist_ok=True)

    client = AsyncNotebookLMClient(
        profile=user_id,
        config_dir=config_dir,
    )
    # Inject credentials so the server can use them (first time or refresh)
    await client.auth.save_tokens(cookies=decrypted_cookies)
    return client

# Then use the client as usual
async def handle_request(user_id: str, ...):
    cookies = get_encrypted_cookies_from_db(user_id)
    decrypted = decrypt(cookies)
    client = await notebooklm_client_for_user(user_id, decrypted)
    try:
        notebooks = await client.notebook.list()
        # ...
    finally:
        await client.disconnect()
```

See [docs/multi-user-credentials-design.md](docs/multi-user-credentials-design.md) for how credential isolation works and design details.

## API Reference

| Resource | Methods |
|----------|---------|
| `client.notebook` | `list()`, `get(id)`, `describe(id)`, `create(title)`, `rename(id, title)`, `delete(id, confirm=True)` |
| `client.source` | `add(notebook_id, type, url=...)`, `list_drive(notebook_id)`, `sync_drive(ids, confirm=True)`, `delete(id, confirm=True)`, `describe(id)`, `get_content(id)` |
| `client.chat` | `ask(notebook_id, query)`, `configure(notebook_id, goal=..., response_length=...)` |
| `client.research` | `start(query, source="web", mode="fast")`, `status(notebook_id)`, `import_sources(notebook_id, task_id)` |
| `client.studio` | `create(notebook_id, type, confirm=True)`, `status(notebook_id)`, `delete(notebook_id, artifact_id, confirm=True)` |
| `client.share` | `status(notebook_id)`, `set_public(notebook_id, is_public)`, `invite(notebook_id, email, role="viewer")` |
| `client.download` | `artifact(notebook_id, type, output_path)` |
| `client.note` | `create(notebook_id, content, title=...)`, `list(notebook_id)`, `update(notebook_id, note_id, ...)`, `delete(notebook_id, note_id, confirm=True)` |
| `client.auth` | `refresh()`, `save_tokens(cookies, ...)` |
| `client.export` | `to_docs(notebook_id, artifact_id)`, `to_sheets(notebook_id, artifact_id)` |

## Error Handling

All operations raise `NotebookLMError` subclasses on failure:

```python
from notebooklm_wrapper import (
    NotebookLMClient,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    GenerationError,
)

client = NotebookLMClient()

try:
    notebooks = client.notebook.list()
except AuthenticationError:
    print("Run 'nlm login' to authenticate")
except NotFoundError as e:
    print(f"Not found: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
```

Error messages include the tool name for easier debugging (e.g. `[notebook_list] Please login first`).

## Development

```bash
# Clone the repository
git clone https://github.com/ai-chitect/notebooklm-wrapper.git
cd notebooklm-wrapper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=notebooklm_wrapper --cov-report=term-missing

# Lint
ruff check src/ tests/

# Format
black src/ tests/
isort src/ tests/

# Type check
mypy src/

# Publish to PyPI (after tests pass)
./scripts/publish.sh

# Test OAuth + list notebooks (integration-style; opens browser for login)
python scripts/test_oauth_list_notebooks.py
# Reuse credentials in a directory (skip login next time):
python scripts/test_oauth_list_notebooks.py --config-dir ./tmp_oauth_test
python scripts/test_oauth_list_notebooks.py --config-dir ./tmp_oauth_test --skip-login
```

## Acknowledgments

This wrapper connects to the [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) MCP server by [Jacob Ben-David](https://github.com/jacob-bd), which provides the underlying NotebookLM integration. That project is MIT-licensed and compatible with this wrapper.

## License

MIT
