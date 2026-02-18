"""Tests for ChatResource.

Dependencies: pytest, notebooklm_wrapper.
"""

import pytest


@pytest.mark.asyncio
async def test_chat_ask(async_client_with_mock_mcp: tuple) -> None:
    """Test asking a question."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {
        "response": "The answer is 42",
        "conversation_id": "conv-1",
        "citations": [],
    }

    response = await client.chat.ask("nb-123", "What is the answer?")

    assert response.answer == "The answer is 42"
    assert response.conversation_id == "conv-1"


@pytest.mark.asyncio
async def test_chat_configure(async_client_with_mock_mcp: tuple) -> None:
    """Test configuring chat settings."""
    client, mock_mcp = async_client_with_mock_mcp
    mock_mcp.call_tool.return_value = {"configured": True}

    result = await client.chat.configure(
        "nb-1",
        goal="learning_guide",
        response_length="longer",
    )

    assert result["configured"] is True
    mock_mcp.call_tool.assert_called_once_with(
        "chat_configure",
        {
            "notebook_id": "nb-1",
            "goal": "learning_guide",
            "custom_prompt": None,
            "response_length": "longer",
        },
    )
