"""Tests for DownloadResource.

Dependencies: pytest, notebooklm_wrapper.
"""

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_download_artifact(async_client_with_mock_mcp: tuple) -> None:
    """Test downloading an artifact."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"path": "/tmp/report.json", "size": 1024}

    result = await client.download.artifact(
        "nb-1", "report", "/tmp/report.json", output_format="json"
    )

    assert result["path"] == "/tmp/report.json"
    mock_mcp.call_tool.assert_called_once_with(
        "download_artifact",
        {
            "notebook_id": "nb-1",
            "artifact_type": "report",
            "output_path": "/tmp/report.json",
            "artifact_id": None,
            "output_format": "json",
        },
    )


@pytest.mark.asyncio
async def test_download_artifact_with_path_object(
    async_client_with_mock_mcp: tuple,
) -> None:
    """Test download with Path object."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {}

    await client.download.artifact("nb-1", "slide_deck", Path("/tmp/deck.json"))

    call_args = mock_mcp.call_tool.call_args[0][1]
    assert call_args["output_path"] == "/tmp/deck.json"
