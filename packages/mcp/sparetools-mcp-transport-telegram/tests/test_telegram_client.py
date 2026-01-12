"""Unit tests for Telegram client wrapper."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from mcp_transport_telegram.config import TelegramConfig
from mcp_transport_telegram.telegram_client import TelegramClientWrapper, TelegramAPIError


@pytest.fixture
def telegram_config():
    """Create test Telegram configuration."""
    return TelegramConfig(
        api_id="123456",
        api_hash="abcdef123456",
        bot_token="bot_token_123",
        phone="+1234567890"
    )


@pytest.fixture
def telegram_client(telegram_config):
    """Create Telegram client instance."""
    return TelegramClientWrapper(telegram_config)


class TestTelegramClientWrapper:
    """Test cases for TelegramClientWrapper."""

    @pytest.mark.asyncio
    async def test_connect_success(self, telegram_client):
        """Test successful connection."""
        with patch('mcp_transport_telegram.telegram_client.TelegramClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.is_connected.return_value = True

            await telegram_client.connect()

            assert telegram_client._connected is True
            mock_client.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, telegram_client):
        """Test connection failure."""
        with patch('mcp_transport_telegram.telegram_client.TelegramClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.start.side_effect = Exception("Connection failed")

            with pytest.raises(TelegramAPIError):
                await telegram_client.connect()

    @pytest.mark.asyncio
    async def test_get_dialogs(self, telegram_client):
        """Test getting dialogs."""
        mock_dialogs = [MagicMock(), MagicMock()]

        with patch.object(telegram_client, 'is_connected', return_value=True), \
             patch.object(telegram_client, 'connect', new_callable=AsyncMock), \
             patch.object(telegram_client.client, 'get_dialogs', new_callable=AsyncMock) as mock_get_dialogs:

            mock_get_dialogs.return_value = mock_dialogs

            result = await telegram_client.get_dialogs(limit=10)

            assert result == mock_dialogs
            mock_get_dialogs.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_send_message(self, telegram_client):
        """Test sending a message."""
        mock_message = MagicMock()
        chat_id = "@test_chat"
        text = "Test message"

        with patch.object(telegram_client, 'is_connected', return_value=True), \
             patch.object(telegram_client, 'connect', new_callable=AsyncMock), \
             patch.object(telegram_client.client, 'get_entity', new_callable=AsyncMock) as mock_get_entity, \
             patch.object(telegram_client.client, 'send_message', new_callable=AsyncMock) as mock_send:

            mock_get_entity.return_value = MagicMock()
            mock_send.return_value = mock_message

            result = await telegram_client.send_message(chat_id, text)

            assert result == mock_message
            mock_get_entity.assert_called_once_with(chat_id)
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages(self, telegram_client):
        """Test getting messages."""
        mock_messages = [MagicMock(), MagicMock()]
        chat_id = "@test_chat"

        with patch.object(telegram_client, 'is_connected', return_value=True), \
             patch.object(telegram_client, 'connect', new_callable=AsyncMock), \
             patch.object(telegram_client.client, 'get_entity', new_callable=AsyncMock) as mock_get_entity, \
             patch.object(telegram_client.client, 'get_messages', new_callable=AsyncMock) as mock_get_messages:

            mock_get_entity.return_value = MagicMock()
            mock_get_messages.return_value = mock_messages

            result = await telegram_client.get_messages(chat_id, limit=20)

            assert result == mock_messages
            mock_get_entity.assert_called_once_with(chat_id)
            mock_get_messages.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_media_no_media(self, telegram_client):
        """Test downloading media when message has no media."""
        mock_message = MagicMock()
        mock_message.media = None

        result = await telegram_client.download_media(mock_message)

        assert result is None

    @pytest.mark.asyncio
    async def test_download_media_success(self, telegram_client):
        """Test successful media download."""
        mock_message = MagicMock()
        mock_message.media = MagicMock()
        mock_message.media.__class__.__name__ = "MessageMediaDocument"

        download_path = "/tmp/test_file.bin"

        with patch.object(telegram_client, 'is_connected', return_value=True), \
             patch.object(telegram_client, 'connect', new_callable=AsyncMock), \
             patch.object(telegram_client.client, 'download_media', new_callable=AsyncMock) as mock_download:

            mock_download.return_value = download_path

            result = await telegram_client.download_media(mock_message)

            assert result == Path(download_path)
            mock_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, telegram_client):
        """Test async context manager."""
        with patch.object(telegram_client, 'connect', new_callable=AsyncMock) as mock_connect, \
             patch.object(telegram_client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:

            async with telegram_client:
                pass

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()