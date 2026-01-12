"""Telegram webhook infrastructure for real-time message processing."""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
import hashlib
import hmac
from urllib.parse import parse_qs

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    from uvicorn import Server, Config
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    Request = None
    HTTPException = None
    Server = None
    Config = None


from .telegram_client import TelegramClientWrapper
from .message_handler import MessageHandler
from .config import Config


logger = logging.getLogger(__name__)


class TelegramWebhook:
    """Webhook-based Telegram message receiver."""

    def __init__(
        self,
        telegram_client: TelegramClientWrapper,
        message_handler: MessageHandler,
        config: Config,
        webhook_url: str,
        webhook_secret: Optional[str] = None,
        port: int = 8080,
        host: str = "0.0.0.0"
    ):
        """Initialize Telegram webhook.

        Args:
            telegram_client: Telegram client wrapper
            message_handler: Message processing handler
            config: Application configuration
            webhook_url: Public URL for the webhook
            webhook_secret: Secret for webhook verification
            port: Port to run the webhook server on
            host: Host to bind the webhook server to
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is required for webhook functionality. "
                "Install with: pip install fastapi uvicorn"
            )

        self.telegram_client = telegram_client
        self.message_handler = message_handler
        self.config = config
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret
        self.port = port
        self.host = host

        # FastAPI app
        self.app = FastAPI(title="MCP Transport Telegram Webhook")
        self.server: Optional[Server] = None

        # Setup routes
        self._setup_routes()

        # Webhook state
        self.webhook_set = False

    def _setup_routes(self) -> None:
        """Set up FastAPI routes."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "mcp-transport-telegram"}

        @self.app.post("/webhook")
        async def telegram_webhook(request: Request):
            """Telegram webhook endpoint."""
            try:
                # Verify webhook secret if provided
                if self.webhook_secret:
                    await self._verify_webhook_secret(request)

                # Parse webhook data
                data = await request.json()

                # Process the update
                await self._process_webhook_update(data)

                return {"status": "ok"}

            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/webhook/{token}")
        async def telegram_webhook_with_token(token: str, request: Request):
            """Telegram webhook endpoint with bot token in URL."""
            # Verify token matches our bot token
            if not self._verify_bot_token(token):
                raise HTTPException(status_code=403, detail="Invalid token")

            # Process as regular webhook
            return await telegram_webhook(request)

    async def _verify_webhook_secret(self, request: Request) -> None:
        """Verify webhook secret token."""
        if not self.webhook_secret:
            return

        # Get secret from header
        secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not secret_header:
            raise HTTPException(status_code=403, detail="Missing secret token")

        # Verify secret
        if not hmac.compare_digest(secret_header, self.webhook_secret):
            raise HTTPException(status_code=403, detail="Invalid secret token")

    def _verify_bot_token(self, token: str) -> bool:
        """Verify bot token in URL path."""
        expected_token = self.config.telegram.bot_token
        if not expected_token:
            return False

        # Extract token part (before first colon)
        expected_token_part = expected_token.split(':')[0]
        return token == expected_token_part

    async def _process_webhook_update(self, data: Dict[str, Any]) -> None:
        """Process a webhook update from Telegram."""
        try:
            # Telegram webhook updates come in different formats
            # For now, we'll focus on message updates
            if 'message' in data:
                message_data = data['message']

                # Convert webhook message to Telethon-like format
                # This is a simplified conversion - in production you'd want
                # more comprehensive message parsing
                message = self._convert_webhook_message(message_data)

                if message:
                    # Process through message handler
                    processed_messages = await self.message_handler.process_incoming_messages([message])

                    # Queue for processing
                    for processed_msg in processed_messages:
                        await self.message_handler.message_queue.put(processed_msg)

                    logger.info(f"Processed webhook message {message.id}")

            elif 'edited_message' in data:
                # Handle edited messages
                logger.debug("Received edited message webhook")
                # Could implement edit handling here

            else:
                logger.debug(f"Received unhandled webhook update type: {list(data.keys())}")

        except Exception as e:
            logger.error(f"Error processing webhook update: {e}")

    def _convert_webhook_message(self, message_data: Dict[str, Any]):
        """Convert webhook message data to a format compatible with message handler."""
        try:
            # Create a mock Message-like object
            # This is a simplified implementation
            class MockMessage:
                def __init__(self, data):
                    self.id = data.get('message_id')
                    self.chat_id = data.get('chat', {}).get('id')
                    self.sender_id = data.get('from', {}).get('id')
                    self.text = data.get('text', '')
                    self.date = data.get('date')  # Unix timestamp
                    self.media = data.get('photo') or data.get('document') or data.get('voice')
                    self.reply_to = data.get('reply_to_message')

                    # Convert Unix timestamp to datetime if needed
                    if isinstance(self.date, int):
                        from datetime import datetime
                        self.date = datetime.fromtimestamp(self.date)

            return MockMessage(message_data)

        except Exception as e:
            logger.error(f"Error converting webhook message: {e}")
            return None

    async def set_webhook(self) -> bool:
        """Set the webhook URL in Telegram."""
        if not self.config.telegram.bot_token:
            logger.error("Bot token required for webhook setup")
            return False

        try:
            # Use Telegram Bot API directly to set webhook
            # Note: This would need to be implemented with httpx or similar
            # For now, we'll just log the intent
            logger.info(f"Setting webhook to: {self.webhook_url}")

            # TODO: Implement actual webhook setting via Bot API
            # This would involve making an HTTP request to:
            # https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}

            self.webhook_set = True
            return True

        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False

    async def delete_webhook(self) -> bool:
        """Delete the webhook."""
        try:
            # TODO: Implement webhook deletion
            logger.info("Deleting webhook")
            self.webhook_set = False
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False

    async def start_server(self) -> None:
        """Start the webhook server."""
        config = Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

        self.server = Server(config)

        logger.info(f"Starting webhook server on {self.host}:{self.port}")
        await self.server.serve()

    async def stop_server(self) -> None:
        """Stop the webhook server."""
        if self.server:
            self.server.should_exit = True
            logger.info("Stopped webhook server")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_server()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_server()