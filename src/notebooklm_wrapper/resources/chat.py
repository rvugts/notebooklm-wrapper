"""Chat resource - query and configuration.

Dependencies: typing, MCPClientManager, ChatResponse, BaseResource.
"""

from typing import Any

from ..models import ChatResponse
from .base import BaseResource


class ChatResource(BaseResource):
    """Chat and query operations."""

    async def ask(
        self,
        notebook_id: str,
        query: str,
        *,
        source_ids: list[str] | None = None,
        conversation_id: str | None = None,
        timeout: float | None = None,
    ) -> ChatResponse:
        """Ask a question about existing sources in the notebook.

        :param notebook_id: Target notebook ID.
        :param query: User question.
        :param source_ids: Optional source IDs to scope the query.
        :param conversation_id: Optional conversation to continue.
        :param timeout: Optional timeout in seconds.
        :return: Chat response with answer and citations.
        """
        result = await self._call(
            "notebook_query",
            notebook_id=notebook_id,
            query=query,
            source_ids=source_ids,
            conversation_id=conversation_id,
            timeout=timeout,
        )
        return ChatResponse.model_validate(result)

    async def configure(
        self,
        notebook_id: str,
        *,
        goal: str = "default",
        custom_prompt: str | None = None,
        response_length: str = "default",
    ) -> dict[str, Any]:
        """Configure notebook chat settings.

        :param notebook_id: Target notebook ID.
        :param goal: Chat goal (e.g. default, learning_guide).
        :param custom_prompt: Custom system prompt when goal is custom.
        :param response_length: Response length preference.
        :return: Configuration result.
        """
        return await self._call(
            "chat_configure",
            notebook_id=notebook_id,
            goal=goal,
            custom_prompt=custom_prompt,
            response_length=response_length,
        )
