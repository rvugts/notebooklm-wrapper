"""Tests for NotebookLMClient.

Dependencies: unittest.mock, notebooklm_wrapper.
"""

from unittest.mock import patch

from notebooklm_wrapper import AsyncNotebookLMClient, NotebookLMClient


def test_client_imports() -> None:
    """Test that clients can be imported."""
    assert NotebookLMClient is not None
    assert AsyncNotebookLMClient is not None


def test_async_client_creation() -> None:
    """Test AsyncNotebookLMClient has all resources."""
    with patch("notebooklm_wrapper.async_client.MCPClientManager"):
        client = AsyncNotebookLMClient()
        assert client.notebook is not None
        assert client.source is not None
        assert client.chat is not None
        assert client.research is not None
        assert client.studio is not None
        assert client.share is not None
        assert client.download is not None
        assert client.note is not None
        assert client.auth is not None
        assert client.export is not None


def test_sync_client_creation() -> None:
    """Test NotebookLMClient has all resources."""
    with patch("notebooklm_wrapper.async_client.MCPClientManager"):
        client = NotebookLMClient()
        assert client.notebook is not None
        assert client.source is not None
        assert client.chat is not None
