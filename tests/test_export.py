"""Tests for ExportResource.

Dependencies: pytest, notebooklm_wrapper.
"""

import pytest


@pytest.mark.asyncio
async def test_export_to_docs(async_client_with_mock_mcp: tuple) -> None:
    """Test exporting to Google Docs."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"doc_url": "https://docs.google.com/doc/123"}

    result = await client.export.to_docs("nb-1", "art-1", title="My Doc")

    assert result["doc_url"] == "https://docs.google.com/doc/123"
    mock_mcp.call_tool.assert_called_once_with(
        "export_artifact",
        {
            "notebook_id": "nb-1",
            "artifact_id": "art-1",
            "export_type": "docs",
            "title": "My Doc",
        },
    )


@pytest.mark.asyncio
async def test_export_to_sheets(async_client_with_mock_mcp: tuple) -> None:
    """Test exporting to Google Sheets."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"sheet_url": "https://docs.google.com/spreadsheets/456"}

    result = await client.export.to_sheets("nb-1", "art-1")

    assert result["sheet_url"] == "https://docs.google.com/spreadsheets/456"
    mock_mcp.call_tool.assert_called_once_with(
        "export_artifact",
        {
            "notebook_id": "nb-1",
            "artifact_id": "art-1",
            "export_type": "sheets",
            "title": None,
        },
    )
