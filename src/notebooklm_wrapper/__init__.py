"""NotebookLM Python wrapper - Pythonic interface via MCP protocol."""

from .async_client import AsyncNotebookLMClient
from .client import NotebookLMClient
from .exceptions import (
    AuthenticationError,
    ExportError,
    GenerationError,
    NotebookLMError,
    NotebookLMTimeoutError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import (
    AddSourceResult,
    ArtifactInfo,
    ChatResponse,
    Citation,
    CollaboratorInfo,
    Note,
    Notebook,
    NotebookDetails,
    NotebookSummary,
    ResearchImportResult,
    ResearchTask,
    ShareStatus,
    Source,
    SourceContent,
    SourceInfo,
    SourceSummary,
    StudioStatus,
    SyncResult,
)

__all__ = [
    "AddSourceResult",
    "ArtifactInfo",
    "AsyncNotebookLMClient",
    "AuthenticationError",
    "ChatResponse",
    "Citation",
    "CollaboratorInfo",
    "ExportError",
    "GenerationError",
    "NotFoundError",
    "Note",
    "Notebook",
    "NotebookDetails",
    "NotebookLMClient",
    "NotebookLMError",
    "NotebookLMTimeoutError",
    "NotebookSummary",
    "RateLimitError",
    "ResearchImportResult",
    "ResearchTask",
    "ShareStatus",
    "Source",
    "SourceContent",
    "SourceInfo",
    "SourceSummary",
    "StudioStatus",
    "SyncResult",
    "ValidationError",
]

__version__ = "0.1.4"
