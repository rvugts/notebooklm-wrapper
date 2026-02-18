"""Export resource - export to Google Docs/Sheets.

Dependencies: typing, MCPClientManager, BaseResource.
"""

from typing import Any

from .base import BaseResource


class ExportResource(BaseResource):
    """Export artifact operations."""

    async def to_docs(
        self,
        notebook_id: str,
        artifact_id: str,
        *,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Export artifact to Google Docs.

        :param notebook_id: Notebook ID.
        :param artifact_id: Artifact to export.
        :param title: Optional document title.
        :return: Export result (e.g. doc URL).
        """
        return await self._call(
            "export_artifact",
            notebook_id=notebook_id,
            artifact_id=artifact_id,
            export_type="docs",
            title=title,
        )

    async def to_sheets(
        self,
        notebook_id: str,
        artifact_id: str,
        *,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Export artifact to Google Sheets.

        :param notebook_id: Notebook ID.
        :param artifact_id: Artifact to export.
        :param title: Optional sheet title.
        :return: Export result (e.g. sheet URL).
        """
        return await self._call(
            "export_artifact",
            notebook_id=notebook_id,
            artifact_id=artifact_id,
            export_type="sheets",
            title=title,
        )
