"""Tests for MCP client error mapping and tool name in exceptions.

Dependencies: notebooklm_wrapper._mcp_client, notebooklm_wrapper.exceptions.
"""

# pylint: disable=protected-access  # tests exercise _map_error API intentionally

from notebooklm_wrapper._mcp_client import MCPClientManager
from notebooklm_wrapper.exceptions import (
    AuthenticationError,
    GenerationError,
    NotebookLMError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def _map_and_assert(
    message: str,
    tool_name: str,
    expected_class: type,
) -> None:
    """Call _map_error and assert exception type and message content."""
    manager = MCPClientManager()
    err = manager._map_error(message, tool_name)
    assert isinstance(err, expected_class)
    assert f"[{tool_name}]" in str(err)
    if message:
        assert message in str(err)


def test_map_error_includes_tool_name() -> None:
    """Test that _map_error includes tool name in exception message."""
    manager = MCPClientManager()
    err = manager._map_error("Something went wrong", "notebook_list")
    assert isinstance(err, NotebookLMError)
    assert "[notebook_list]" in str(err)
    assert "Something went wrong" in str(err)


def test_map_error_auth() -> None:
    """Test auth error mapping."""
    _map_and_assert("Please login first", "source_add", AuthenticationError)


def test_map_error_not_found() -> None:
    """Test not found error mapping."""
    _map_and_assert("Notebook not found", "notebook_get", NotFoundError)


def test_map_error_rate_limit() -> None:
    """Test rate limit error mapping."""
    _map_and_assert("Rate limit exceeded", "chat_ask", RateLimitError)


def test_map_error_validation() -> None:
    """Test validation error mapping."""
    _map_and_assert("Invalid input", "notebook_create", ValidationError)


def test_map_error_generation() -> None:
    """Test generation error mapping."""
    _map_and_assert("Artifact generation failed", "studio_create", GenerationError)


def test_map_error_empty_message() -> None:
    """Test mapping with empty message uses tool name."""
    manager = MCPClientManager()
    err = manager._map_error("", "unknown_tool")
    assert "[unknown_tool]" in str(err)
    assert "Unknown error" in str(err)
