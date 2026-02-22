"""Tests for MCP client error mapping, tool name in exceptions, and config_dir.

Dependencies: notebooklm_wrapper._mcp_client, notebooklm_wrapper.exceptions.
"""

# pylint: disable=protected-access  # tests exercise _map_error API intentionally

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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


def test_map_error_no_confirmation_adds_deep_research_hint() -> None:
    """No-confirmation research error message gets Deep Research limit hint."""
    manager = MCPClientManager()
    msg = "Failed to start research — no confirmation from API."
    err = manager._map_error(msg, "research_start")
    assert isinstance(err, NotebookLMError)
    assert "[research_start]" in str(err)
    assert "no confirmation from API" in str(err)
    assert "Deep Research limit" in str(err)
    assert "try again later or upgrade" in str(err)


def test_mcp_manager_config_dir_attribute() -> None:
    """Test that MCPClientManager stores config_dir."""
    manager = MCPClientManager(profile="u1", config_dir="/data/u1")
    assert manager.profile == "u1"
    assert manager.config_dir == "/data/u1"


@pytest.mark.asyncio
async def test_connect_passes_home_env_when_config_dir_set() -> None:
    """Test that connect() passes HOME=config_dir in env when config_dir is set."""
    captured_params = []

    def fake_stdio_client(params):
        captured_params.append(params)
        read = MagicMock()
        write = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=(read, write))
        ctx.__aexit__ = AsyncMock(return_value=None)
        return ctx

    with (
        patch("notebooklm_wrapper._mcp_client.stdio_client", side_effect=fake_stdio_client),
        patch("notebooklm_wrapper._mcp_client.ClientSession") as mock_session,
    ):
        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.return_value.initialize = AsyncMock()

        manager = MCPClientManager(config_dir="/app/users/abc")
        await manager.connect()

    assert len(captured_params) == 1
    params = captured_params[0]
    assert params.env is not None
    assert params.env.get("HOME") == "/app/users/abc"
