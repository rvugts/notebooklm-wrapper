"""Download resource - artifact downloads.

Dependencies: pathlib, typing, MCPClientManager, BaseResource.
"""

from pathlib import Path
from typing import Any

from .base import BaseResource


class DownloadResource(BaseResource):
    """Artifact download operations."""

    async def artifact(
        self,
        notebook_id: str,
        artifact_type: str,
        output_path: str | Path,
        *,
        artifact_id: str | None = None,
        output_format: str = "json",
    ) -> dict[str, Any]:
        """Download any artifact to a file.

        :param notebook_id: Notebook ID.
        :param artifact_type: Type of artifact (e.g. report, slide_deck).
        :param output_path: Local path to write the file.
        :param artifact_id: Optional specific artifact ID.
        :param output_format: Output format (e.g. json).
        :return: Download result from the server.
        """
        path_str = str(output_path) if isinstance(output_path, Path) else output_path
        return await self._call(
            "download_artifact",
            notebook_id=notebook_id,
            artifact_type=artifact_type,
            output_path=path_str,
            artifact_id=artifact_id,
            output_format=output_format,
        )
