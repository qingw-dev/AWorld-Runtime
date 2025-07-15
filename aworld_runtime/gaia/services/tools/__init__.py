"""GAIA MCP Servers API package."""

from .arxiv_collection import ArxivCollection, ArxivMetadata, PaperResult
from .browser_collection import BrowserCollection, BrowserMetadata
from .download_collection import DownloadCollection, DownloadMetadata, DownloadResult
from .pubchem_collection import PubChemCollection, PubChemMetadata
from .search_collection import SearchCollection, SearchMetadata, SearchResult
from .terminal_collection import TerminalCollection, TerminalMetadata
from .wayback_collection import WaybackCollection, WaybackMetadata
from .wikipedia_collection import WikipediaArticle, WikipediaCollection, WikipediaMetadata, WikipediaSearchResult
from .youtube_collection import TranscriptResult, YouTubeCollection, YoutubeDownloadResults, YouTubeMetadata

__all__ = [
    "ArxivCollection",
    "ArxivMetadata",
    "PaperResult",
    "BrowserCollection",
    "BrowserMetadata",
    "DownloadCollection",
    "DownloadMetadata",
    "DownloadResult",
    "PubChemCollection",
    "PubChemMetadata",
    "SearchCollection",
    "SearchMetadata",
    "SearchResult",
    "TerminalCollection",
    "TerminalMetadata",
    "WaybackMetadata",
    "WaybackCollection",
    "WikipediaArticle",
    "WikipediaMetadata",
    "WikipediaCollection",
    "WikipediaSearchResult",
    "YouTubeCollection",
    "YouTubeMetadata",
    "TranscriptResult",
    "YoutubeDownloadResults",
]
