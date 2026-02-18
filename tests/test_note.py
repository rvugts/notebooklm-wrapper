"""Tests for NoteResource.

Dependencies: pytest, notebooklm_wrapper.async_client,
notebooklm_wrapper.exceptions.
"""

import pytest

from notebooklm_wrapper.exceptions import ValidationError


@pytest.mark.asyncio
async def test_note_create(async_client_with_mock_mcp: tuple) -> None:
    """Test creating a note."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"note_id": "note-1", "title": "My Note"}

    result = await client.note.create("nb-1", "Note content", title="My Note")

    assert result["note_id"] == "note-1"
    mock_mcp.call_tool.assert_called_once_with(
        "note",
        {
            "notebook_id": "nb-1",
            "action": "create",
            "content": "Note content",
            "title": "My Note",
        },
    )


@pytest.mark.asyncio
async def test_note_list(async_client_with_mock_mcp: tuple) -> None:
    """Test listing notes."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"notes": [{"id": "note-1", "title": "Note 1"}]}

    result = await client.note.list("nb-1")

    assert "notes" in result
    assert len(result["notes"]) == 1


@pytest.mark.asyncio
async def test_note_update(async_client_with_mock_mcp: tuple) -> None:
    """Test updating a note."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"updated": True}

    result = await client.note.update("nb-1", "note-1", content="Updated content")

    assert result["updated"] is True
    call_args = mock_mcp.call_tool.call_args[0][1]
    assert call_args["action"] == "update"
    assert call_args["content"] == "Updated content"


@pytest.mark.asyncio
async def test_note_delete_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that note delete requires confirm=True."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.note.delete("nb-1", "note-1", confirm=False)


@pytest.mark.asyncio
async def test_note_delete(async_client_with_mock_mcp: tuple) -> None:
    """Test deleting a note."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"deleted": True}

    result = await client.note.delete("nb-1", "note-1", confirm=True)

    assert result["deleted"] is True
    mock_mcp.call_tool.assert_called_once_with(
        "note",
        {
            "notebook_id": "nb-1",
            "action": "delete",
            "note_id": "note-1",
            "confirm": True,
        },
    )
