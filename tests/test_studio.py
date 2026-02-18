"""Tests for StudioResource.

Dependencies: pytest, notebooklm_wrapper.async_client,
notebooklm_wrapper.exceptions.
"""

import pytest

from notebooklm_wrapper.exceptions import ValidationError


@pytest.mark.asyncio
async def test_studio_create_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that create requires confirm=True."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.studio.create("nb-1", "report", confirm=False)


@pytest.mark.asyncio
async def test_studio_create(async_client_with_mock_mcp: tuple) -> None:
    """Test creating a studio artifact."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "artifact_id": "art-1",
        "status": "generating",
    }

    result = await client.studio.create("nb-1", "report", confirm=True)

    assert result["artifact_id"] == "art-1"
    call_args = mock_mcp.call_tool.call_args
    assert call_args[0][0] == "studio_create"
    assert call_args[0][1]["notebook_id"] == "nb-1"
    assert call_args[0][1]["artifact_type"] == "report"
    assert call_args[0][1]["confirm"] is True


@pytest.mark.asyncio
async def test_studio_status(async_client_with_mock_mcp: tuple) -> None:
    """Test checking studio status."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "artifacts": [
            {
                "artifact_id": "art-1",
                "type": "report",
                "status": "completed",
                "title": "My Report",
            }
        ],
        "total": 1,
        "completed": 1,
        "in_progress": 0,
    }

    status = await client.studio.status("nb-1")

    assert status.total == 1
    assert status.completed == 1
    assert len(status.artifacts) == 1
    assert status.artifacts[0].artifact_id == "art-1"
    assert status.artifacts[0].status == "completed"


@pytest.mark.asyncio
async def test_studio_delete_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that delete requires confirm=True."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.studio.delete("nb-1", "art-1", confirm=False)


@pytest.mark.asyncio
async def test_studio_delete(async_client_with_mock_mcp: tuple) -> None:
    """Test deleting a studio artifact."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {}

    await client.studio.delete("nb-1", "art-1", confirm=True)

    mock_mcp.call_tool.assert_called_once_with(
        "studio_delete",
        {"notebook_id": "nb-1", "artifact_id": "art-1", "confirm": True},
    )
