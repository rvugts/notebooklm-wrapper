"""Async NotebookLM client.

Dependencies: MCPClientManager, resource classes.
"""

from ._mcp_client import MCPClientManager
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


class AsyncNotebookLMClient:
    """
    Async client for NotebookLM operations via MCP protocol.

    Connects to the notebooklm-mcp server and provides typed access to all
    NotebookLM functionality.

    Example:
        >>> async def main():
        ...     client = AsyncNotebookLMClient()
        ...     notebooks = await client.notebook.list()
        ...     notebook = await client.notebook.create(title="My Research")
        >>> import asyncio
        >>> asyncio.run(main())
    """

    def __init__(self, profile: str | None = None) -> None:
        """Initialize async client.

        :param profile: NotebookLM profile to use. If None, uses default
            from nlm login.
        """
        self._mcp = MCPClientManager(profile=profile)
        self.notebook = NotebookResource(self._mcp)
        self.source = SourceResource(self._mcp)
        self.chat = ChatResource(self._mcp)
        self.research = ResearchResource(self._mcp)
        self.studio = StudioResource(self._mcp)
        self.share = ShareResource(self._mcp)
        self.download = DownloadResource(self._mcp)
        self.note = NoteResource(self._mcp)
        self.auth = AuthResource(self._mcp)
        self.export = ExportResource(self._mcp)

    @property
    def profile(self) -> str | None:
        """Get current profile name."""
        return self._mcp.profile

    async def disconnect(self) -> None:
        """Close MCP connection."""
        await self._mcp.disconnect()
