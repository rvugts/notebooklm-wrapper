"""Resource modules for NotebookLM wrapper."""

from .auth import AuthResource
from .chat import ChatResource
from .download import DownloadResource
from .export import ExportResource
from .note import NoteResource
from .notebook import NotebookResource
from .research import ResearchResource
from .share import ShareResource
from .source import SourceResource
from .studio import StudioResource

__all__ = [
    "AuthResource",
    "ChatResource",
    "DownloadResource",
    "ExportResource",
    "NoteResource",
    "NotebookResource",
    "ResearchResource",
    "ShareResource",
    "SourceResource",
    "StudioResource",
]
