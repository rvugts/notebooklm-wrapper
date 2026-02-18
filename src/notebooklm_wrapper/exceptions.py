"""Exception hierarchy for NotebookLM wrapper.

No external dependencies beyond the standard library.
"""


class NotebookLMError(Exception):
    """Base exception for all NotebookLM operations."""


class AuthenticationError(NotebookLMError):
    """Authentication failed or credentials expired."""


class NotFoundError(NotebookLMError):
    """Resource not found (notebook, source, etc.)."""


class ValidationError(NotebookLMError):
    """Invalid parameters or data."""


class RateLimitError(NotebookLMError):
    """API rate limit exceeded."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class GenerationError(NotebookLMError):
    """Content generation failed (Studio artifacts)."""


class NotebookLMTimeoutError(NotebookLMError):
    """Operation timed out."""


class ExportError(NotebookLMError):
    """Export operation failed."""
