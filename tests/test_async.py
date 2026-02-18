"""Tests for async client (profile and integration-style usage).

Dependencies: pytest, unittest.mock, notebooklm_wrapper.
"""

from unittest.mock import AsyncMock, patch

import pytest

from notebooklm_wrapper import AsyncNotebookLMClient


@pytest.mark.asyncio
async def test_async_notebook_list_integration() -> None:
    """Test async notebook list with mocked MCP and custom profile."""
    with patch("notebooklm_wrapper.async_client.MCPClientManager") as mock_mcp:
        mock_instance = mock_mcp.return_value
        mock_instance.call_tool = AsyncMock(
            return_value={"notebooks": [{"id": "nb-1", "title": "A"}]}
        )
        mock_instance.profile = "test"

        client = AsyncNotebookLMClient(profile="test")
        assert client.profile == "test"

        notebooks = await client.notebook.list(max_results=10)
        assert len(notebooks) == 1
        assert notebooks[0].id == "nb-1"
