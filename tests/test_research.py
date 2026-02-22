"""Tests for ResearchResource.

Dependencies: pytest, notebooklm_wrapper.
"""

import pytest

from notebooklm_wrapper import NotebookLMTimeoutError


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
async def test_research_status_raises_timeout_only_after_max_wait(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Raises NotebookLMTimeoutError only when elapsed >= max_wait and status still non-terminal."""
    from unittest.mock import patch

    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "task_id": "task-1",
        "notebook_id": "nb-1",
        "status": "in_progress",
        "sources_found": 0,
    }
    # t0=0, remaining uses 0 → 60, then elapsed uses 60 → 60 >= 60 → raise
    with patch("notebooklm_wrapper.resources.research.time") as mock_time:
        mock_time.monotonic.side_effect = [0, 0, 60]
        with pytest.raises(NotebookLMTimeoutError) as exc_info:
            await client.research.status("nb-1", max_wait=60)

    assert "60" in str(exc_info.value)
    assert "in_progress" in str(exc_info.value)


@pytest.mark.asyncio
async def test_research_status_returns_after_terminal_without_timeout(
    async_client_with_mock_mcp: tuple,
) -> None:
    """When MCP returns terminal status (e.g. on second poll), returns without raising."""
    from unittest.mock import AsyncMock, patch

    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.side_effect = [
        {"task_id": "t1", "notebook_id": "nb-1", "status": "in_progress", "sources_found": 0},
        {
            "task_id": "t1",
            "notebook_id": "nb-1",
            "status": "completed",
            "sources_found": 2,
            "report": "Done.",
        },
    ]
    # First poll: elapsed stays low so we don't raise; second poll: completed → return
    with (
        patch("notebooklm_wrapper.resources.research.time") as mock_time,
        patch("notebooklm_wrapper.resources.research.asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_time.monotonic.side_effect = [0, 0, 10, 10]
        task = await client.research.status("nb-1", max_wait=60, poll_interval=1)

    assert task.status == "completed"
    assert task.report == "Done."
    assert mock_mcp.call_tool.call_count == 2


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
