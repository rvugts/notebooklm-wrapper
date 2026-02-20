# Multi-User / Web App Credential Isolation

This document describes how to use the notebooklm-wrapper in a multi-tenant web app where each user has their own NotebookLM credentials stored in your database (e.g. encrypted) and obtained via OAuth.

## How notebooklm-mcp-cli Stores Credentials

The underlying [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) server:

- Stores auth data under **`~/.notebooklm-mcp-cli`** (tokens, cookies, profile data).
- Uses **`NOTEBOOKLM_MCP_PROFILE`** (env) for a named profile; profiles are isolated under that directory.
- Does not document a separate env var to override the config base path; it follows the usual convention of using the process **`HOME`** for `~`.

So: if we spawn the MCP server with **`HOME`** set to a user-specific directory, the server will use **`<that_dir>/.notebooklm-mcp-cli`** for that process. That gives per-user credential isolation when you run one MCP process per user (or per session).

## Chosen Approach: `config_dir` and `HOME`

The wrapper adds an optional **`config_dir`** parameter to:

- `MCPClientManager(profile=..., config_dir=...)`
- `AsyncNotebookLMClient(profile=..., config_dir=...)`
- `NotebookLMClient(profile=..., config_dir=...)`

When **`config_dir`** is set:

1. The wrapper spawns the MCP server with **`HOME=<config_dir>`** (and copies the rest of the process environment so `PATH` etc. are preserved).
2. The server therefore uses **`<config_dir>/.notebooklm-mcp-cli`** for credentials and profile data.
3. You can use **`profile`** as a stable user or session id (e.g. `user_id`) so multiple profiles under the same `config_dir` stay separate if needed.

When **`config_dir`** is `None` (default), behavior is unchanged: the server uses the real `HOME` and existing “nlm login” / profile setup.

## Wrapper API for Multi-User

- **Isolated credential store:** Create a client with a user-specific directory:

  ```python
  client = AsyncNotebookLMClient(
      profile=user_id,           # optional; stable id for this user
      config_dir="/app/data/users/{}".format(user_id),
  )
  ```

- **Inject credentials:** After OAuth (or loading from your DB), call `save_tokens` so the server persists cookies for this process (and thus for this `config_dir`/profile):

  ```python
  await client.auth.save_tokens(cookies=decrypted_cookies_string)
  ```

- Then use the client as usual: `client.notebook.list()`, `client.notebook.create(...)`, etc. All tools in that session use the same credential store.

## End-to-End Flow (Web App)

1. **Store credentials:** When the user completes OAuth (or pastes cookies), encrypt and store the cookie string (or tokens) in your DB keyed by user id.
2. **Per request or session:** When the user wants to use NotebookLM:
   - Resolve a **user-specific directory** (e.g. `/app/data/users/<user_id>` or a temp dir you create per session). Ensure the directory exists.
   - **Decrypt** the credentials from your DB.
   - Create a client:  
     `AsyncNotebookLMClient(profile=user_id, config_dir=user_specific_dir)`.
   - If this is the first time (or you want to refresh), call  
     `await client.auth.save_tokens(cookies=decrypted_cookies)`.
   - Use the client for notebook/list/create/chat/etc.
   - When done, call `await client.disconnect()` and, if you use temp dirs, clean them up.
3. **One MCP process per client:** Each `AsyncNotebookLMClient` (with its own `config_dir`) spawns its own MCP server process, so users’ credentials and data stay isolated.

## Compatibility

- **Single-user / CLI:** Omit `config_dir`; use `profile` only if you use multiple profiles with `nlm login`. No change to existing behavior.
- **Tests:** All existing tests use the default `config_dir=None` and continue to pass.
