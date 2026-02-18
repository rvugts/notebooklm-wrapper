"""Base resource class for MCP tool calls.

Dependencies: typing, MCPClientManager.
"""

from typing import Any

from .._mcp_client import MCPClientManager


class BaseResource:
    """Base class for all resource namespaces."""

    def __init__(self, mcp_manager: MCPClientManager) -> None:
        self._mcp = mcp_manager

    async def _call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """Call MCP tool with error handling.

        :param tool_name: MCP tool name.
        :param kwargs: Tool arguments (None values are filtered out by MCP).
        :return: Parsed tool result as a dict.
        """
        return await self._mcp.call_tool(tool_name, kwargs)
