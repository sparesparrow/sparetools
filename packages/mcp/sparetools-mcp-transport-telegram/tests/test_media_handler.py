"""Unit tests for media handler."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_transport_telegram.media_handler import MediaHandler, MediaDownloadResult
from mcp_transport_telegram.media_types import MediaType, MediaInfo, MediaTypeDetector
from mcp_transport_telegram.config import TelegramConfig


@pytest.fixture
def telegram_config():
    """Create test Telegram configuration."""
    return TelegramConfig(
        api_id="123456",
        api_hash="abcdef123456",
        bot_token="bot_token_123"
    )


@pytest.fixture
def telegram_client(telegram_config):
    """Create mock Telegram client."""
    from mcp_transport_telegram.telegram_client import TelegramClientWrapper
    client = TelegramClientWrapper(telegram_config)
    return client


@pytest.fixture
def media_handler(telegram_client):
    """Create media handler instance."""
    return MediaHandler(telegram_client)


class TestMediaHandler:
    """Test cases for MediaHandler."""

    @pytest.mark.asyncio
    async def test_download_media_no_media(self, media_handler):
        """Test downloading media when message has no media."""
        mock_message = MagicMock()
        mock_message.media = None

        result = await media_handler.download_media(mock_message)

        assert isinstance(result, MediaDownloadResult)
        assert result.success is False
        assert result.error_message == "Message contains no media"

    @pytest.mark.asyncio
    async def test_download_media_success(self, media_handler):
        """Test successful media download."""
        mock_message = MagicMock()
        mock_message.media = MagicMock()
        mock_message.media.__class__.__name__ = "MessageMediaPhoto"

        download_path = "/tmp/test_image.jpg"

        with patch.object(media_handler.telegram_client, 'download_media', new_callable=AsyncMock) as mock_download:
            mock_download.return_value = download_path

            result = await media_handler.download_media(mock_message)

            assert result.success is True
            assert result.local_path == Path(download_path)
            assert result.media_info is not None
            assert result.media_info.media_type == MediaType.PHOTO

    @pytest.mark.asyncio
    async def test_download_media_file_too_large(self, media_handler):
        """Test downloading media that's too large."""
        media_handler.max_file_size = 1024  # Small limit

        mock_message = MagicMock()
        mock_message.media = MagicMock()
        mock_message.media.document = MagicMock()
        mock_message.media.document.size = 2048  # Larger than limit

        result = await media_handler.download_media(mock_message)

        assert result.success is False
        assert "exceeds maximum" in result.error_message

    @pytest.mark.asyncio
    async def test_upload_media_file_not_found(self, media_handler):
        """Test uploading media when file doesn't exist."""
        result = await media_handler.upload_media("/nonexistent/file.jpg", "@test_chat")

        assert result.success is False
        assert "File not found" in result.error_message

    @pytest.mark.asyncio
    async def test_cleanup_temp_files(self, media_handler):
        """Test cleanup of temporary files."""
        import time
        import os

        # Create a test file
        test_file = media_handler.temp_dir / "test_cleanup.txt"
        test_file.write_text("test")

        # Set old modification time (2 days ago)
        old_time = time.time() - (48 * 3600)
        os.utime(test_file, (old_time, old_time))

        # Clean up files older than 1 day
        cleaned_count = await media_handler.cleanup_temp_files(max_age_hours=24)

        assert cleaned_count >= 1
        # File should be gone
        assert not test_file.exists()


class TestMediaTypeDetector:
    """Test cases for MediaTypeDetector."""

    def test_detect_from_extension_photo(self):
        """Test detecting photo from extension."""
        assert MediaTypeDetector.detect_from_extension("test.jpg") == MediaType.PHOTO
        assert MediaTypeDetector.detect_from_extension("test.png") == MediaType.PHOTO

    def test_detect_from_extension_document(self):
        """Test detecting document from extension."""
        assert MediaTypeDetector.detect_from_extension("test.pdf") == MediaType.DOCUMENT
        assert MediaTypeDetector.detect_from_extension("test.docx") == MediaType.DOCUMENT

    def test_detect_from_extension_unknown(self):
        """Test detecting unknown type."""
        assert MediaTypeDetector.detect_from_extension("test.xyz") == MediaType.UNKNOWN

    def test_detect_from_mime_type(self):
        """Test detecting from MIME type."""
        assert MediaTypeDetector.detect_from_mime_type("image/jpeg") == MediaType.PHOTO
        assert MediaTypeDetector.detect_from_mime_type("application/pdf") == MediaType.DOCUMENT
        assert MediaTypeDetector.detect_from_mime_type("unknown/type") == MediaType.UNKNOWN

    def test_get_mime_type(self):
        """Test getting MIME type from file."""
        # This is a basic test - actual MIME detection depends on system
        mime_type = MediaTypeDetector.get_mime_type("test.jpg")
        assert mime_type is not None or mime_type == "image/jpeg"

    def test_is_safe_file_type(self):
        """Test checking if file type is safe."""
        assert MediaTypeDetector.is_safe_file_type("test.jpg") is True
        assert MediaTypeDetector.is_safe_file_type("test.exe") is False

    def test_get_safe_filename(self):
        """Test generating safe filename."""
        # Normal filename
        assert MediaTypeDetector.get_safe_filename("test.jpg") == "test.jpg"

        # Dangerous characters
        safe = MediaTypeDetector.get_safe_filename('test<file>.jpg')
        assert '<' not in safe and '>' not in safe

        # Long filename
        long_name = "a" * 300 + ".txt"
        safe_long = MediaTypeDetector.get_safe_filename(long_name, max_length=100)
        assert len(safe_long) <= 100