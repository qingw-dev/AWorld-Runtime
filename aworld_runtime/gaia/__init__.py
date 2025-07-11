"""GAIA is a collection of services for building and managing AI agents.

This package exposes the main collection classes from each service module, making them easily accessible.
"""

from .models import DocumentMetadata
from .services import (
    ActionArguments,
    ArxivCollection,
    AudioCollection,
    BrowserCollection,
    CodeCollection,
    CSVCollection,
    DOCXExtractionCollection,
    DownloadCollection,
    ImageCollection,
    PDFDocumentCollection,
    PPTXCollection,
    PubChemCollection,
    SearchCollection,
    TerminalCollection,
    TextCollection,
    ThinkCollection,
    VideoCollection,
    WaybackCollection,
    WikipediaCollection,
    XLSXCollection,
    YouTubeCollection,
)
from .services.sse_server import sse_cli

__all__ = [
    "sse_cli",
    "ActionArguments",
    "DocumentMetadata",
    "CSVCollection",
    "DOCXExtractionCollection",
    "PDFDocumentCollection",
    "PPTXCollection",
    "TextCollection",
    "XLSXCollection",
    "CodeCollection",
    "ThinkCollection",
    "AudioCollection",
    "ImageCollection",
    "VideoCollection",
    "ArxivCollection",
    "BrowserCollection",
    "DownloadCollection",
    "PubChemCollection",
    "SearchCollection",
    "TerminalCollection",
    "WaybackCollection",
    "WikipediaCollection",
    "YouTubeCollection",
]
