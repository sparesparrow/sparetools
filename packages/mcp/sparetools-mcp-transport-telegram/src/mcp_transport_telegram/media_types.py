"""Type definitions and utilities for Telegram media handling."""

import mimetypes
from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    """Enumeration of supported media types."""
    PHOTO = "photo"
    DOCUMENT = "document"
    AUDIO = "audio"
    VOICE = "voice"
    VIDEO = "video"
    STICKER = "sticker"
    ANIMATION = "animation"
    UNKNOWN = "unknown"


@dataclass
class MediaInfo:
    """Information about a media file."""
    media_type: MediaType
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None  # seconds for audio/video
    file_path: Optional[Path] = None


@dataclass
class MediaUploadResult:
    """Result of a media upload operation."""
    success: bool
    media_info: Optional[MediaInfo]
    error_message: Optional[str]
    telegram_file_id: Optional[str]


@dataclass
class MediaDownloadResult:
    """Result of a media download operation."""
    success: bool
    local_path: Optional[Path]
    media_info: Optional[MediaInfo]
    error_message: Optional[str]


class MediaTypeDetector:
    """Utility for detecting media types and MIME types."""

    # File extensions to media types mapping
    EXTENSION_MAPPING: Dict[str, MediaType] = {
        # Images
        '.jpg': MediaType.PHOTO,
        '.jpeg': MediaType.PHOTO,
        '.png': MediaType.PHOTO,
        '.gif': MediaType.ANIMATION,
        '.webp': MediaType.PHOTO,
        '.bmp': MediaType.PHOTO,

        # Documents
        '.pdf': MediaType.DOCUMENT,
        '.doc': MediaType.DOCUMENT,
        '.docx': MediaType.DOCUMENT,
        '.txt': MediaType.DOCUMENT,
        '.rtf': MediaType.DOCUMENT,
        '.xls': MediaType.DOCUMENT,
        '.xlsx': MediaType.DOCUMENT,
        '.ppt': MediaType.DOCUMENT,
        '.pptx': MediaType.DOCUMENT,
        '.zip': MediaType.DOCUMENT,
        '.rar': MediaType.DOCUMENT,
        '.7z': MediaType.DOCUMENT,

        # Audio
        '.mp3': MediaType.AUDIO,
        '.wav': MediaType.AUDIO,
        '.flac': MediaType.AUDIO,
        '.aac': MediaType.AUDIO,
        '.ogg': MediaType.AUDIO,
        '.m4a': MediaType.AUDIO,

        # Video
        '.mp4': MediaType.VIDEO,
        '.avi': MediaType.VIDEO,
        '.mkv': MediaType.VIDEO,
        '.mov': MediaType.VIDEO,
        '.wmv': MediaType.VIDEO,
        '.flv': MediaType.VIDEO,
        '.webm': MediaType.VIDEO,
    }

    # MIME type to media type mapping
    MIME_MAPPING: Dict[str, MediaType] = {
        # Images
        'image/jpeg': MediaType.PHOTO,
        'image/png': MediaType.PHOTO,
        'image/gif': MediaType.ANIMATION,
        'image/webp': MediaType.PHOTO,
        'image/bmp': MediaType.PHOTO,

        # Audio
        'audio/mpeg': MediaType.AUDIO,
        'audio/wav': MediaType.AUDIO,
        'audio/flac': MediaType.AUDIO,
        'audio/aac': MediaType.AUDIO,
        'audio/ogg': MediaType.AUDIO,
        'audio/mp4': MediaType.AUDIO,

        # Video
        'video/mp4': MediaType.VIDEO,
        'video/avi': MediaType.VIDEO,
        'video/x-matroska': MediaType.VIDEO,
        'video/quicktime': MediaType.VIDEO,
        'video/webm': MediaType.VIDEO,

        # Documents
        'application/pdf': MediaType.DOCUMENT,
        'application/msword': MediaType.DOCUMENT,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': MediaType.DOCUMENT,
        'text/plain': MediaType.DOCUMENT,
        'application/rtf': MediaType.DOCUMENT,
        'application/vnd.ms-excel': MediaType.DOCUMENT,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': MediaType.DOCUMENT,
        'application/vnd.ms-powerpoint': MediaType.DOCUMENT,
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': MediaType.DOCUMENT,
        'application/zip': MediaType.DOCUMENT,
        'application/x-rar-compressed': MediaType.DOCUMENT,
        'application/x-7z-compressed': MediaType.DOCUMENT,
    }

    @classmethod
    def detect_from_extension(cls, file_path: Union[str, Path]) -> MediaType:
        """Detect media type from file extension."""
        path = Path(file_path)
        extension = path.suffix.lower()

        return cls.EXTENSION_MAPPING.get(extension, MediaType.UNKNOWN)

    @classmethod
    def detect_from_mime_type(cls, mime_type: str) -> MediaType:
        """Detect media type from MIME type."""
        if not mime_type:
            return MediaType.UNKNOWN

        # Check for exact match first
        if mime_type in cls.MIME_MAPPING:
            return cls.MIME_MAPPING[mime_type]

        # Check for prefix match (e.g., "image/*" -> PHOTO)
        main_type = mime_type.split('/')[0]
        if main_type == 'image':
            return MediaType.PHOTO
        elif main_type == 'audio':
            return MediaType.AUDIO
        elif main_type == 'video':
            return MediaType.VIDEO

        return MediaType.UNKNOWN

    @classmethod
    def get_mime_type(cls, file_path: Union[str, Path]) -> Optional[str]:
        """Get MIME type for a file."""
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type

    @classmethod
    def is_safe_file_type(cls, file_path: Union[str, Path], allowed_types: Optional[List[MediaType]] = None) -> bool:
        """Check if file type is safe to process."""
        if allowed_types is None:
            # Default safe types
            allowed_types = [MediaType.PHOTO, MediaType.DOCUMENT, MediaType.AUDIO]

        media_type = cls.detect_from_extension(file_path)
        return media_type in allowed_types

    @classmethod
    def get_safe_filename(cls, filename: str, max_length: int = 255) -> str:
        """Generate a safe filename."""
        import re

        # Remove or replace dangerous characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Limit length
        if len(safe_name) > max_length:
            name_part, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
            max_name_length = max_length - len(ext) - 1 if ext else max_length
            safe_name = f"{name_part[:max_name_length]}.{ext}" if ext else name_part[:max_length]

        return safe_name