"""Enums and constants for NotebookLM wrapper.

Dependencies: enum (standard library).
"""

from enum import StrEnum


class SourceType(StrEnum):
    """Source types supported by NotebookLM."""

    URL = "url"
    TEXT = "text"
    DRIVE = "drive"
    FILE = "file"
    YOUTUBE = "youtube"


class ArtifactType(StrEnum):
    """Studio artifact types."""

    AUDIO = "audio"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    SLIDE_DECK = "slide_deck"
    REPORT = "report"
    FLASHCARDS = "flashcards"
    QUIZ = "quiz"
    DATA_TABLE = "data_table"
    MIND_MAP = "mind_map"


class AudioFormat(StrEnum):
    """Audio overview formats."""

    DEEP_DIVE = "deep_dive"
    BRIEF = "brief"
    CRITIQUE = "critique"
    DEBATE = "debate"


class AudioLength(StrEnum):
    """Audio overview lengths."""

    SHORT = "short"
    DEFAULT = "default"
    LONG = "long"


class VideoFormat(StrEnum):
    """Video overview formats."""

    EXPLAINER = "explainer"
    BRIEF = "brief"


class VideoStyle(StrEnum):
    """Video visual styles."""

    AUTO_SELECT = "auto_select"
    CLASSIC = "classic"
    WHITEBOARD = "whiteboard"
    KAWAII = "kawaii"
    ANIME = "anime"
    WATERCOLOR = "watercolor"
    RETRO_PRINT = "retro_print"
    HERITAGE = "heritage"
    PAPER_CRAFT = "paper_craft"


class InfographicOrientation(StrEnum):
    """Infographic orientations."""

    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class InfographicDetailLevel(StrEnum):
    """Infographic detail levels."""

    CONCISE = "concise"
    STANDARD = "standard"
    DETAILED = "detailed"


class SlideDeckFormat(StrEnum):
    """Slide deck formats."""

    DETAILED_DECK = "detailed_deck"
    PRESENTER_SLIDES = "presenter_slides"


class SlideDeckLength(StrEnum):
    """Slide deck lengths."""

    SHORT = "short"
    DEFAULT = "default"


class ReportFormat(StrEnum):
    """Report formats."""

    BRIEFING_DOC = "Briefing Doc"
    STUDY_GUIDE = "Study Guide"
    BLOG_POST = "Blog Post"
    CREATE_YOUR_OWN = "Create Your Own"


class Difficulty(StrEnum):
    """Flashcard/quiz difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ResearchSource(StrEnum):
    """Research search sources."""

    WEB = "web"
    DRIVE = "drive"


class ResearchMode(StrEnum):
    """Research modes."""

    FAST = "fast"
    DEEP = "deep"


class ShareRole(StrEnum):
    """Collaborator roles."""

    VIEWER = "viewer"
    EDITOR = "editor"


class ChatGoal(StrEnum):
    """Chat configuration goals."""

    DEFAULT = "default"
    LEARNING_GUIDE = "learning_guide"
    CUSTOM = "custom"


class ResponseLength(StrEnum):
    """Chat response length."""

    DEFAULT = "default"
    LONGER = "longer"
    SHORTER = "shorter"


class ExportType(StrEnum):
    """Export destination types."""

    DOCS = "docs"
    SHEETS = "sheets"


class NoteAction(StrEnum):
    """Note operations."""

    CREATE = "create"
    LIST = "list"
    UPDATE = "update"
    DELETE = "delete"
