"""Synchronous NotebookLM client.

Dependencies: asyncio (stdlib), AsyncNotebookLMClient, resource classes.
"""

import asyncio
from typing import Any

from .async_client import AsyncNotebookLMClient
from .resources import (
    AuthResource,
    ChatResource,
    DownloadResource,
    ExportResource,
    NotebookResource,
    NoteResource,
    ResearchResource,
    ShareResource,
    SourceResource,
    StudioResource,
)


def _run_async(coro: object) -> Any:
    """Run async coroutine in sync context.

    :param coro: Awaitable to run.
    :return: Result of the coroutine.
    :raises RuntimeError: If called from an already running event loop.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        raise RuntimeError(
            "Cannot use sync client from async context. Use AsyncNotebookLMClient instead."
        )
    return loop.run_until_complete(coro)


class SyncNotebookResource:
    """Sync wrapper for NotebookResource."""

    def __init__(self, async_resource: NotebookResource) -> None:
        self._async = async_resource

    def list(self, max_results: int = 100) -> list[Any]:
        """List notebooks."""
        return _run_async(self._async.list(max_results=max_results))

    def get(self, notebook_id: str) -> Any:
        """Get notebook details."""
        return _run_async(self._async.get(notebook_id))

    def describe(self, notebook_id: str) -> Any:
        """Get notebook summary."""
        return _run_async(self._async.describe(notebook_id))

    def create(self, title: str = "") -> Any:
        """Create a notebook."""
        return _run_async(self._async.create(title=title))

    def rename(self, notebook_id: str, new_title: str) -> Any:
        """Rename a notebook."""
        return _run_async(self._async.rename(notebook_id, new_title))

    def delete(self, notebook_id: str, *, confirm: bool = False) -> None:
        """Delete a notebook."""
        return _run_async(self._async.delete(notebook_id, confirm=confirm))


class SyncSourceResource:
    """Sync wrapper for SourceResource."""

    def __init__(self, async_resource: SourceResource) -> None:
        self._async = async_resource

    def add(self, notebook_id: str, source_type: str, **kwargs: Any) -> Any:
        """Add a source."""
        return _run_async(self._async.add(notebook_id, source_type, **kwargs))

    def list_drive(self, notebook_id: str) -> Any:
        """List Drive sources."""
        return _run_async(self._async.list_drive(notebook_id))

    def sync_drive(self, source_ids: list[str], *, confirm: bool = False) -> Any:
        """Sync Drive sources."""
        return _run_async(self._async.sync_drive(source_ids, confirm=confirm))

    def delete(self, source_id: str, *, confirm: bool = False) -> None:
        """Delete a source."""
        return _run_async(self._async.delete(source_id, confirm=confirm))

    def describe(self, source_id: str) -> Any:
        """Describe a source."""
        return _run_async(self._async.describe(source_id))

    def get_content(self, source_id: str) -> Any:
        """Get source content."""
        return _run_async(self._async.get_content(source_id))


class SyncChatResource:
    """Sync wrapper for ChatResource."""

    def __init__(self, async_resource: ChatResource) -> None:
        self._async = async_resource

    def ask(self, notebook_id: str, query: str, **kwargs: Any) -> Any:
        """Ask a question."""
        return _run_async(self._async.ask(notebook_id, query, **kwargs))

    def configure(self, notebook_id: str, **kwargs: Any) -> Any:
        """Configure chat."""
        return _run_async(self._async.configure(notebook_id, **kwargs))


class SyncResearchResource:
    """Sync wrapper for ResearchResource."""

    def __init__(self, async_resource: ResearchResource) -> None:
        self._async = async_resource

    def start(self, query: str, **kwargs: Any) -> Any:
        """Start research."""
        return _run_async(self._async.start(query, **kwargs))

    def status(self, notebook_id: str, **kwargs: Any) -> Any:
        """Get research status."""
        return _run_async(self._async.status(notebook_id, **kwargs))

    def import_sources(self, notebook_id: str, task_id: str, **kwargs: Any) -> Any:
        """Import research sources."""
        return _run_async(self._async.import_sources(notebook_id, task_id, **kwargs))


class SyncStudioResource:
    """Sync wrapper for StudioResource."""

    def __init__(self, async_resource: StudioResource) -> None:
        self._async = async_resource

    def create(self, notebook_id: str, artifact_type: str, **kwargs: Any) -> Any:
        """Create studio artifact."""
        return _run_async(self._async.create(notebook_id, artifact_type, **kwargs))

    def status(self, notebook_id: str, **kwargs: Any) -> Any:
        """Get studio status."""
        return _run_async(self._async.status(notebook_id, **kwargs))

    def delete(
        self,
        notebook_id: str,
        artifact_id: str,
        *,
        confirm: bool = False,
    ) -> None:
        """Delete studio artifact."""
        return _run_async(self._async.delete(notebook_id, artifact_id, confirm=confirm))


class SyncShareResource:
    """Sync wrapper for ShareResource."""

    def __init__(self, async_resource: ShareResource) -> None:
        self._async = async_resource

    def status(self, notebook_id: str) -> Any:
        """Get share status."""
        return _run_async(self._async.status(notebook_id))

    def set_public(self, notebook_id: str, is_public: bool = True) -> Any:
        """Set public link."""
        return _run_async(self._async.set_public(notebook_id, is_public))

    def invite(
        self,
        notebook_id: str,
        email: str,
        *,
        role: str = "viewer",
    ) -> Any:
        """Invite collaborator."""
        return _run_async(self._async.invite(notebook_id, email, role=role))


class SyncDownloadResource:
    """Sync wrapper for DownloadResource."""

    def __init__(self, async_resource: DownloadResource) -> None:
        self._async = async_resource

    def artifact(
        self,
        notebook_id: str,
        artifact_type: str,
        output_path: str,
        **kwargs: Any,
    ) -> Any:
        """Download artifact to file."""
        return _run_async(self._async.artifact(notebook_id, artifact_type, output_path, **kwargs))


class SyncNoteResource:
    """Sync wrapper for NoteResource."""

    def __init__(self, async_resource: NoteResource) -> None:
        self._async = async_resource

    def create(self, notebook_id: str, content: str, **kwargs: Any) -> Any:
        """Create a note."""
        return _run_async(self._async.create(notebook_id, content, **kwargs))

    def list(self, notebook_id: str) -> Any:
        """List notes."""
        return _run_async(self._async.list(notebook_id))

    def update(self, notebook_id: str, note_id: str, **kwargs: Any) -> Any:
        """Update a note."""
        return _run_async(self._async.update(notebook_id, note_id, **kwargs))

    def delete(
        self,
        notebook_id: str,
        note_id: str,
        *,
        confirm: bool = False,
    ) -> Any:
        """Delete a note."""
        return _run_async(self._async.delete(notebook_id, note_id, confirm=confirm))


class SyncAuthResource:
    """Sync wrapper for AuthResource."""

    def __init__(self, async_resource: AuthResource) -> None:
        self._async = async_resource

    def refresh(self) -> Any:
        """Refresh auth tokens."""
        return _run_async(self._async.refresh())

    def save_tokens(self, cookies: str, **kwargs: Any) -> Any:
        """Save auth tokens."""
        return _run_async(self._async.save_tokens(cookies, **kwargs))


class SyncExportResource:
    """Sync wrapper for ExportResource."""

    def __init__(self, async_resource: ExportResource) -> None:
        self._async = async_resource

    def to_docs(
        self,
        notebook_id: str,
        artifact_id: str,
        **kwargs: Any,
    ) -> Any:
        """Export to Google Docs."""
        return _run_async(self._async.to_docs(notebook_id, artifact_id, **kwargs))

    def to_sheets(
        self,
        notebook_id: str,
        artifact_id: str,
        **kwargs: Any,
    ) -> Any:
        """Export to Google Sheets."""
        return _run_async(self._async.to_sheets(notebook_id, artifact_id, **kwargs))


class NotebookLMClient:
    """
    Synchronous client for NotebookLM operations via MCP protocol.

    Wraps AsyncNotebookLMClient and runs operations in the event loop.

    Example:
        >>> client = NotebookLMClient()
        >>> notebooks = client.notebook.list()
        >>> notebook = client.notebook.create(title="My Research")
        >>> response = client.chat.ask(notebook.id, "What are the main points?")
    """

    def __init__(self, profile: str | None = None) -> None:
        """Initialize sync client.

        :param profile: NotebookLM profile to use. If None, uses default.
        """
        self._async_client = AsyncNotebookLMClient(profile=profile)
        self.notebook = SyncNotebookResource(self._async_client.notebook)
        self.source = SyncSourceResource(self._async_client.source)
        self.chat = SyncChatResource(self._async_client.chat)
        self.research = SyncResearchResource(self._async_client.research)
        self.studio = SyncStudioResource(self._async_client.studio)
        self.share = SyncShareResource(self._async_client.share)
        self.download = SyncDownloadResource(self._async_client.download)
        self.note = SyncNoteResource(self._async_client.note)
        self.auth = SyncAuthResource(self._async_client.auth)
        self.export = SyncExportResource(self._async_client.export)

    @property
    def profile(self) -> str | None:
        """Get current profile name."""
        return self._async_client.profile
