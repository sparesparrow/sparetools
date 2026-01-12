"""Configuration management for MCP Transport Telegram."""

import os
from typing import Optional

from pydantic import BaseModel, Field


class TelegramConfig(BaseModel):
    """Telegram API configuration."""

    api_id: str = Field(..., description="Telegram API ID from telegram.org")
    api_hash: str = Field(..., description="Telegram API hash from telegram.org")
    bot_token: Optional[str] = Field(None, description="Bot token from @BotFather")
    phone: Optional[str] = Field(None, description="Phone number for client authentication")
    session_name: str = Field("mcp_transport_telegram", description="Telethon session name")


class Config(BaseModel):
    """Main configuration for MCP Transport Telegram."""

    telegram: TelegramConfig
    polling_interval: int = Field(30, description="Message polling interval in seconds")
    max_message_age: int = Field(3600, description="Maximum message age to process in seconds")
    rate_limit_per_minute: int = Field(30, description="Rate limit for API calls per minute")

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            telegram=TelegramConfig(
                api_id=os.getenv("TELEGRAM_API_ID", ""),
                api_hash=os.getenv("TELEGRAM_API_HASH", ""),
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
                phone=os.getenv("TELEGRAM_PHONE"),
                session_name=os.getenv("TELEGRAM_SESSION_NAME", "mcp_transport_telegram")
            ),
            polling_interval=int(os.getenv("TELEGRAM_POLLING_INTERVAL", "30")),
            max_message_age=int(os.getenv("TELEGRAM_MAX_MESSAGE_AGE", "3600")),
            rate_limit_per_minute=int(os.getenv("TELEGRAM_RATE_LIMIT_PER_MINUTE", "30"))
        )


# Global configuration instance
config = Config.from_env()