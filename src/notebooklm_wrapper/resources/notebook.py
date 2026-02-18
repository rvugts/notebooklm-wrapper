"""Notebook resource - CRUD operations.

Dependencies: MCPClientManager, ValidationError, models, BaseResource.
"""

from ..exceptions import ValidationError
from ..models import Notebook, NotebookDetails, NotebookSummary, SourceInfo
from .base import BaseResource


class NotebookResource(BaseResource):
    """Notebook management operations."""

    async def list(self, max_results: int = 100) -> list[Notebook]:
        """List all notebooks.

        :param max_results: Maximum number of notebooks to return.
        :return: List of Notebook models.
        """
        result = await self._call("notebook_list", max_results=max_results)
        notebooks_data = result.get("notebooks", [])
        return [Notebook.model_validate(nb) for nb in notebooks_data]

    async def get(self, notebook_id: str) -> NotebookDetails:
        """Get notebook details with sources.

        :param notebook_id: Notebook ID.
        :return: Notebook details including source list.
        """
        result = await self._call("notebook_get", notebook_id=notebook_id)
        notebook_data = result.get("notebook", result)
        sources_data = result.get("sources", [])
        sources = [SourceInfo.model_validate(s) for s in sources_data]
        return NotebookDetails(
            **{k: v for k, v in notebook_data.items() if k != "sources"},
            sources=sources,
        )

    async def describe(self, notebook_id: str) -> NotebookSummary:
        """Get AI-generated notebook summary with suggested topics.

        :param notebook_id: Notebook ID.
        :return: Summary and suggested topics.
        """
        result = await self._call("notebook_describe", notebook_id=notebook_id)
        return NotebookSummary(
            summary=result.get("summary", ""),
            suggested_topics=result.get("suggested_topics", []),
        )

    async def create(self, title: str = "") -> Notebook:
        """Create a new notebook.

        :param title: Notebook title (can be empty).
        :return: Created Notebook model.
        """
        result = await self._call("notebook_create", title=title)
        notebook_data = result.get("notebook", result)
        if not notebook_data:
            notebook_data = {
                "id": result.get("notebook_id", ""),
                "title": result.get("title", title),
                "url": result.get("url"),
            }
        return Notebook.model_validate(notebook_data)

    async def rename(self, notebook_id: str, new_title: str) -> Notebook:
        """Rename a notebook.

        :param notebook_id: Notebook ID.
        :param new_title: New title (non-empty).
        :return: Updated Notebook model.
        :raises ValidationError: If new_title is empty.
        """
        if not new_title or not new_title.strip():
            raise ValidationError("New title cannot be empty")
        result = await self._call(
            "notebook_rename",
            notebook_id=notebook_id,
            new_title=new_title,
        )
        return Notebook.model_validate(
            {
                "id": notebook_id,
                "title": new_title,
                **result.get("notebook", result),
            }
        )

    async def delete(self, notebook_id: str, *, confirm: bool = False) -> None:
        """Delete a notebook permanently.

        :param notebook_id: Notebook ID.
        :param confirm: Must be True to perform delete.
        :raises ValidationError: If confirm is not True.
        """
        if not confirm:
            raise ValidationError("Must set confirm=True to delete notebook. This is irreversible.")
        await self._call("notebook_delete", notebook_id=notebook_id, confirm=True)
