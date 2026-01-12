"""Message processing and handling for Telegram MCP transport."""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

from telethon.tl.types import Message

from .telegram_client import TelegramClientWrapper


logger = logging.getLogger(__name__)


@dataclass
class ProcessedMessage:
    """Represents a processed Telegram message."""
    message_id: int
    chat_id: int
    user_id: Optional[int]
    text: str
    timestamp: datetime
    has_media: bool
    media_type: Optional[str]
    reply_to_id: Optional[int]
    thread_id: Optional[int]


class MessageHandler:
    """Handles incoming Telegram messages and manages processing state."""

    def __init__(
        self,
        telegram_client: TelegramClientWrapper,
        max_age_seconds: int = 3600,
        deduplication_window: int = 300
    ):
        """Initialize message handler.

        Args:
            telegram_client: Telegram client wrapper
            max_age_seconds: Maximum age of messages to process
            deduplication_window: Time window for message deduplication in seconds
        """
        self.telegram_client = telegram_client
        self.max_age_seconds = max_age_seconds
        self.deduplication_window = deduplication_window

        # Track processed message IDs for deduplication
        self.processed_messages: Set[int] = set()
        self.message_timestamps: Dict[int, datetime] = {}

        # Processing queue
        self.message_queue: asyncio.Queue[ProcessedMessage] = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None

        # Chat state tracking
        self.last_message_ids: Dict[int, int] = {}  # chat_id -> last_message_id

    async def start_processing(self) -> None:
        """Start the message processing task."""
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self._process_messages())
            logger.info("Started message processing task")

    async def stop_processing(self) -> None:
        """Stop the message processing task."""
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped message processing task")

    async def process_incoming_messages(self, messages: List[Message]) -> List[ProcessedMessage]:
        """Process a batch of incoming messages.

        Args:
            messages: List of Telegram messages

        Returns:
            List of processed messages that are new and valid
        """
        processed_messages = []
        current_time = datetime.now()

        for message in messages:
            # Skip if message is too old
            if self._is_message_too_old(message, current_time):
                continue

            # Skip if already processed (deduplication)
            if message.id in self.processed_messages:
                continue

            # Convert to processed message
            processed = self._convert_to_processed_message(message)

            # Mark as processed
            self.processed_messages.add(message.id)
            self.message_timestamps[message.id] = current_time

            processed_messages.append(processed)

        # Clean up old processed message tracking
        await self._cleanup_old_messages(current_time)

        return processed_messages

    async def get_next_message(self) -> ProcessedMessage:
        """Get the next processed message from the queue."""
        return await self.message_queue.get()

    def _is_message_too_old(self, message: Message, current_time: datetime) -> bool:
        """Check if a message is too old to process."""
        if not message.date:
            return True

        message_time = message.date.replace(tzinfo=None)
        age = current_time - message_time

        return age.total_seconds() > self.max_age_seconds

    def _convert_to_processed_message(self, message: Message) -> ProcessedMessage:
        """Convert a Telegram Message to ProcessedMessage."""
        # Determine media type
        media_type = None
        has_media = bool(message.media)

        if has_media and message.media:
            media_class = message.media.__class__.__name__
            if 'Photo' in media_class:
                media_type = 'photo'
            elif 'Document' in media_class:
                media_type = 'document'
            elif 'Voice' in media_class:
                media_type = 'voice'
            elif 'Audio' in media_class:
                media_type = 'audio'
            else:
                media_type = 'other'

        # Extract thread/reply information
        reply_to_id = None
        thread_id = None

        if message.reply_to:
            reply_to_id = message.reply_to.reply_to_msg_id
            # For channels, thread_id might be different
            if hasattr(message.reply_to, 'reply_to_top_id'):
                thread_id = message.reply_to.reply_to_top_id

        return ProcessedMessage(
            message_id=message.id,
            chat_id=message.chat_id if message.chat_id else message.peer_id.channel_id,
            user_id=message.sender_id,
            text=message.text or "",
            timestamp=message.date.replace(tzinfo=None) if message.date else datetime.now(),
            has_media=has_media,
            media_type=media_type,
            reply_to_id=reply_to_id,
            thread_id=thread_id
        )

    async def _cleanup_old_messages(self, current_time: datetime) -> None:
        """Clean up old message tracking to prevent memory leaks."""
        cutoff_time = current_time - timedelta(seconds=self.deduplication_window)

        # Remove old timestamps
        expired_ids = [
            msg_id for msg_id, timestamp in self.message_timestamps.items()
            if timestamp < cutoff_time
        ]

        for msg_id in expired_ids:
            self.processed_messages.discard(msg_id)
            del self.message_timestamps[msg_id]

        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} old message IDs")

    async def _process_messages(self) -> None:
        """Background task to process messages from the queue."""
        try:
            while True:
                # Get message from queue
                message = await self.message_queue.get()

                try:
                    # Here we would normally forward to MCP tools
                    # For now, just log the message
                    logger.info(
                        f"Processed message {message.message_id} "
                        f"from chat {message.chat_id}: {message.text[:100]}..."
                    )

                    # Mark task as done
                    self.message_queue.task_done()

                except Exception as e:
                    logger.error(f"Error processing message {message.message_id}: {e}")
                    # Continue processing other messages even if one fails

        except asyncio.CancelledError:
            logger.info("Message processing task cancelled")
            raise
        except Exception as e:
            logger.error(f"Fatal error in message processing task: {e}")
            raise

    async def update_last_message_id(self, chat_id: int, message_id: int) -> None:
        """Update the last processed message ID for a chat."""
        self.last_message_ids[chat_id] = message_id

    def get_last_message_id(self, chat_id: int) -> Optional[int]:
        """Get the last processed message ID for a chat."""
        return self.last_message_ids.get(chat_id)