"""Pytest fixtures for NotebookLM wrapper tests.

Dependencies: pytest, mcp (mcp.types), unittest.mock.
"""

import json
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import CallToolResult, TextContent

from notebooklm_wrapper.async_client import AsyncNotebookLMClient


def make_tool_result(data: dict[str, Any], is_error: bool = False) -> CallToolResult:
    """Create a CallToolResult from dict data.

    :param data: JSON-serializable payload for the tool result.
    :param is_error: Whether the result represents an error.
    :return: A CallToolResult with text content.
    """
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(data))],
        structured_content=None,
        is_error=is_error,
    )


@pytest.fixture
def mock_mcp_call_tool() -> Generator[AsyncMock, None, None]:
    """Mock MCPClientManager.call_tool for testing."""
    with patch("notebooklm_wrapper.resources.notebook.MCPClientManager") as mock_manager_class:
        mock_manager = MagicMock()
        mock_manager.call_tool = AsyncMock()
        mock_manager_class.return_value = mock_manager
        yield mock_manager.call_tool


@pytest.fixture
def mock_mcp_manager() -> Generator[MagicMock, None, None]:
    """Create a mock MCPClientManager."""
    with patch("notebooklm_wrapper._mcp_client.MCPClientManager") as mock_class:
        mock_manager = MagicMock()
        mock_manager.call_tool = AsyncMock()
        mock_class.return_value = mock_manager
        yield mock_manager


@pytest.fixture
def async_client_with_mock_mcp() -> Generator[tuple[AsyncNotebookLMClient, MagicMock], None, None]:
    """Provide AsyncNotebookLMClient with patched MCPClientManager for resource tests."""
    with patch("notebooklm_wrapper.async_client.MCPClientManager") as mock_class:
        mock_instance = MagicMock()
        mock_instance.call_tool = AsyncMock()
        mock_instance.profile = None
        mock_class.return_value = mock_instance
        client = AsyncNotebookLMClient()
        yield client, mock_instance


@pytest.fixture
def sample_notebook_list() -> dict[str, Any]:
    """Sample notebook list response."""
    return {
        "notebooks": [
            {
                "id": "nb-123",
                "title": "Test Notebook",
                "source_count": 2,
                "url": "https://notebooklm.google.com/notebook/nb-123",
                "created_at": "2026-02-18T10:00:00Z",
            }
        ],
        "count": 1,
    }


@pytest.fixture
def sample_notebook_create() -> dict[str, Any]:
    """Sample notebook create response."""
    return {
        "notebook_id": "nb-new",
        "title": "New Notebook",
        "notebook": {
            "id": "nb-new",
            "title": "New Notebook",
            "url": "https://notebooklm.google.com/notebook/nb-new",
        },
        "message": "Created successfully",
    }


@pytest.fixture
def sample_chat_response() -> dict[str, Any]:
    """Sample chat/query response."""
    return {
        "response": "The main points are...",
        "conversation_id": "conv-123",
        "citations": [
            {
                "source_id": "src-1",
                "source_title": "Document 1",
                "excerpt": "Relevant excerpt...",
            }
        ],
    }
