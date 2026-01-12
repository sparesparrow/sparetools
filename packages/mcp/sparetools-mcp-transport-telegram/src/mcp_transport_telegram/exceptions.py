"""Custom exceptions for MCP Transport Telegram."""

from typing import Optional


class MCPTelegramError(Exception):
    """Base exception for MCP Transport Telegram errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code or "INTERNAL_ERROR"


class TelegramAPIError(MCPTelegramError):
    """Telegram API related errors."""
    pass


class MessageProcessingError(MCPTelegramError):
    """Message processing related errors."""
    pass


class MediaHandlingError(MCPTelegramError):
    """Media handling related errors."""
    pass


class ConfigurationError(MCPTelegramError):
    """Configuration related errors."""
    pass


class RateLimitError(MCPTelegramError):
    """Rate limiting errors."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class AuthenticationError(MCPTelegramError):
    """Authentication related errors."""
    pass


class PermissionError(MCPTelegramError):
    """Permission related errors."""
    pass


class ValidationError(MCPTelegramError):
    """Input validation errors."""
    pass