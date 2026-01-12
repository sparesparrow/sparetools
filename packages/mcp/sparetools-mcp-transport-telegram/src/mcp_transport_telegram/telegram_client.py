"""Telegram API client wrapper using Telethon."""

import asyncio
import logging
from typing import List, Optional, Union
from pathlib import Path
import tempfile

from telethon import TelegramClient
from telethon.tl.types import (
    Message,
    Dialog,
    User,
    Chat,
    Channel,
    MessageMediaDocument,
    MessageMediaPhoto,
    MessageMediaAudio,
    MessageMediaVoice
)

from .config import TelegramConfig


logger = logging.getLogger(__name__)


class TelegramAPIError(Exception):
    """Telegram API related errors."""
    pass


class TelegramClientWrapper:
    """Wrapper around Telethon TelegramClient for MCP Transport."""

    def __init__(self, config: TelegramConfig):
        """Initialize the Telegram client.

        Args:
            config: Telegram configuration
        """
        self.config = config
        self.client: Optional[TelegramClient] = None
        self._connected = False

        # Initialize Telethon client
        self.client = TelegramClient(
            session=config.session_name,
            api_id=config.api_id,
            api_hash=config.api_hash
        )

    async def connect(self) -> None:
        """Establish connection to Telegram API."""
        if self._connected:
            return

        try:
            logger.info("Connecting to Telegram API...")
            await self.client.start(
                phone=self.config.phone,
                bot_token=self.config.bot_token
            )
            self._connected = True
            logger.info("Successfully connected to Telegram API")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram API: {e}")
            raise TelegramAPIError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Telegram API."""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
            logger.info("Disconnected from Telegram API")

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self.client and self.client.is_connected()

    async def get_dialogs(self, limit: int = 100) -> List[Dialog]:
        """Retrieve available chats/dialogs.

        Args:
            limit: Maximum number of dialogs to retrieve

        Returns:
            List of Dialog objects
        """
        if not await self.is_connected():
            await self.connect()

        try:
            dialogs = await self.client.get_dialogs(limit=limit)
            return list(dialogs)
        except Exception as e:
            logger.error(f"Failed to get dialogs: {e}")
            raise TelegramAPIError(f"Get dialogs failed: {e}")

    async def get_messages(
        self,
        chat_id: Union[int, str],
        limit: int = 50,
        offset_id: int = 0
    ) -> List[Message]:
        """Fetch messages from specific chat.

        Args:
            chat_id: Chat identifier (username, ID, or entity)
            limit: Maximum number of messages to retrieve
            offset_id: Message ID offset for pagination

        Returns:
            List of Message objects
        """
        if not await self.is_connected():
            await self.connect()

        try:
            # Resolve chat entity
            entity = await self.client.get_entity(chat_id)

            # Get messages
            messages = await self.client.get_messages(
                entity=entity,
                limit=limit,
                offset_id=offset_id
            )

            return list(messages)
        except Exception as e:
            logger.error(f"Failed to get messages from chat {chat_id}: {e}")
            raise TelegramAPIError(f"Get messages failed: {e}")

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        reply_to: Optional[int] = None
    ) -> Message:
        """Send message to chat.

        Args:
            chat_id: Chat identifier
            text: Message text
            reply_to: Message ID to reply to

        Returns:
            Sent Message object
        """
        if not await self.is_connected():
            await self.connect()

        try:
            entity = await self.client.get_entity(chat_id)

            message = await self.client.send_message(
                entity=entity,
                message=text,
                reply_to=reply_to
            )

            logger.info(f"Sent message to chat {chat_id}: {text[:50]}...")
            return message
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
            raise TelegramAPIError(f"Send message failed: {e}")

    async def edit_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        text: str
    ) -> Message:
        """Edit existing message.

        Args:
            chat_id: Chat identifier
            message_id: ID of message to edit
            text: New message text

        Returns:
            Edited Message object
        """
        if not await self.is_connected():
            await self.connect()

        try:
            entity = await self.client.get_entity(chat_id)

            message = await self.client.edit_message(
                entity=entity,
                message=message_id,
                text=text
            )

            logger.info(f"Edited message {message_id} in chat {chat_id}")
            return message
        except Exception as e:
            logger.error(f"Failed to edit message {message_id} in chat {chat_id}: {e}")
            raise TelegramAPIError(f"Edit message failed: {e}")

    async def download_media(
        self,
        message: Message,
        file_path: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """Download media from a message.

        Args:
            message: Message containing media
            file_path: Optional path to save the file

        Returns:
            Path to downloaded file, or None if no media
        """
        if not message.media:
            return None

        if not await self.is_connected():
            await self.connect()

        try:
            # Create temporary file if no path provided
            if file_path is None:
                suffix = self._get_media_suffix(message.media)
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                )
                file_path = Path(temp_file.name)
                temp_file.close()

            # Download media
            downloaded_path = await self.client.download_media(
                message=message,
                file=file_path
            )

            if downloaded_path:
                logger.info(f"Downloaded media to {downloaded_path}")
                return Path(downloaded_path)
            else:
                logger.warning("Failed to download media")
                return None

        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            raise TelegramAPIError(f"Media download failed: {e}")

    def _get_media_suffix(self, media) -> str:
        """Get appropriate file suffix based on media type."""
        if isinstance(media, MessageMediaDocument):
            # Try to get extension from document attributes
            if hasattr(media.document, 'attributes'):
                for attr in media.document.attributes:
                    if hasattr(attr, 'file_name'):
                        return Path(attr.file_name).suffix or '.bin'
            return '.bin'
        elif isinstance(media, MessageMediaPhoto):
            return '.jpg'
        elif isinstance(media, MessageMediaAudio) or isinstance(media, MessageMediaVoice):
            return '.ogg'
        else:
            return '.bin'

    async def get_chat_info(self, chat_id: Union[int, str]) -> Union[User, Chat, Channel]:
        """Get information about a chat.

        Args:
            chat_id: Chat identifier

        Returns:
            Chat/User/Channel information
        """
        if not await self.is_connected():
            await self.connect()

        try:
            return await self.client.get_entity(chat_id)
        except Exception as e:
            logger.error(f"Failed to get chat info for {chat_id}: {e}")
            raise TelegramAPIError(f"Get chat info failed: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()