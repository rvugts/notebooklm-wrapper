"""Internal MCP client for connecting to notebooklm-mcp server.

Dependencies: json, shutil (stdlib), mcp (ClientSession, StdioServerParameters,
stdio_client, TextContent), typing.
"""

import json
import shutil
from typing import Any, cast

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from .exceptions import (
    AuthenticationError,
    GenerationError,
    NotebookLMError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def _find_notebooklm_mcp() -> str:
    """Find the notebooklm-mcp executable path.

    :return: Path to notebooklm-mcp or the string 'notebooklm-mcp'.
    """
    return shutil.which("notebooklm-mcp") or "notebooklm-mcp"


def _parse_tool_result(
    content: list[Any], structured_content: dict[str, Any] | None
) -> dict[str, Any]:
    """Parse MCP tool result into a dict.

    :param content: Raw content blocks from MCP response.
    :param structured_content: Optional pre-parsed structured content.
    :return: Result as a dict; empty dict if unparseable.
    """
    if structured_content is not None:
        return dict(structured_content)

    for block in content:
        if isinstance(block, TextContent) and block.text:
            try:
                return cast("dict[str, Any]", json.loads(block.text))
            except json.JSONDecodeError:
                return {"raw": block.text}
    return {}


class MCPClientManager:
    """Manages MCP server connection and tool calls."""

    def __init__(self, profile: str | None = None) -> None:
        """Initialize manager.

        :param profile: Optional NotebookLM profile name for env.
        """
        self.profile = profile
        self._read: Any = None
        self._write: Any = None
        self._session: ClientSession | None = None
        self._stdio_context: Any = None
        self._session_context: Any = None

    async def connect(self) -> ClientSession:
        """Start MCP server and establish session.

        :return: Initialized MCP client session.
        """
        if self._session is not None:
            return self._session

        command = _find_notebooklm_mcp()
        args: list[str] = []
        env: dict[str, str] | None = None
        if self.profile:
            env = {"NOTEBOOKLM_MCP_PROFILE": self.profile}

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
        )

        self._stdio_context = stdio_client(server_params)
        # Manual context entry: we exit in disconnect(), not in a single async with block
        read, write = await self._stdio_context.__aenter__()  # pylint: disable=C2801
        self._read = read
        self._write = write

        self._session_context = ClientSession(read, write)
        self._session = await self._session_context.__aenter__()  # pylint: disable=C2801
        await self._session.initialize()
        return self._session

    async def disconnect(self) -> None:
        """Close MCP connection and release resources."""
        if self._session_context is not None:
            await self._session_context.__aexit__(None, None, None)
            self._session_context = None
            self._session = None
        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(None, None, None)
            self._stdio_context = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call an MCP tool and return parsed result.

        :param name: Tool name.
        :param arguments: Tool arguments (None values are filtered out).
        :return: Parsed result dict.
        :raises NotebookLMError: On MCP or application error.
        """
        session = await self.connect()

        # Filter out None values for cleaner calls
        filtered_args = {k: v for k, v in arguments.items() if v is not None}

        result = await session.call_tool(name, filtered_args)

        if getattr(result, "is_error", getattr(result, "isError", False)):
            error_msg = ""
            for block in result.content:
                if isinstance(block, TextContent):
                    error_msg = block.text
                    break
            raise self._map_error(error_msg, name)

        data = _parse_tool_result(
            result.content,
            getattr(result, "structured_content", None),
        )

        # Handle status/error in response
        if isinstance(data, dict):
            status = data.get("status")
            if status == "error":
                err_text = str(data.get("error") or data.get("message") or "Unknown error")
                raise self._map_error(err_text, name)
            if data.get("error"):
                raise self._map_error(str(data["error"]), name)

        return data

    def _map_error(self, message: str, tool_name: str) -> NotebookLMError:
        """Map MCP error message to the appropriate exception type.

        :param message: Error message from the server.
        :param tool_name: Name of the tool that was called.
        :return: Concrete NotebookLMError subclass.
        """
        full_message = f"[{tool_name}] {message}" if message else f"[{tool_name}] Unknown error"
        msg_lower = message.lower()
        if "auth" in msg_lower or "login" in msg_lower or "credential" in msg_lower:
            return AuthenticationError(full_message)
        if "not found" in msg_lower or "404" in msg_lower:
            return NotFoundError(full_message)
        if "rate limit" in msg_lower or "429" in msg_lower:
            return RateLimitError(full_message)
        if "invalid" in msg_lower or "validation" in msg_lower:
            return ValidationError(full_message)
        if "generat" in msg_lower or "artifact" in msg_lower:
            return GenerationError(full_message)
        return NotebookLMError(full_message)
