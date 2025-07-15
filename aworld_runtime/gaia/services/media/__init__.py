"""GAIA MCP Servers API package for media services."""

from .audio_collection import AudioCollection, AudioMetadata
from .image_collection import ImageCollection, ImageMetadata
from .video_collection import (
    KeyframeResult,
    VideoAnalysisResult,
    VideoCollection,
    VideoMetadata,
    VideoSummaryResult,
)

__all__ = [
    "AudioCollection",
    "AudioMetadata",
    "ImageCollection",
    "ImageMetadata",
    "VideoCollection",
    "VideoMetadata",
    "VideoAnalysisResult",
    "VideoSummaryResult",
    "KeyframeResult",
]
