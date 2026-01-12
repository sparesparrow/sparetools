"""Telegram message polling infrastructure."""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from telethon.tl.types import Message

from .telegram_client import TelegramClientWrapper, TelegramAPIError
from .message_handler import MessageHandler, ProcessedMessage
from .config import Config


logger = logging.getLogger(__name__)


class TelegramPoller:
    """Polls Telegram for new messages and forwards them to the message handler."""

    def __init__(
        self,
        telegram_client: TelegramClientWrapper,
        message_handler: MessageHandler,
        config: Config
    ):
        """Initialize the Telegram poller.

        Args:
            telegram_client: Telegram client wrapper
            message_handler: Message processing handler
            config: Application configuration
        """
        self.telegram_client = telegram_client
        self.message_handler = message_handler
        self.config = config

        # Polling state
        self.polling_interval = config.polling_interval
        self.is_polling = False
        self.polling_task: Optional[asyncio.Task] = None

        # Rate limiting
        self.last_poll_time: Optional[datetime] = None
        self.rate_limit_delay = 60 / config.rate_limit_per_minute  # seconds between calls

        # Chat tracking
        self.monitored_chats: Set[int] = set()
        self.chat_last_message_ids: Dict[int, int] = {}

    async def start_polling(self, chat_ids: Optional[List[int]] = None) -> None:
        """Start polling for messages.

        Args:
            chat_ids: Specific chat IDs to monitor, or None for all dialogs
        """
        if self.is_polling:
            logger.warning("Polling is already active")
            return

        # Set up monitored chats
        if chat_ids:
            self.monitored_chats.update(chat_ids)
        else:
            # Get all available dialogs
            try:
                dialogs = await self.telegram_client.get_dialogs()
                self.monitored_chats.update(
                    dialog.id for dialog in dialogs
                    if hasattr(dialog, 'id')
                )
            except TelegramAPIError as e:
                logger.error(f"Failed to get dialogs for polling: {e}")
                return

        self.is_polling = True
        self.polling_task = asyncio.create_task(self._poll_loop())
        logger.info(f"Started polling for {len(self.monitored_chats)} chats")

    async def stop_polling(self) -> None:
        """Stop polling for messages."""
        if not self.is_polling:
            return

        self.is_polling = False

        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped polling")

    async def add_chat(self, chat_id: int) -> None:
        """Add a chat to the monitoring list."""
        self.monitored_chats.add(chat_id)
        logger.info(f"Added chat {chat_id} to monitoring")

    async def remove_chat(self, chat_id: int) -> None:
        """Remove a chat from the monitoring list."""
        self.monitored_chats.discard(chat_id)
        self.chat_last_message_ids.pop(chat_id, None)
        logger.info(f"Removed chat {chat_id} from monitoring")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        try:
            while self.is_polling:
                try:
                    await self._poll_iteration()
                except Exception as e:
                    logger.error(f"Error in polling iteration: {e}")
                    # Continue polling despite errors

                # Wait for next polling interval
                await asyncio.sleep(self.polling_interval)

        except asyncio.CancelledError:
            logger.info("Polling loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Fatal error in polling loop: {e}")
            raise

    async def _poll_iteration(self) -> None:
        """Single polling iteration - check all monitored chats for new messages."""
        # Rate limiting check
        if not self._can_poll():
            return

        self.last_poll_time = datetime.now()

        for chat_id in self.monitored_chats.copy():  # Copy to avoid modification during iteration
            try:
                await self._poll_chat(chat_id)
            except Exception as e:
                logger.error(f"Error polling chat {chat_id}: {e}")
                # Continue with other chats

    def _can_poll(self) -> bool:
        """Check if polling is allowed based on rate limiting."""
        if self.last_poll_time is None:
            return True

        time_since_last_poll = datetime.now() - self.last_poll_time
        return time_since_last_poll.total_seconds() >= self.rate_limit_delay

    async def _poll_chat(self, chat_id: int) -> None:
        """Poll a specific chat for new messages."""
        try:
            # Get the last message ID we processed for this chat
            last_message_id = self.chat_last_message_ids.get(chat_id, 0)

            # Get recent messages from this chat
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=50,  # Get last 50 messages
                offset_id=0  # Start from the most recent
            )

            if not messages:
                return

            # Filter for messages newer than our last processed message
            new_messages = []
            for message in messages:
                if message.id > last_message_id:
                    new_messages.append(message)
                else:
                    break  # Messages are ordered newest first

            if not new_messages:
                return

            # Reverse to process in chronological order (oldest first)
            new_messages.reverse()

            # Process the new messages
            processed_messages = await self.message_handler.process_incoming_messages(new_messages)

            # Queue processed messages for handling
            for processed_msg in processed_messages:
                await self.message_handler.message_queue.put(processed_msg)

            # Update the last message ID for this chat
            if messages:
                latest_message_id = max(msg.id for msg in messages)
                self.chat_last_message_ids[chat_id] = latest_message_id

                # Also update in message handler
                await self.message_handler.update_last_message_id(chat_id, latest_message_id)

            logger.debug(f"Polled chat {chat_id}: {len(new_messages)} new messages")

        except TelegramAPIError as e:
            logger.error(f"Telegram API error polling chat {chat_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error polling chat {chat_id}: {e}")

    async def get_status(self) -> Dict:
        """Get polling status information."""
        return {
            "is_polling": self.is_polling,
            "monitored_chats_count": len(self.monitored_chats),
            "polling_interval": self.polling_interval,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "rate_limit_delay": self.rate_limit_delay
        }