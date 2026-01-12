"""Unit tests for MCP server."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_transport_telegram.mcp_server import TelegramMCPServer
from mcp_transport_telegram.config import Config, TelegramConfig


@pytest.fixture
def telegram_config():
    """Create test Telegram configuration."""
    return TelegramConfig(
        api_id="123456",
        api_hash="abcdef123456",
        bot_token="bot_token_123"
    )


@pytest.fixture
def config(telegram_config):
    """Create test configuration."""
    return Config(telegram=telegram_config)


@pytest.fixture
def mcp_server(config):
    """Create MCP server instance."""
    return TelegramMCPServer(config)


class TestTelegramMCPServer:
    """Test cases for TelegramMCPServer."""

    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test server initialization."""
        assert mcp_server.config is not None
        assert mcp_server.server is not None
        assert mcp_server.telegram_client is not None
        assert mcp_server.message_handler is not None
        assert mcp_server.media_handler is not None

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_server):
        """Test listing available tools."""
        # Mock the server.list_tools call
        mock_list_tools = AsyncMock()
        mcp_server.server.list_tools = mock_list_tools

        # The actual tools are set up in __init__, so we just verify the structure exists
        assert hasattr(mcp_server, 'server')
        assert mcp_server.server is not None

    @pytest.mark.asyncio
    async def test_handle_list_chats(self, mcp_server):
        """Test list_chats tool handler."""
        mock_dialogs = [
            MagicMock(id=1, title="Test Chat", username=None),
            MagicMock(id=2, title=None, username="testuser")
        ]

        with patch.object(mcp_server.telegram_client, 'get_dialogs', new_callable=AsyncMock) as mock_get_dialogs:
            mock_get_dialogs.return_value = mock_dialogs

            result = await mcp_server._handle_list_chats({})

            assert len(result) == 1
            assert "Found 2 chats" in result[0].text
            assert "Test Chat" in result[0].text
            assert "testuser" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_send_message(self, mcp_server):
        """Test send_message tool handler."""
        mock_message = MagicMock()
        mock_message.id = 123

        with patch.object(mcp_server.telegram_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_message

            result = await mcp_server._handle_send_message({
                "chat_id": "@test_chat",
                "text": "Hello world"
            })

            assert len(result) == 1
            assert "Message sent successfully" in result[0].text
            assert "Hello world" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_send_message_missing_params(self, mcp_server):
        """Test send_message with missing parameters."""
        result = await mcp_server._handle_send_message({"text": "Hello"})

        assert len(result) == 1
        assert "Missing required arguments" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_messages(self, mcp_server):
        """Test get_messages tool handler."""
        mock_messages = [
            MagicMock(id=1, text="Hello", sender_id=123, date=MagicMock()),
            MagicMock(id=2, text="Hi there", sender_id=456, date=MagicMock())
        ]

        with patch.object(mcp_server.telegram_client, 'get_messages', new_callable=AsyncMock) as mock_get_messages:
            mock_get_messages.return_value = mock_messages

            result = await mcp_server._handle_get_messages({
                "chat_id": "@test_chat",
                "limit": 10
            })

            assert len(result) == 1
            assert "Found 2 messages" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_media(self, mcp_server):
        """Test get_media tool handler."""
        mock_message = MagicMock()
        mock_message.id = 123
        mock_message.media = MagicMock()

        with patch.object(mcp_server.telegram_client, 'get_messages', new_callable=AsyncMock) as mock_get_messages, \
             patch.object(mcp_server.media_handler, 'download_media', new_callable=AsyncMock) as mock_download:

            mock_get_messages.return_value = [mock_message]
            mock_download.return_value = MagicMock(
                success=True,
                local_path="/tmp/test.jpg",
                media_info=MagicMock(media_type=MagicMock(value="photo"))
            )

            result = await mcp_server._handle_get_media({
                "chat_id": "@test_chat",
                "message_id": 123
            })

            assert len(result) == 1
            assert "Media downloaded successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_server):
        """Test error handling in tool calls."""
        with patch.object(mcp_server.telegram_client, 'get_dialogs', side_effect=Exception("API Error")):
            result = await mcp_server._handle_list_chats({})

            assert len(result) == 1
            assert "Failed to list chats" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self, mcp_server):
        """Test handling unknown tools."""
        result = await mcp_server.call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text