# Research start failure: "no confirmation from API"

## Where the error comes from

The message **`[research_start] Failed to start research — no confirmation from API`** is raised by **notebooklm-mcp-cli**, not by this wrapper.

In [notebooklm-mcp-cli `src/notebooklm_tools/services/research.py`](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/src/notebooklm_tools/services/research.py):

```python
try:
    result = client.start_research(
        notebook_id=notebook_id,
        query=query,
        source=source,
        mode=mode,
    )
except Exception as e:
    raise ServiceError(f"Failed to start research: {e}")

if result:
    return { ... }

raise ServiceError(
    "Research start returned no data",
    user_message="Failed to start research — no confirmation from API.",
)
```

So the error is raised when the **underlying NotebookLM client’s `start_research()` returns a falsy value** (e.g. `None` or `{}`). The Google/NotebookLM API call either returned nothing or the client did not get a usable response.

## Likely causes

1. **API returns no data** – The internal NotebookLM API sometimes returns an empty or unexpected payload (e.g. after a change on Google’s side, or when the request is not “confirmed” in their system).
2. **Cookie/session** – With cookie-based auth (e.g. `save_tokens`), the session might be missing headers or cookies that the browser sends when starting research (e.g. CSRF or extra confirmation). The UI may require a user confirmation step that has no equivalent in the API response we see.
3. **`notebook_id=None`** – Your test calls `research.start(..., notebook_id=None)`. The MCP server then calls the internal client with `notebook_id=None` (create-new-notebook path). That path might return a different response shape or no data in some cases.
4. **Rate limiting / account** – Research can be rate-limited or restricted for some accounts; the API might respond with an empty or non-success result.

## What to try

1. **Pass an existing notebook ID**  
   Call `research.start(query, notebook_id=<existing_nb_id>, ...)` instead of `notebook_id=None`, and see if the error persists.

2. **Use `mode="fast"`**  
   Try fast research first; deep research might have different API behavior or limits.

3. **Report upstream**  
   Open an issue on [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) with:
   - The exact error message
   - That you use cookie auth (`save_tokens`) and `notebook_id=None`
   - Ask whether `start_research` can return no data and what “no confirmation from API” means (e.g. which API response or condition triggers it)

4. **Compare with `nlm login`**  
   Run the same research flow (e.g. `nlm research start ...`) after a normal `nlm login` (browser) and see if it succeeds. If it works only with browser login, the difference is likely session/cookie/confirmation related.

## Wrapper behavior

This wrapper only forwards arguments to the MCP tool `research_start`. It does not add or require a `confirm` parameter; the MCP guide does not list one for research. The failure is in the MCP server / NotebookLM API layer, not in the wrapper’s call shape.
