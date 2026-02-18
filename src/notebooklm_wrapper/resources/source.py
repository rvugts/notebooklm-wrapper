"""Source resource - source management operations.

Dependencies: typing, MCPClientManager, ValidationError, models,
BaseResource.
"""

from typing import Any

from ..exceptions import ValidationError
from ..models import AddSourceResult, SourceContent, SourceSummary, SyncResult
from .base import BaseResource


class SourceResource(BaseResource):
    """Source management operations."""

    async def add(
        self,
        notebook_id: str,
        source_type: str,
        *,
        url: str | None = None,
        text: str | None = None,
        title: str | None = None,
        file_path: str | None = None,
        document_id: str | None = None,
        doc_type: str = "doc",
        wait: bool = False,
        wait_timeout: float = 120.0,
    ) -> AddSourceResult:
        """Add a source to a notebook.

        :param notebook_id: Target notebook ID.
        :param source_type: Type (url, text, drive, file, youtube).
        :param url: URL for url source type.
        :param text: Raw text for text type.
        :param title: Optional title.
        :param file_path: Path for file type.
        :param document_id: Drive document ID.
        :param doc_type: Drive doc type (e.g. doc, sheet).
        :param wait: Whether to wait for processing.
        :param wait_timeout: Timeout when wait is True.
        :return: Add result with source_id and title.
        """
        result = await self._call(
            "source_add",
            notebook_id=notebook_id,
            source_type=source_type,
            url=url,
            text=text,
            title=title,
            file_path=file_path,
            document_id=document_id,
            doc_type=doc_type,
            wait=wait,
            wait_timeout=wait_timeout,
        )
        return AddSourceResult.model_validate(result)

    async def list_drive(self, notebook_id: str) -> dict[str, Any]:
        """List sources with Drive freshness status.

        :param notebook_id: Notebook ID.
        :return: Drive source list/status.
        """
        return await self._call("source_list_drive", notebook_id=notebook_id)

    async def sync_drive(self, source_ids: list[str], *, confirm: bool = False) -> list[SyncResult]:
        """Sync Drive sources with latest content.

        :param source_ids: Source IDs to sync.
        :param confirm: Must be True to perform sync.
        :return: Per-source sync results.
        :raises ValidationError: If confirm is False or source_ids empty.
        """
        if not confirm:
            raise ValidationError("Must set confirm=True to sync Drive sources.")
        if not source_ids:
            raise ValidationError("source_ids cannot be empty")
        result = await self._call("source_sync_drive", source_ids=source_ids, confirm=True)
        results = result.get("results", [])
        return [SyncResult.model_validate(r) for r in results]

    async def delete(self, source_id: str, *, confirm: bool = False) -> None:
        """Delete a source permanently.

        :param source_id: Source ID.
        :param confirm: Must be True to perform delete.
        :raises ValidationError: If confirm is not True.
        """
        if not confirm:
            raise ValidationError("Must set confirm=True to delete source. This is irreversible.")
        await self._call("source_delete", source_id=source_id, confirm=True)

    async def describe(self, source_id: str) -> SourceSummary:
        """Get AI-generated source summary with keywords.

        :param source_id: Source ID.
        :return: Summary and keywords.
        """
        result = await self._call("source_describe", source_id=source_id)
        return SourceSummary(
            summary=result.get("summary", ""),
            keywords=result.get("keywords", []),
        )

    async def get_content(self, source_id: str) -> SourceContent:
        """Get raw text content of a source.

        :param source_id: Source ID.
        :return: Source content model.
        """
        result = await self._call("source_get_content", source_id=source_id)
        return SourceContent.model_validate(result)
