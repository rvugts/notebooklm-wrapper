"""Auth resource - authentication management.

Dependencies: typing, MCPClientManager, BaseResource.
"""

from typing import Any

from .base import BaseResource


class AuthResource(BaseResource):
    """Authentication operations."""

    async def refresh(self) -> dict[str, Any]:
        """Reload auth tokens from disk or run headless re-authentication.

        :return: Auth status/result from the server.
        """
        return await self._call("refresh_auth")

    async def save_tokens(
        self,
        cookies: str,
        *,
        csrf_token: str | None = None,
        session_id: str | None = None,
        request_body: str | None = None,
        request_url: str | None = None,
    ) -> dict[str, Any]:
        """Save NotebookLM cookies (fallback - try nlm login first).

        :param cookies: Cookie string from browser.
        :param csrf_token: Optional CSRF token.
        :param session_id: Optional session ID.
        :param request_body: Optional request body.
        :param request_url: Optional request URL.
        :return: Save result from the server.
        """
        return await self._call(
            "save_auth_tokens",
            cookies=cookies,
            csrf_token=csrf_token,
            session_id=session_id,
            request_body=request_body,
            request_url=request_url,
        )
