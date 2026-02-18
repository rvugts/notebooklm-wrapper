"""Tests for Pydantic models.

Dependencies: notebooklm_wrapper (ChatResponse, Notebook, NotebookSummary,
SourceInfo, StudioStatus).
"""

from notebooklm_wrapper import ChatResponse, Notebook, NotebookSummary, SourceInfo, StudioStatus


def test_notebook_model() -> None:
    """Test Notebook model validation."""
    nb = Notebook.model_validate(
        {
            "id": "nb-123",
            "title": "Test",
            "source_count": 2,
        }
    )
    assert nb.id == "nb-123"
    assert nb.title == "Test"
    assert nb.source_count == 2


def test_chat_response_model() -> None:
    """Test ChatResponse with response/answer alias."""
    resp = ChatResponse.model_validate(
        {
            "response": "Hello",
            "conversation_id": "conv-1",
        }
    )
    assert resp.answer == "Hello"
    assert resp.conversation_id == "conv-1"


def test_notebook_summary_model() -> None:
    """Test NotebookSummary model."""
    summary = NotebookSummary.model_validate(
        {
            "summary": "A summary",
            "suggested_topics": ["topic1", "topic2"],
        }
    )
    assert summary.summary == "A summary"
    assert summary.suggested_topics == ["topic1", "topic2"]


def test_source_info_model() -> None:
    """Test SourceInfo model."""
    info = SourceInfo.model_validate({"id": "src-1", "title": "Doc 1"})
    assert info.id == "src-1"
    assert info.title == "Doc 1"


def test_studio_status_with_summary() -> None:
    """Test StudioStatus handles summary wrapper."""
    status = StudioStatus.model_validate(
        {
            "summary": {"total": 3, "completed": 2, "in_progress": 1},
            "artifacts": [
                {"artifact_id": "art-1", "type": "audio", "status": "completed"},
            ],
            "notebook_url": "https://x.com",
        }
    )
    assert status.total == 3
    assert status.completed == 2
    assert status.in_progress == 1
    assert len(status.artifacts) == 1
    assert status.artifacts[0].artifact_id == "art-1"
