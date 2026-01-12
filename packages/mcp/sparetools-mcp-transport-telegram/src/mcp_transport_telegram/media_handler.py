"""Media download/upload utilities for Telegram MCP transport."""

import asyncio
import logging
import tempfile
from typing import Optional, Union, List
from pathlib import Path
import aiofiles
import os

from telethon.tl.types import (
    Message, MessageMediaDocument, MessageMediaPhoto,
    MessageMediaAudio, MessageMediaVoice
)

from .telegram_client import TelegramClientWrapper, TelegramAPIError
from .media_types import (
    MediaType, MediaInfo, MediaDownloadResult,
    MediaUploadResult, MediaTypeDetector
)


logger = logging.getLogger(__name__)


class MediaHandler:
    """Handles media download and upload operations for Telegram."""

    def __init__(
        self,
        telegram_client: TelegramClientWrapper,
        temp_dir: Optional[Union[str, Path]] = None,
        max_file_size: int = 50 * 1024 * 1024,  # 50MB default
        allowed_types: Optional[List[MediaType]] = None
    ):
        """Initialize media handler.

        Args:
            telegram_client: Telegram client wrapper
            temp_dir: Directory for temporary files
            max_file_size: Maximum allowed file size in bytes
            allowed_types: List of allowed media types
        """
        self.telegram_client = telegram_client
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "mcp_telegram_media"
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or [MediaType.PHOTO, MediaType.DOCUMENT, MediaType.AUDIO, MediaType.VIDEO]

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def download_media(
        self,
        message: Message,
        custom_path: Optional[Union[str, Path]] = None
    ) -> MediaDownloadResult:
        """Download media from a Telegram message.

        Args:
            message: Telegram message containing media
            custom_path: Custom path to save the file

        Returns:
            MediaDownloadResult with download status and file info
        """
        try:
            if not message.media:
                return MediaDownloadResult(
                    success=False,
                    local_path=None,
                    media_info=None,
                    error_message="Message contains no media"
                )

            # Check file size
            file_size = self._get_media_size(message.media)
            if file_size and file_size > self.max_file_size:
                return MediaDownloadResult(
                    success=False,
                    local_path=None,
                    media_info=None,
                    error_message=f"File size {file_size} exceeds maximum allowed size {self.max_file_size}"
                )

            # Determine file path
            if custom_path:
                file_path = Path(custom_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                file_path = self._generate_temp_path(message.media)

            # Download the media
            downloaded_path = await self.telegram_client.download_media(message, file_path)

            if downloaded_path:
                # Get media info
                media_info = self._extract_media_info(message.media, Path(downloaded_path))

                # Verify file type safety
                if not self._is_allowed_type(media_info.media_type):
                    # Clean up downloaded file
                    try:
                        Path(downloaded_path).unlink()
                    except:
                        pass

                    return MediaDownloadResult(
                        success=False,
                        local_path=None,
                        media_info=media_info,
                        error_message=f"Media type {media_info.media_type.value} not allowed"
                    )

                logger.info(f"Successfully downloaded media to {downloaded_path}")
                return MediaDownloadResult(
                    success=True,
                    local_path=Path(downloaded_path),
                    media_info=media_info,
                    error_message=None
                )
            else:
                return MediaDownloadResult(
                    success=False,
                    local_path=None,
                    media_info=None,
                    error_message="Download failed"
                )

        except TelegramAPIError as e:
            logger.error(f"Telegram API error downloading media: {e}")
            return MediaDownloadResult(
                success=False,
                local_path=None,
                media_info=None,
                error_message=f"API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error downloading media: {e}")
            return MediaDownloadResult(
                success=False,
                local_path=None,
                media_info=None,
                error_message=f"Unexpected error: {e}"
            )

    async def upload_media(
        self,
        file_path: Union[str, Path],
        chat_id: Union[int, str],
        caption: Optional[str] = None
    ) -> MediaUploadResult:
        """Upload media to a Telegram chat.

        Args:
            file_path: Path to the file to upload
            chat_id: Chat ID to upload to
            caption: Optional caption for the media

        Returns:
            MediaUploadResult with upload status
        """
        file_path = Path(file_path)

        try:
            # Check if file exists
            if not file_path.exists():
                return MediaUploadResult(
                    success=False,
                    media_info=None,
                    error_message=f"File not found: {file_path}",
                    telegram_file_id=None
                )

            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return MediaUploadResult(
                    success=False,
                    media_info=None,
                    error_message=f"File size {file_size} exceeds maximum allowed size {self.max_file_size}",
                    telegram_file_id=None
                )

            # Detect media type
            media_type = MediaTypeDetector.detect_from_extension(file_path)
            if not self._is_allowed_type(media_type):
                return MediaUploadResult(
                    success=False,
                    media_info=None,
                    error_message=f"Media type {media_type.value} not allowed for upload",
                    telegram_file_id=None
                )

            # For now, we'll use send_message with file path
            # In a full implementation, you'd want to use specific send_* methods
            # based on media type (send_photo, send_document, etc.)

            # This is a simplified implementation
            # Real implementation would need to determine the appropriate send method
            logger.warning("Media upload not fully implemented - would need specific send_* methods")

            return MediaUploadResult(
                success=False,
                media_info=None,
                error_message="Upload not yet implemented",
                telegram_file_id=None
            )

        except Exception as e:
            logger.error(f"Error uploading media {file_path}: {e}")
            return MediaUploadResult(
                success=False,
                media_info=None,
                error_message=f"Upload error: {e}",
                telegram_file_id=None
            )

    def _generate_temp_path(self, media) -> Path:
        """Generate a temporary file path for media download."""
        suffix = self._get_media_suffix(media)
        temp_file = tempfile.NamedTemporaryFile(
            dir=self.temp_dir,
            delete=False,
            suffix=suffix
        )
        temp_file.close()
        return Path(temp_file.name)

    def _get_media_suffix(self, media) -> str:
        """Get appropriate file suffix based on media type."""
        if isinstance(media, MessageMediaDocument):
            # Try to get extension from document attributes
            if hasattr(media.document, 'attributes'):
                for attr in media.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        return Path(attr.file_name).suffix or '.bin'
            return '.bin'
        elif isinstance(media, MessageMediaPhoto):
            return '.jpg'
        elif isinstance(media, MessageMediaAudio) or isinstance(media, MessageMediaVoice):
            return '.ogg'
        else:
            return '.bin'

    def _get_media_size(self, media) -> Optional[int]:
        """Get the size of media in bytes."""
        if hasattr(media, 'document') and media.document:
            return media.document.size
        elif hasattr(media, 'photo') and media.photo:
            # For photos, size might be in different sizes array
            if hasattr(media.photo, 'sizes') and media.photo.sizes:
                # Return size of largest size
                return max((size.size for size in media.photo.sizes if hasattr(size, 'size')), default=None)
        return None

    def _extract_media_info(self, media, file_path: Path) -> MediaInfo:
        """Extract media information from Telegram media object."""
        media_type = MediaType.UNKNOWN
        file_name = file_path.name
        mime_type = MediaTypeDetector.get_mime_type(file_path)
        file_size = file_path.stat().st_size if file_path.exists() else None

        width = height = duration = None

        # Extract type-specific information
        if isinstance(media, MessageMediaPhoto):
            media_type = MediaType.PHOTO
            if hasattr(media.photo, 'sizes') and media.photo.sizes:
                # Get dimensions from largest size
                largest_size = max(
                    (size for size in media.photo.sizes if hasattr(size, 'w') and hasattr(size, 'h')),
                    key=lambda s: (s.w * s.h) if hasattr(s, 'w') and hasattr(s, 'h') else 0,
                    default=None
                )
                if largest_size:
                    width, height = largest_size.w, largest_size.h

        elif isinstance(media, MessageMediaDocument):
            media_type = MediaType.DOCUMENT
            # Check document attributes for more specific type
            if hasattr(media.document, 'attributes'):
                for attr in media.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        file_name = attr.file_name
                        # Re-detect type from actual filename
                        media_type = MediaTypeDetector.detect_from_extension(file_name)
                    elif hasattr(attr, 'duration'):
                        duration = attr.duration
                    elif hasattr(attr, 'w') and hasattr(attr, 'h'):
                        width, height = attr.w, attr.h

        elif isinstance(media, (MessageMediaAudio, MessageMediaVoice)):
            media_type = MediaType.VOICE if isinstance(media, MessageMediaVoice) else MediaType.AUDIO
            if hasattr(media, 'duration'):
                duration = media.duration

        return MediaInfo(
            media_type=media_type,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            width=width,
            height=height,
            duration=duration,
            file_path=file_path
        )

    def _is_allowed_type(self, media_type: MediaType) -> bool:
        """Check if media type is allowed."""
        return media_type in self.allowed_types

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up old temporary files.

        Args:
            max_age_hours: Maximum age of files to keep

        Returns:
            Number of files cleaned up
        """
        import time

        cleaned_count = 0
        cutoff_time = time.time() - (max_age_hours * 3600)

        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} old temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")

        return cleaned_count

    def get_temp_dir_size(self) -> int:
        """Get the total size of files in temp directory."""
        total_size = 0
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating temp directory size: {e}")

        return total_size