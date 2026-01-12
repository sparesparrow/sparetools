"""Structured logging and error handling utilities for MCP Transport Telegram."""

import logging
import sys
import uuid
from typing import Dict, Any, Optional
from contextvars import ContextVar
from datetime import datetime
import json

from pythonjsonlogger import jsonlogger


# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIdFilter(logging.Filter):
    """Logging filter to add correlation ID to log records."""

    def filter(self, record):
        record.correlation_id = correlation_id.get()
        return True


class TelegramJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for Telegram MCP logs."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.fromtimestamp(record.created).isoformat()

        # Add log level as string
        log_record['level'] = record.levelname

        # Add module and function info
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # Add correlation ID if available
        correlation_id_value = correlation_id.get()
        if correlation_id_value:
            log_record['correlation_id'] = correlation_id_value

        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_record.update(record.extra_fields)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type ('json' or 'text')
        log_file: Optional log file path

    Returns:
        Root logger instance
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    if format_type.lower() == "json":
        formatter = TelegramJSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s'
        )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationIdFilter())

    logger.addHandler(console_handler)

    # Create file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(CorrelationIdFilter())
        logger.addHandler(file_handler)

    return logger


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set the correlation ID for the current context.

    Args:
        corr_id: Correlation ID to set, or None to generate new one

    Returns:
        The correlation ID that was set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())

    correlation_id.set(corr_id)
    return corr_id


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context information to log messages."""

    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})

    def log_with_context(self, level: int, message: str, **kwargs):
        """Log a message with additional context."""
        extra = kwargs.pop('extra', {})
        extra.update(self.extra)

        # Add operation context if provided
        if 'operation' in kwargs:
            extra['operation'] = kwargs.pop('operation')
        if 'user_id' in kwargs:
            extra['user_id'] = kwargs.pop('user_id')
        if 'chat_id' in kwargs:
            extra['chat_id'] = kwargs.pop('chat_id')

        self.log(level, message, extra=extra, **kwargs)


def get_logger(name: str) -> LoggerAdapter:
    """Get a logger adapter for the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        LoggerAdapter instance
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger)


class ErrorReporter:
    """Error reporting and handling utilities."""

    def __init__(self, logger: LoggerAdapter):
        """Initialize error reporter.

        Args:
            logger: Logger adapter instance
        """
        self.logger = logger

    def report_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        level: int = logging.ERROR
    ) -> None:
        """Report an error with context.

        Args:
            error: Exception that occurred
            operation: Operation being performed
            context: Additional context information
            level: Logging level
        """
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'operation': operation
        }

        if context:
            error_context.update(context)

        self.logger.log_with_context(
            level,
            f"Error in {operation}: {error}",
            extra={'extra_fields': error_context}
        )

    def report_telegram_error(
        self,
        error: Exception,
        operation: str,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> None:
        """Report Telegram-specific errors.

        Args:
            error: Telegram API error
            operation: Operation being performed
            chat_id: Chat ID if applicable
            user_id: User ID if applicable
        """
        context = {}
        if chat_id:
            context['chat_id'] = chat_id
        if user_id:
            context['user_id'] = user_id

        self.report_error(error, f"telegram_{operation}", context)


class RateLimiter:
    """Rate limiting utilities."""

    def __init__(self, max_calls: int, time_window: int):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, list] = {}

    def is_allowed(self, key: str = "default") -> bool:
        """Check if a call is allowed for the given key.

        Args:
            key: Rate limiting key

        Returns:
            True if call is allowed, False if rate limited
        """
        import time

        current_time = time.time()

        if key not in self.calls:
            self.calls[key] = []

        # Remove old calls outside the time window
        self.calls[key] = [
            call_time for call_time in self.calls[key]
            if current_time - call_time < self.time_window
        ]

        # Check if under limit
        if len(self.calls[key]) < self.max_calls:
            self.calls[key].append(current_time)
            return True

        return False

    def get_remaining_calls(self, key: str = "default") -> int:
        """Get remaining calls allowed for the key.

        Args:
            key: Rate limiting key

        Returns:
            Number of remaining calls
        """
        import time

        current_time = time.time()

        if key not in self.calls:
            return self.max_calls

        # Clean up old calls
        self.calls[key] = [
            call_time for call_time in self.calls[key]
            if current_time - call_time < self.time_window
        ]

        return max(0, self.max_calls - len(self.calls[key]))

    def get_reset_time(self, key: str = "default") -> float:
        """Get time until rate limit resets.

        Args:
            key: Rate limiting key

        Returns:
            Seconds until reset
        """
        import time

        if key not in self.calls or not self.calls[key]:
            return 0

        oldest_call = min(self.calls[key])
        return max(0, self.time_window - (time.time() - oldest_call))


class PerformanceMonitor:
    """Performance monitoring utilities."""

    def __init__(self, logger: LoggerAdapter):
        """Initialize performance monitor.

        Args:
            logger: Logger adapter instance
        """
        self.logger = logger
        self.operations: Dict[str, list] = {}

    def start_operation(self, operation: str) -> str:
        """Start timing an operation.

        Args:
            operation: Operation name

        Returns:
            Operation ID for later reference
        """
        import time

        op_id = str(uuid.uuid4())
        start_time = time.time()

        if operation not in self.operations:
            self.operations[operation] = []

        self.operations[operation].append({
            'id': op_id,
            'start_time': start_time,
            'end_time': None,
            'duration': None
        })

        return op_id

    def end_operation(self, operation: str, op_id: str) -> float:
        """End timing an operation.

        Args:
            operation: Operation name
            op_id: Operation ID from start_operation

        Returns:
            Duration in seconds
        """
        import time

        if operation not in self.operations:
            return 0

        end_time = time.time()

        for op in self.operations[operation]:
            if op['id'] == op_id and op['end_time'] is None:
                op['end_time'] = end_time
                op['duration'] = end_time - op['start_time']
                duration = op['duration']

                # Log performance
                self.logger.log_with_context(
                    logging.DEBUG,
                    f"Operation {operation} completed in {duration:.3f}s",
                    operation=operation,
                    duration=duration
                )

                return duration

        return 0

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Statistics dictionary
        """
        if operation not in self.operations:
            return {}

        ops = [op for op in self.operations[operation] if op['duration'] is not None]
        if not ops:
            return {}

        durations = [op['duration'] for op in ops]

        return {
            'count': len(ops),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_duration': sum(durations)
        }