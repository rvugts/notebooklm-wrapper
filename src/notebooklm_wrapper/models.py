"""Pydantic models for NotebookLM wrapper.

Dependencies: datetime, typing, pydantic.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Notebook(BaseModel):
    """A NotebookLM notebook."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Unique notebook ID")
    title: str = Field(..., description="Notebook title")
    source_count: int = Field(default=0, alias="sources_count")
    url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = Field(default=None, alias="modified_at")
    ownership: str | None = None
    is_shared: bool | None = None


class SourceInfo(BaseModel):
    """Minimal source info (id, title)."""

    id: str
    title: str
    type: str | None = None
    stale: bool | None = None
    drive_doc_id: str | None = None


class NotebookDetails(Notebook):
    """Detailed notebook with sources."""

    sources: list[SourceInfo] = Field(default_factory=list)


class NotebookSummary(BaseModel):
    """AI-generated notebook summary."""

    summary: str
    suggested_topics: list[str] = Field(default_factory=list)


class Source(BaseModel):
    """A source document in a notebook."""

    id: str
    title: str
    type: str = "unknown"
    url: HttpUrl | None = None
    is_stale: bool = False
    drive_doc_id: str | None = None


class SourceContent(BaseModel):
    """Raw text content of a source."""

    content: str
    title: str = ""
    source_type: str = ""
    char_count: int = 0


class SourceSummary(BaseModel):
    """AI-generated source summary with keywords."""

    summary: str
    keywords: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    """A citation from a source."""

    source_id: str | None = None
    source_title: str | None = None
    excerpt: str | None = None
    url: HttpUrl | None = None


class ChatResponse(BaseModel):
    """Response from a chat query."""

    model_config = ConfigDict(populate_by_name=True)

    answer: str = Field(default="", validation_alias="response")
    conversation_id: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    sources_used: list[dict[str, Any]] = Field(default_factory=list)


class ResearchTask(BaseModel):
    """Research task status."""

    task_id: str | None = None
    notebook_id: str | None = None
    query: str | None = None
    source: str | None = None
    mode: str | None = None
    status: Literal[
        "pending",
        "running",
        "in_progress",
        "completed",
        "failed",
        "no_research",
        "success",
    ] = "pending"
    sources_found: int = 0
    report: str | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    message: str | None = None


class ResearchImportResult(BaseModel):
    """Result of importing research sources."""

    notebook_id: str
    imported_count: int = 0
    imported_sources: list[Any] = Field(default_factory=list)
    message: str = ""


class ArtifactInfo(BaseModel):
    """Studio artifact info."""

    model_config = ConfigDict(populate_by_name=True)

    artifact_id: str
    type: str
    title: str | None = None
    status: Literal["pending", "generating", "completed", "failed"] = "pending"
    created_at: datetime | None = None
    url: str | None = None


class StudioStatus(BaseModel):
    """Studio status with artifact list."""

    model_config = ConfigDict(populate_by_name=True)

    artifacts: list[ArtifactInfo] = Field(default_factory=list)
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    notebook_url: str | None = None

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> "StudioStatus":
        """Handle MCP response with summary wrapper."""
        if isinstance(obj, dict) and "summary" in obj:
            summary = obj["summary"]
            artifacts = [ArtifactInfo.model_validate(a) for a in obj.get("artifacts", [])]
            return cls(
                artifacts=artifacts,
                total=summary.get("total", 0),
                completed=summary.get("completed", 0),
                in_progress=summary.get("in_progress", 0),
                notebook_url=obj.get("notebook_url"),
            )
        return super().model_validate(obj, *args, **kwargs)


class CollaboratorInfo(BaseModel):
    """Collaborator info."""

    email: str
    role: str
    is_pending: bool = False
    display_name: str | None = None


class ShareStatus(BaseModel):
    """Notebook sharing status."""

    notebook_id: str = ""
    is_public: bool = False
    access_level: str = "restricted"
    public_link: str | None = None
    collaborators: list[CollaboratorInfo] = Field(default_factory=list)
    collaborator_count: int = 0


class Note(BaseModel):
    """A note in a notebook."""

    id: str
    title: str | None = None
    content: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AddSourceResult(BaseModel):
    """Result of adding a source."""

    source_type: str
    source_id: str
    title: str
    ready: bool | None = None


class SyncResult(BaseModel):
    """Result of syncing a Drive source."""

    source_id: str
    synced: bool
    error: str | None = None
