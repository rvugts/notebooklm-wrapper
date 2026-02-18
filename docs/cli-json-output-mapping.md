# notebooklm-mcp-cli: CLI Command -> JSON Output Mapping

> Comprehensive analysis of every `nlm` CLI command, its flags, JSON output shape,
> error reporting patterns, confirmation prompts, and timeout/polling behavior.
> Based on source analysis of `notebooklm-mcp-cli` (GitHub: jacob-bd/notebooklm-mcp-cli).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Global Patterns](#global-patterns)
3. [Notebook Commands](#notebook-commands)
4. [Source Commands](#source-commands)
5. [Chat Commands](#chat-commands)
6. [Studio Commands](#studio-commands)
7. [Research Commands](#research-commands)
8. [Sharing Commands](#sharing-commands)
9. [Download Commands](#download-commands)
10. [Error Taxonomy](#error-taxonomy)

---

## Architecture Overview

### Layer Diagram

```
CLI Layer (typer commands)
  -> formatters.py -> detect_output_format() -> JsonFormatter / TableFormatter / CompactFormatter
      -> Services Layer (business logic, TypedDicts, validation)
          -> Client Layer (NotebookLMClient -- raw API calls)
```

### Output Format Selection (`formatters.py`)

The `detect_output_format()` function resolves the output mode:

| Condition | OutputFormat | Serialization |
|---|---|---|
| `--json` / `-j` flag | `JSON` | `json.dumps(data, indent=2)` via `print()` to **stdout** |
| `--quiet` / `-q` or `--title` / `-t` or `--url` / `-u` | `COMPACT` | Plain text IDs or `ID: value` to **stdout** |
| Non-TTY (piped) | `JSON` | Auto-detected; same as `--json` |
| Default (TTY, no flags) | `TABLE` | Rich tables via `Console` |

**Critical for subprocess parsing**: When stdout is **not a TTY** (i.e., captured by subprocess), the CLI automatically outputs JSON even without `--json`. This means `subprocess.run(capture_output=True)` will always get JSON by default for commands that use the formatter system.

### JSON Serialization

- All JSON from `JsonFormatter` is emitted via `print(json.dumps(data, indent=2))` to **stdout**
- All Rich-formatted messages (spinners, checkmarks, errors) go through `Console()` which writes to **stderr** by default in non-TTY mode
- `JsonFormatter.format_item()` calls `.model_dump(exclude_none=True)` for Pydantic models, or `.__dict__` filtering for plain objects

---

## Global Patterns

### Error Reporting

```
Pattern 1 -- ServiceError:
  stderr: "Error: {e.user_message}"
  exit code: 1

Pattern 2 -- NLMError (core):
  stderr: "Error: {e.message}"
  stderr: "Hint: {e.hint}"  (if hint exists)
  exit code: 1

Pattern 3 -- AuthenticationError:
  stderr: "Authentication Error"
  stderr: "  {str(e)}"
  stderr: "-> Run nlm login to re-authenticate"
  exit code: 1

Pattern 4 -- ArtifactNotReadyError (downloads only):
  stderr: "Error: {type} is not ready or does not exist."
  exit code: 1
```

Errors are **never** returned as JSON objects. They always go to **stderr** as Rich-formatted text with `typer.Exit(1)`.

### Confirmation Prompts (`--confirm` / `-y`)

Commands that modify or create resources prompt via `typer.confirm()` unless `--confirm`/`-y` is passed. For subprocess automation, **always pass `--confirm`/`-y`**.

Affected commands:
- `nlm notebook delete`
- `nlm source delete`
- `nlm source sync`
- `nlm studio delete`
- `nlm audio create`
- `nlm report create`
- `nlm quiz create`
- `nlm flashcards create`
- `nlm mindmap create`
- `nlm slides create`
- `nlm infographic create`
- `nlm video create`
- `nlm data-table create`
- `nlm login profile delete`

### Profile Selection

All commands accept `--profile`/`-p` to select an auth profile. Defaults to the config's `auth.default_profile`.

### Alias Resolution

All commands that take IDs pass them through `get_alias_manager().resolve(id)` which maps user-defined aliases to real UUIDs transparently.

---

## Notebook Commands

### `nlm notebook list`

```bash
nlm notebook list [--json|-j] [--quiet|-q] [--title|-t] [--full|-a] [--profile|-p PROFILE]
```

**JSON output** (`--json` or piped):
```json
[
  {
    "id": "uuid-string",
    "title": "My Notebook",
    "source_count": 5,
    "updated_at": "2025-01-15T10:30:00"
  }
]
```
- When `--full`: adds `"created_at": "2025-01-10T08:00:00"` to each item
- `updated_at` is either ISO string or `YYYY-MM-DD` date part
- Array is always a list, even if empty: `[]`

**Quiet output** (`--quiet`): One ID per line
```
uuid-1
uuid-2
```

**Title output** (`--title`): `ID: Title` per line
```
uuid-1: My Notebook
uuid-2: Research Notes
```

---

### `nlm notebook get <notebook_id>`

```bash
nlm notebook get <notebook_id> [--json|-j] [--profile|-p PROFILE]
```

**JSON output** (via service `NotebookDetailResult`):
```json
{
  "notebook_id": "uuid-string",
  "title": "My Notebook",
  "source_count": 3,
  "url": "https://notebooklm.google.com/notebook/uuid-string",
  "sources": [
    {"id": "source-uuid-1", "title": "Source A"},
    {"id": "source-uuid-2", "title": "Source B"}
  ]
}
```

---

### `nlm notebook describe <notebook_id>`

```bash
nlm notebook describe <notebook_id> [--json|-j] [--profile|-p PROFILE]
```

**JSON output** (via service `NotebookSummaryResult`):
```json
{
  "summary": "AI-generated summary text...",
  "suggested_topics": ["topic1", "topic2", "topic3"]
}
```

---

### `nlm notebook create [title]`

```bash
nlm notebook create [TITLE] [--profile|-p PROFILE]
```

**No `--json` flag.** Output is always Rich-formatted to stderr:
```
Created notebook: My Notebook
  ID: uuid-string
```

The service returns `NotebookCreateResult`:
```json
{
  "notebook_id": "uuid-string",
  "title": "My Notebook",
  "url": "https://notebooklm.google.com/notebook/uuid-string",
  "message": "Created notebook: My Notebook"
}
```
But the CLI only prints `message` and `notebook_id` as Rich text -- not JSON.

---

### `nlm notebook rename <notebook_id> <new_title>`

```bash
nlm notebook rename <notebook_id> <new_title> [--profile|-p PROFILE]
```

**No `--json` flag.** Output is Rich-formatted:
```
Renamed notebook to: New Title
```

Service returns `NotebookRenameResult`:
```json
{
  "notebook_id": "uuid",
  "new_title": "New Title",
  "message": "Renamed notebook to: New Title"
}
```

---

### `nlm notebook delete <notebook_id>`

```bash
nlm notebook delete <notebook_id> [--confirm|-y] [--profile|-p PROFILE]
```

**Confirmation prompt** unless `--confirm`/`-y`.

**No `--json` flag.** Output: `Notebook uuid has been permanently deleted.`

---

### `nlm notebook query <notebook_id> <question>`

```bash
nlm notebook query <notebook_id> <question> [--json|-j] \
  [--conversation-id|-c ID] [--source-ids|-s IDS] [--profile|-p PROFILE]
```

**JSON output** (via service `QueryResult`):
```json
{
  "answer": "The AI response text...",
  "conversation_id": "conv-uuid-or-null",
  "sources_used": [
    {"id": "source-uuid", "title": "Source Title"}
  ]
}
```

- `conversation_id` can be `null` on first query; use returned value for follow-ups
- `sources_used` is a list (may be empty)

---

## Source Commands

### `nlm source list <notebook_id>`

```bash
nlm source list <notebook_id> [--json|-j] [--quiet|-q] [--url|-u] \
  [--full|-a] [--drive|-d] [--skip-freshness|-S] [--profile|-p PROFILE]
```

**JSON output**:
```json
[
  {
    "id": "source-uuid",
    "title": "Source Title",
    "type": "web_page",
    "url": "https://example.com"
  }
]
```
- When `--full` or `--drive`: adds `"is_stale": false` to each item
- `type` is `source_type_name` from API (e.g., `"web_page"`, `"text"`, `"google_doc"`, `"pdf"`, `"youtube"`)

**Quiet output** (`--quiet`): One source ID per line

**URL output** (`--url`): `ID: URL` per line

---

### `nlm source add <notebook_id>`

```bash
nlm source add <notebook_id> \
  [--url|-u URL] [--text|-t TEXT] [--file|-f PATH] \
  [--drive|-d DOC_ID] [--youtube|-y URL] \
  [--title TITLE] [--type TYPE] [--wait|-w] [--profile|-p PROFILE]
```

**No `--json` flag.** Output is Rich-formatted:
```
Added source: Source Title (ready)
Source ID: source-uuid
```

Service returns `AddSourceResult`:
```json
{
  "source_type": "url",
  "source_id": "source-uuid",
  "title": "Page Title"
}
```

**`--wait` flag**: Blocks until source processing completes (service default: 120s `wait_timeout`).

---

### `nlm source get <source_id>`

```bash
nlm source get <source_id> [--json|-j] [--profile|-p PROFILE]
```

**JSON output**: Passes through `client.get_source_fulltext()` result via `format_item()`.

---

### `nlm source describe <source_id>`

```bash
nlm source describe <source_id> [--json|-j] [--profile|-p PROFILE]
```

**JSON output** via `format_item()`:
```json
{
  "summary": "AI summary of the source...",
  "keywords": ["keyword1", "keyword2"]
}
```

---

### `nlm source content <source_id>`

```bash
nlm source content <source_id> [--json|-j] [--output|-o FILE] [--profile|-p PROFILE]
```

**JSON output**:
```json
{
  "content": "Full text of the source...",
  "title": "Source Title",
  "source_type": "web_page",
  "char_count": 12345
}
```

With `--output FILE`: writes raw content to file, prints confirmation to stderr.

---

### `nlm source delete <source_id>`

```bash
nlm source delete <source_id> [--confirm|-y] [--profile|-p PROFILE]
```

**Confirmation prompt** unless `--confirm`/`-y`. Output: `Deleted source: source-uuid`

---

### `nlm source stale <notebook_id>`

```bash
nlm source stale <notebook_id> [--json|-j] [--profile|-p PROFILE]
```

**JSON output**: Same shape as `source list` with `--full` -- array of source objects with `is_stale`.

---

### `nlm source sync <notebook_id>`

```bash
nlm source sync <notebook_id> [--source-ids|-s IDS] [--confirm|-y] [--profile|-p PROFILE]
```

**Confirmation prompt** unless `--confirm`/`-y`. **No `--json` flag.** Output: `Synced N source(s)`

Service returns `list[SyncResult]`:
```json
[
  {"source_id": "uuid", "synced": true, "error": null},
  {"source_id": "uuid2", "synced": false, "error": "error message"}
]
```

---

## Chat Commands

### `nlm chat configure <notebook_id>`

```bash
nlm chat configure <notebook_id> \
  [--goal|-g GOAL] [--prompt PROMPT] [--response-length|-r LENGTH] \
  [--profile|-p PROFILE]
```

- `goal`: `default`, `learning_guide`, or `custom`
- `response_length`: `default`, `longer`, or `shorter`
- `prompt`: required when `goal=custom`, max 10000 chars

**No `--json` flag.** Service returns `ConfigureResult`:
```json
{
  "notebook_id": "uuid",
  "goal": "learning_guide",
  "response_length": "default",
  "message": "Chat settings updated."
}
```

### `nlm chat start <notebook_id>`

Interactive REPL -- not suitable for subprocess wrapping.

---

## Studio Commands

### `nlm studio status <notebook_id>`

```bash
nlm studio status <notebook_id> [--json|-j] [--full|-a] [--profile|-p PROFILE]
```

**JSON output**:
```json
[
  {
    "id": "artifact-uuid",
    "type": "audio",
    "status": "completed",
    "custom_instructions": null
  }
]
```
- When `--full`: adds `"title": "..."` and `"url": "..."` to each item
- `status` values: `"completed"`, `"pending"`, `"in_progress"`, `"failed"`
- `custom_instructions` is always included (may be `null`)

---

### `nlm studio delete <notebook_id> <artifact_id>`

```bash
nlm studio delete <notebook_id> <artifact_id> [--confirm|-y] [--profile|-p PROFILE]
```

**Confirmation prompt** unless `--confirm`/`-y`. Output: `Deleted artifact: artifact-uuid`

---

### `nlm studio rename <artifact_id> <new_title>`

```bash
nlm studio rename <artifact_id> <new_title> [--profile|-p PROFILE]
```

Output: `Renamed artifact to: New Title`

---

### Generation Commands

All generation commands share the same output pattern via `_run_create()`:

```bash
nlm audio create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm video create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm report create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm quiz create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm flashcards create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm mindmap create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm slides create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm infographic create <notebook_id> [options] [--confirm|-y] [--profile|-p PROFILE]
nlm data-table create <notebook_id> <description> [options] [--confirm|-y] [--profile|-p PROFILE]
```

**All require `--confirm`/`-y` for automation.**
**No `--json` flag on any creation command.** All output is Rich-formatted.

**Standard artifact output**:
```
Audio generation started
  Artifact ID: artifact-uuid
Run 'nlm studio status <notebook_id>' to check progress.
```

**Mind map output** (synchronous creation):
```
Mind map created
  ID: artifact-uuid
  Title: Mind Map
```

**Service return shapes**:

`CreateResult` (standard artifacts):
```json
{
  "artifact_type": "audio",
  "artifact_id": "uuid",
  "status": "in_progress",
  "message": "Audio generation started."
}
```

`MindMapResult` (mind maps):
```json
{
  "artifact_type": "mind_map",
  "artifact_id": "uuid",
  "title": "Mind Map",
  "root_name": "Main Topic",
  "children_count": 5,
  "message": "Mind map created successfully."
}
```

#### Audio options
| Flag | Values | Default |
|------|--------|---------|
| `--format`/`-f` | `deep_dive`, `brief`, `critique`, `debate` | `deep_dive` |
| `--length`/`-l` | `short`, `default`, `long` | `default` |
| `--language` | BCP-47 code | `en` |
| `--focus` | topic string | none |
| `--source-ids`/`-s` | comma-separated | all sources |

#### Video options
| Flag | Values | Default |
|------|--------|---------|
| `--format`/`-f` | `explainer`, `brief` | `explainer` |
| `--style`/`-s` | `auto_select`, `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft` | `auto_select` |
| `--language` | BCP-47 | `en` |
| `--focus` | topic string | none |

#### Report options
| Flag | Values | Default |
|------|--------|---------|
| `--format`/`-f` | `Briefing Doc`, `Study Guide`, `Blog Post`, `Create Your Own` | `Briefing Doc` |
| `--prompt` | custom prompt (required for `Create Your Own`) | none |
| `--language` | BCP-47 | `en` |

#### Quiz options
| Flag | Values | Default |
|------|--------|---------|
| `--count`/`-c` | integer | `2` |
| `--difficulty`/`-d` | `1`-`5` (1=easy, 5=hard) | `2` |
| `--focus`/`-f` | topic string | none |

#### Flashcard options
| Flag | Values | Default |
|------|--------|---------|
| `--difficulty`/`-d` | `easy`, `medium`, `hard` | `medium` |
| `--focus`/`-f` | topic string | none |

#### Slide options
| Flag | Values | Default |
|------|--------|---------|
| `--format`/`-f` | `detailed_deck`, `presenter_slides` | `detailed_deck` |
| `--length`/`-l` | `short`, `default` | `default` |
| `--language` | BCP-47 | `en` |
| `--focus` | topic string | none |

#### Infographic options
| Flag | Values | Default |
|------|--------|---------|
| `--orientation`/`-o` | `landscape`, `portrait`, `square` | `landscape` |
| `--detail`/`-d` | `concise`, `standard`, `detailed` | `standard` |
| `--language` | BCP-47 | `en` |
| `--focus` | topic string | none |

#### Data Table options
| Flag | Values | Default |
|------|--------|---------|
| `description` | positional argument (required) | -- |
| `--language` | BCP-47 | `en` |

---

## Research Commands

### `nlm research start <query>`

```bash
nlm research start <query> \
  --notebook-id|-n ID \
  [--source|-s web|drive] [--mode|-m fast|deep] \
  [--title|-t TITLE] [--force|-f] [--profile|-p PROFILE]
```

**No `--json` flag.** Rich output with Task ID, Query, Source, Mode, Notebook ID.

**`--force` flag**: Skips check for existing in-progress/completed research.

Service returns `ResearchStartResult`:
```json
{
  "task_id": "task-uuid",
  "notebook_id": "uuid",
  "query": "quantum computing basics",
  "source": "web",
  "mode": "fast",
  "message": "Research started. Use research_status to check progress."
}
```

---

### `nlm research status <notebook_id>`

```bash
nlm research status <notebook_id> \
  [--task-id|-t ID] [--compact/--full] \
  [--poll-interval N] [--max-wait N] [--profile|-p PROFILE]
```

**Polling behavior**:
- Default `--poll-interval`: 30 seconds
- Default `--max-wait`: 300 seconds (5 minutes)
- `--max-wait 0`: Single status check, no polling
- Polls until status is `"completed"` or timeout

Service returns `ResearchStatusResult`:
```json
{
  "status": "completed",
  "notebook_id": "uuid",
  "task_id": "task-uuid",
  "sources_found": 10,
  "sources": [
    {"title": "Source A", "url": "https://..."}
  ],
  "report": "Research summary text...",
  "message": "Use research_import to add sources to notebook."
}
```

Status values: `"completed"`, `"pending"`, `"running"`, `"in_progress"`, `"no_research"`, `"failed"`

With `--compact` (default): report truncated to 500 chars, sources capped at 5.

---

### `nlm research import <notebook_id> [task_id]`

```bash
nlm research import <notebook_id> [TASK_ID] \
  [--indices|-i INDICES] [--profile|-p PROFILE]
```

Auto-detects task ID if not provided.

Service returns `ResearchImportResult`:
```json
{
  "notebook_id": "uuid",
  "imported_count": 5,
  "imported_sources": [
    {"title": "Source A", "id": "source-uuid"}
  ],
  "message": "Imported 5 sources."
}
```

---

## Sharing Commands

### `nlm share status <notebook>`

```bash
nlm share status <notebook> [--json|-j] [--profile|-p PROFILE]
```

**JSON output** (directly via `json.dumps`, NOT through formatter):
```json
{
  "notebook_id": "uuid",
  "is_public": true,
  "access_level": "public",
  "public_link": "https://notebooklm.google.com/notebook/uuid?sharing=true",
  "collaborators": [
    {
      "email": "user@example.com",
      "role": "editor",
      "is_pending": false,
      "display_name": "User Name"
    }
  ],
  "collaborator_count": 1
}
```

**WARNING**: This command uses `console.print(json.dumps(...))` which routes through Rich Console, NOT `print()`. In non-TTY mode the JSON may go to stderr, not stdout. Always use `--json` explicitly.

---

### `nlm share public <notebook>`

```bash
nlm share public <notebook> [--profile|-p PROFILE]
```

**No `--json` flag.** Rich output: `Public access enabled` + link.

---

### `nlm share private <notebook>`

```bash
nlm share private <notebook> [--profile|-p PROFILE]
```

**No `--json` flag.** Rich output: `Public access disabled`.

---

### `nlm share invite <notebook> <email>`

```bash
nlm share invite <notebook> <email> [--role|-r viewer|editor] [--profile|-p PROFILE]
```

**No `--json` flag.** Rich output with invitation confirmation.

---

## Download Commands

All download commands write files to disk. They have **no `--json` flag**.

### Streaming Downloads (with progress bars)

```bash
nlm download audio <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--no-progress]
nlm download video <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--no-progress]
nlm download slide-deck <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--no-progress]
nlm download infographic <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--no-progress]
```

Default filenames: `{notebook_id}_audio.m4a`, `_video.mp4`, `_slides.pdf`, `_infographic.png`

Errors go to **stderr** via `err_console = Console(stderr=True)`.

### Simple Downloads (synchronous)

```bash
nlm download report <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID]
nlm download mind-map <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID]
nlm download data-table <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID]
```

Default filenames: `{notebook_id}_report.md`, `_mindmap.json`, `_table.csv`

### Interactive Format Downloads

```bash
nlm download quiz <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--format|-f json|markdown|html]
nlm download flashcards <notebook_id> [--output|-o PATH] [--id ARTIFACT_ID] [--format|-f json|markdown|html]
```

Service returns `DownloadResult`:
```json
{
  "artifact_type": "audio",
  "path": "/absolute/path/to/file"
}
```

---

## Error Taxonomy

### Exception Hierarchy

```
ServiceError (base)
  ValidationError     -- invalid input params
  NotFoundError       -- resource not found
  CreationError       -- creation failed
  ExportError         -- export failed

NLMError (core)       -- low-level API errors
  AuthenticationError
  ClientAuthenticationError

ArtifactNotReadyError -- download-specific
```

### Error Reporting Summary

| Layer | Destination | Format | Exit Code |
|-------|-------------|--------|-----------|
| `ServiceError` | stderr | `Error: {user_message}` | 1 |
| `NLMError` | stderr | `Error: {message}` + optional `Hint: {hint}` | 1 |
| `AuthenticationError` | stderr | `Authentication Error` + hint to `nlm login` | 1 |
| `ArtifactNotReadyError` | stderr | `Error: {type} is not ready or does not exist.` | 1 |
| Unexpected exception | stderr | Full traceback (re-raised) | non-zero |

---

## Subprocess Wrapping Recommendations

### Reliable JSON Capture Pattern

```python
import subprocess, json

result = subprocess.run(
    ["nlm", "notebook", "list", "--json"],
    capture_output=True,
    text=True,
    timeout=60,
)

if result.returncode != 0:
    raise RuntimeError(f"nlm failed: {result.stderr.strip()}")

data = json.loads(result.stdout)
```

### Commands That Support `--json`

| Command | `--json` flag | Auto-JSON when piped |
|---------|---------------|----------------------|
| `nlm notebook list` | Yes | Yes |
| `nlm notebook get` | Yes | Yes |
| `nlm notebook describe` | Yes | Yes |
| `nlm notebook query` | Yes | Yes |
| `nlm source list` | Yes | Yes |
| `nlm source get` | Yes | Yes |
| `nlm source describe` | Yes | Yes |
| `nlm source content` | Yes | Yes |
| `nlm source stale` | Yes | Yes |
| `nlm studio status` | Yes | Yes |
| `nlm share status` | Yes | Caution (see note) |

### Commands That Do NOT Support `--json`

| Command | Output Pattern |
|---------|---------------|
| `nlm notebook create` | `{message}\n  ID: {id}` |
| `nlm notebook rename` | `{message}` |
| `nlm notebook delete` | `{message}` |
| `nlm source add` | `Added source: {title}\nSource ID: {id}` |
| `nlm source delete` | `Deleted source: {id}` |
| `nlm source sync` | `Synced N source(s)` |
| `nlm chat configure` | `Chat configuration updated` |
| `nlm studio delete` | `Deleted artifact: {id}` |
| `nlm studio rename` | `Renamed artifact to: {title}` |
| All `{type} create` | `{Type} generation started\n  Artifact ID: {id}` |
| `nlm research start` | `Research started\n  Task ID: {id}` |
| `nlm research status` | Rich status display |
| `nlm research import` | `Imported N sources.` |
| `nlm share public` | `Public access enabled\nLink: {url}` |
| `nlm share private` | `Public access disabled` |
| `nlm share invite` | `{message}` |
| All `nlm download *` | `Downloaded {type} to: {path}` |

### Regex Patterns for Parsing Non-JSON Commands

```python
import re

# Extract ID from creation commands
id_pattern = re.compile(r"(?:ID|Artifact ID|Source ID|Task ID):\s*(\S+)")

# Extract success message
success_pattern = re.compile(r"\\u2713\s+(.+)")  # checkmark unicode

# Extract error message from stderr
error_pattern = re.compile(r"Error:\s*(.+)")
```

### Recommended Approach for Non-JSON Commands

For commands that lack `--json`, the most reliable wrapper strategy is to **import the service layer directly** rather than parsing CLI text:

```python
from notebooklm_tools.services import notebooks, studio, chat, research, sharing, sources, downloads
from notebooklm_tools.core.client import NotebookLMClient

# Get a client (reuse auth infrastructure)
client = NotebookLMClient(cookies=..., csrf_token=..., session_id=...)

# Call service functions directly -- returns typed dicts
result = notebooks.create_notebook(client, "My Notebook")
# result = {"notebook_id": "uuid", "title": "My Notebook", "url": "...", "message": "..."}
```

This bypasses all CLI formatting concerns and gives you the raw TypedDict results documented above.
