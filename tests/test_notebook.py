"""Tests for NotebookResource.

Dependencies: pytest, notebooklm_wrapper.async_client,
notebooklm_wrapper.exceptions.
"""

import pytest

from notebooklm_wrapper.exceptions import ValidationError


@pytest.mark.asyncio
async def test_notebook_list(async_client_with_mock_mcp: tuple) -> None:
    """Test listing notebooks."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "notebooks": [{"id": "nb-123", "title": "Test", "source_count": 2}]
    }

    notebooks = await client.notebook.list()

    assert len(notebooks) == 1
    assert notebooks[0].id == "nb-123"
    assert notebooks[0].title == "Test"


@pytest.mark.asyncio
async def test_notebook_create(async_client_with_mock_mcp: tuple) -> None:
    """Test creating a notebook."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "notebook": {"id": "nb-new", "title": "New", "url": "https://x.com"}
    }

    notebook = await client.notebook.create(title="New")

    assert notebook.id == "nb-new"
    assert notebook.title == "New"


@pytest.mark.asyncio
async def test_notebook_get(async_client_with_mock_mcp: tuple) -> None:
    """Test getting notebook details."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "notebook": {"id": "nb-1", "title": "Test", "source_count": 2},
        "sources": [{"id": "src-1", "title": "Doc 1"}],
    }

    details = await client.notebook.get("nb-1")

    assert details.id == "nb-1"
    assert details.title == "Test"
    assert len(details.sources) == 1
    assert details.sources[0].id == "src-1"


@pytest.mark.asyncio
async def test_notebook_describe(async_client_with_mock_mcp: tuple) -> None:
    """Test getting notebook summary."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "summary": "This notebook covers AI topics.",
        "suggested_topics": ["Machine Learning", "Neural Networks"],
    }

    summary = await client.notebook.describe("nb-1")

    assert "AI topics" in summary.summary
    assert "Machine Learning" in summary.suggested_topics


@pytest.mark.asyncio
async def test_notebook_rename(async_client_with_mock_mcp: tuple) -> None:
    """Test renaming a notebook."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"notebook": {"id": "nb-1", "title": "New Title"}}

    notebook = await client.notebook.rename("nb-1", "New Title")

    assert notebook.id == "nb-1"
    assert notebook.title == "New Title"


@pytest.mark.asyncio
async def test_notebook_rename_empty_title_raises(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that empty title raises ValidationError."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="cannot be empty"):
        await client.notebook.rename("nb-1", "")


@pytest.mark.asyncio
async def test_notebook_delete_requires_confirm(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test that delete requires confirm=True."""
    client, _ = async_client_with_mock_mcp

    with pytest.raises(ValidationError, match="confirm=True"):
        await client.notebook.delete("nb-123", confirm=False)
