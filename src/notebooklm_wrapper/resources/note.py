"""Note resource - note management.

Dependencies: typing, MCPClientManager, ValidationError, BaseResource.
"""

from typing import Any

from ..exceptions import ValidationError
from .base import BaseResource


class NoteResource(BaseResource):
    """Note management operations."""

    async def create(
        self,
        notebook_id: str,
        content: str,
        *,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Create a note in a notebook.

        :param notebook_id: Target notebook ID.
        :param content: Note body text.
        :param title: Optional note title.
        :return: Created note info.
        """
        return await self._call(
            "note",
            notebook_id=notebook_id,
            action="create",
            content=content,
            title=title,
        )

    async def list(self, notebook_id: str) -> dict[str, Any]:
        """List notes in a notebook.

        :param notebook_id: Notebook ID.
        :return: List of notes (in result dict).
        """
        return await self._call("note", notebook_id=notebook_id, action="list")

    async def update(
        self,
        notebook_id: str,
        note_id: str,
        *,
        content: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Update a note.

        :param notebook_id: Notebook ID.
        :param note_id: Note to update.
        :param content: New content (optional).
        :param title: New title (optional).
        :return: Update result.
        """
        return await self._call(
            "note",
            notebook_id=notebook_id,
            action="update",
            note_id=note_id,
            content=content,
            title=title,
        )

    async def delete(
        self, notebook_id: str, note_id: str, *, confirm: bool = False
    ) -> dict[str, Any]:
        """Delete a note.

        :param notebook_id: Notebook ID.
        :param note_id: Note to delete.
        :param confirm: Must be True to perform delete.
        :return: Delete result.
        :raises ValidationError: If confirm is not True.
        """
        if not confirm:
            raise ValidationError("Must set confirm=True to delete note.")
        return await self._call(
            "note",
            notebook_id=notebook_id,
            action="delete",
            note_id=note_id,
            confirm=True,
        )
