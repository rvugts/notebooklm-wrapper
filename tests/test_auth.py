"""Tests for AuthResource.

Dependencies: pytest, unittest.mock, notebooklm_wrapper.
"""

import pytest


@pytest.mark.asyncio
async def test_auth_refresh(async_client_with_mock_mcp: tuple) -> None:
    """Test refreshing auth tokens."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"status": "ok"}

    result = await client.auth.refresh()

    assert result["status"] == "ok"
    mock_mcp.call_tool.assert_called_once_with("refresh_auth", {})


@pytest.mark.asyncio
async def test_auth_save_tokens(async_client_with_mock_mcp: tuple) -> None:
    """Test saving auth tokens."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"saved": True}

    result = await client.auth.save_tokens("cookie=value")

    assert result["saved"] is True
    call_args = mock_mcp.call_tool.call_args[0][1]
    assert call_args["cookies"] == "cookie=value"
