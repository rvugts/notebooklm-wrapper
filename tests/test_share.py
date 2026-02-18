"""Tests for ShareResource.

Dependencies: pytest, notebooklm_wrapper.
"""

import pytest


@pytest.mark.asyncio
async def test_share_status(async_client_with_mock_mcp: tuple) -> None:
    """Test getting share status."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "notebook_id": "nb-1",
        "is_public": False,
        "access_level": "restricted",
        "collaborator_count": 2,
    }

    status = await client.share.status("nb-1")

    assert status.notebook_id == "nb-1"
    assert status.is_public is False
    assert status.collaborator_count == 2


@pytest.mark.asyncio
async def test_share_set_public(async_client_with_mock_mcp: tuple) -> None:
    """Test setting public link."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"updated": True}

    result = await client.share.set_public("nb-1", is_public=True)

    assert result["updated"] is True
    mock_mcp.call_tool.assert_called_once_with(
        "notebook_share_public",
        {"notebook_id": "nb-1", "is_public": True},
    )


@pytest.mark.asyncio
async def test_share_invite(async_client_with_mock_mcp: tuple) -> None:
    """Test inviting a collaborator."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"invited": "user@example.com"}

    result = await client.share.invite("nb-1", "user@example.com", role="editor")

    assert result["invited"] == "user@example.com"
    mock_mcp.call_tool.assert_called_once_with(
        "notebook_share_invite",
        {
            "notebook_id": "nb-1",
            "email": "user@example.com",
            "role": "editor",
        },
    )
