"""Share resource - sharing and collaboration.

Dependencies: typing, MCPClientManager, ShareStatus, BaseResource.
"""

from typing import Any

from ..models import ShareStatus
from .base import BaseResource


class ShareResource(BaseResource):
    """Sharing and collaboration operations."""

    async def status(self, notebook_id: str) -> ShareStatus:
        """Get current sharing settings and collaborators.

        :param notebook_id: Notebook ID.
        :return: Share status with collaborators and public link.
        """
        result = await self._call("notebook_share_status", notebook_id=notebook_id)
        return ShareStatus.model_validate(result)

    async def set_public(self, notebook_id: str, is_public: bool = True) -> dict[str, Any]:
        """Enable or disable public link access.

        :param notebook_id: Notebook ID.
        :param is_public: Whether to enable public link.
        :return: Update result.
        """
        return await self._call(
            "notebook_share_public",
            notebook_id=notebook_id,
            is_public=is_public,
        )

    async def invite(
        self,
        notebook_id: str,
        email: str,
        *,
        role: str = "viewer",
    ) -> dict[str, Any]:
        """Invite a collaborator by email.

        :param notebook_id: Notebook ID.
        :param email: Collaborator email.
        :param role: Role (e.g. viewer, editor).
        :return: Invite result.
        """
        return await self._call(
            "notebook_share_invite",
            notebook_id=notebook_id,
            email=email,
            role=role,
        )
