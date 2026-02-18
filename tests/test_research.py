"""Tests for ResearchResource.

Dependencies: pytest, notebooklm_wrapper.
"""

import pytest


@pytest.mark.asyncio
async def test_research_start(async_client_with_mock_mcp: tuple) -> None:
    """Test starting research."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "task_id": "task-1",
        "notebook_id": "nb-1",
        "status": "pending",
        "sources_found": 0,
    }

    task = await client.research.start("What is AI?", source="web", mode="fast")

    assert task.task_id == "task-1"
    assert task.notebook_id == "nb-1"
    assert task.status == "pending"
    call_args = mock_mcp.call_tool.call_args[0][1]
    assert call_args["query"] == "What is AI?"
    assert call_args["source"] == "web"
    assert call_args["mode"] == "fast"


@pytest.mark.asyncio
async def test_research_status(async_client_with_mock_mcp: tuple) -> None:
    """Test polling research status."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "task_id": "task-1",
        "notebook_id": "nb-1",
        "status": "completed",
        "sources_found": 5,
        "report": "Summary...",
    }

    task = await client.research.status("nb-1")

    assert task.status == "completed"
    assert task.sources_found == 5
    assert task.report == "Summary..."


@pytest.mark.asyncio
async def test_research_import_sources(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test importing research sources into notebook."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "notebook_id": "nb-1",
        "imported_count": 3,
        "message": "Imported 3 sources",
    }

    result = await client.research.import_sources("nb-1", "task-1")

    assert result.notebook_id == "nb-1"
    assert result.imported_count == 3
    call_args = mock_mcp.call_tool.call_args[0]
    assert call_args[0] == "research_import"
    assert call_args[1]["notebook_id"] == "nb-1"
    assert call_args[1]["task_id"] == "task-1"
