"""Tests for exception hierarchy.

Dependencies: notebooklm_wrapper.exceptions.
"""

from notebooklm_wrapper.exceptions import (
    AuthenticationError,
    NotebookLMError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def test_exception_hierarchy() -> None:
    """Test that exceptions inherit from NotebookLMError."""
    assert issubclass(AuthenticationError, NotebookLMError)
    assert issubclass(NotFoundError, NotebookLMError)
    assert issubclass(ValidationError, NotebookLMError)
    assert issubclass(RateLimitError, NotebookLMError)


def test_rate_limit_retry_after() -> None:
    """Test RateLimitError has retry_after attribute."""
    err = RateLimitError("Limited", retry_after=60)
    assert err.retry_after == 60
    assert str(err) == "Limited"
