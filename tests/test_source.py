"""Tests for SourceResource.

Dependencies: pytest, notebooklm_wrapper.async_client,
notebooklm_wrapper.exceptions.
"""

import pytest

from notebooklm_wrapper.exceptions import ValidationError


@pytest.mark.asyncio
async def test_source_add(async_client_with_mock_mcp: tuple) -> None:
    """Test adding a source."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "source_type": "url",
        "source_id": "src-123",
        "title": "Article",
    }

    result = await client.source.add(
        "nb-123",
        "url",
        url="https://example.com",
    )

    assert result.source_id == "src-123"
    assert result.source_type == "url"


@pytest.mark.asyncio
async def test_source_list_drive(async_client_with_mock_mcp: tuple) -> None:
    """Test listing Drive sources."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "drive_sources": [{"id": "src-1", "title": "Doc 1", "drive_doc_id": "abc"}]
    }

    result = await client.source.list_drive("nb-1")

    assert "drive_sources" in result
    assert len(result["drive_sources"]) == 1
    assert result["drive_sources"][0]["id"] == "src-1"


@pytest.mark.asyncio
async def test_source_describe(async_client_with_mock_mcp: tuple) -> None:
    """Test describing a source (AI summary)."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "summary": "This document covers machine learning.",
        "keywords": ["AI", "ML", "neural networks"],
    }

    summary = await client.source.describe("src-1")

    assert "machine learning" in summary.summary
    assert "AI" in summary.keywords


@pytest.mark.asyncio
async def test_source_sync_drive(async_client_with_mock_mcp: tuple) -> None:
    """Test syncing Drive sources."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "results": [{"source_id": "src-1", "synced": True, "error": None}]
    }

    results = await client.source.sync_drive(["src-1"], confirm=True)

    assert len(results) == 1
    assert results[0].source_id == "src-1"
    assert results[0].synced is True


@pytest.mark.asyncio
async def test_source_sync_drive_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that sync requires confirm=True."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.source.sync_drive(["src-1"], confirm=False)


@pytest.mark.asyncio
async def test_source_get_content(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test getting source content."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "content": "Full text of the document...",
        "title": "Article",
        "char_count": 100,
    }

    content = await client.source.get_content("src-1")

    assert content.content == "Full text of the document..."
    assert content.title == "Article"


@pytest.mark.asyncio
async def test_source_delete(async_client_with_mock_mcp: tuple) -> None:
    """Test deleting a source."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {}

    await client.source.delete("src-1", confirm=True)

    mock_mcp.call_tool.assert_called_once_with(
        "source_delete",
        {"source_id": "src-1", "confirm": True},
    )


@pytest.mark.asyncio
async def test_source_delete_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that source delete requires confirm."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.source.delete("src-123", confirm=False)
