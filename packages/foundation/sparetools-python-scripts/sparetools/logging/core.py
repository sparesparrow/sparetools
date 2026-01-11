"""
Structured Logging Core

Provides structured logging with ANSI coloring, context management,
and various output formats for the SpareTools ecosystem.
"""

import logging
import sys
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any, TextIO
from pathlib import Path


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"


class ColoredFormatter(logging.Formatter):
    """Logging formatter with ANSI color support."""

    COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLACK,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE,
    }

    LEVEL_NAMES = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRIT",
    }

    def __init__(self, use_colors: bool = True, show_timestamp: bool = True):
        """
        Initialize colored formatter.

        Args:
            use_colors: Whether to use ANSI colors
            show_timestamp: Whether to show timestamps
        """
        self.use_colors = use_colors and self._supports_color()

        if show_timestamp:
            fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        else:
            fmt = "[%(levelname)s] %(name)s: %(message)s"

        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            # Check environment variables
            if sys.platform == "win32":
                return "ANSICON" in os.environ or "WT_SESSION" in os.environ
            return True
        return False

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with optional colors."""
        # Add custom level name
        record.levelname = self.LEVEL_NAMES.get(record.levelno, record.levelname)

        # Format the message
        formatted = super().format(record)

        if self.use_colors:
            color = self.COLORS.get(record.levelno, "")
            if color:
                formatted = f"{color}{formatted}{Colors.RESET}"

        return formatted


class StructuredFormatter(logging.Formatter):
    """JSON-structured logging formatter."""

    def __init__(self, include_extra: bool = True):
        """
        Initialize structured formatter.

        Args:
            include_extra: Whether to include extra fields in JSON
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                    'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                    'thread', 'threadName', 'processName', 'process', 'message'
                }:
                    log_entry[key] = value

        import json
        return json.dumps(log_entry, default=str)


class ContextLogger:
    """Logger with context management capabilities."""

    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize context logger.

        Args:
            name: Logger name
            context: Default context dictionary
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}
        self._local = threading.local()

    def _get_context(self) -> Dict[str, Any]:
        """Get current context including thread-local context."""
        ctx = self.context.copy()
        if hasattr(self._local, 'context'):
            ctx.update(self._local.context)
        return ctx

    @contextmanager
    def context_manager(self, **kwargs):
        """
        Context manager to temporarily add context.

        Usage:
            with logger.context_manager(task="build", component="compiler"):
                logger.info("Starting build")
        """
        old_context = getattr(self._local, 'context', {})
        self._local.context = {**old_context, **kwargs}
        try:
            yield
        finally:
            self._local.context = old_context

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self._log(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self._log(logging.CRITICAL, message, kwargs)

    def _log(self, level: int, message: str, extra: Dict[str, Any]):
        """Internal logging method."""
        context = self._get_context()
        context.update(extra)

        self.logger.log(level, message, extra=context)


class LoggerManager:
    """Central logger configuration and management."""

    def __init__(self):
        self._configured = False
        self._loggers = {}

    def configure(
        self,
        level: str = "INFO",
        use_colors: bool = True,
        log_file: Optional[str] = None,
        structured: bool = False,
        show_timestamp: bool = True
    ):
        """
        Configure logging system.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Whether to use colored output
            log_file: Optional log file path
            structured: Whether to use JSON structured logging
            show_timestamp: Whether to show timestamps
        """
        if self._configured:
            return

        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatter
        if structured:
            formatter = StructuredFormatter()
        else:
            formatter = ColoredFormatter(use_colors=use_colors, show_timestamp=show_timestamp)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        self._configured = True

    def get_logger(self, name: str, context: Optional[Dict[str, Any]] = None) -> ContextLogger:
        """
        Get or create a context logger.

        Args:
            name: Logger name
            context: Default context

        Returns:
            ContextLogger instance
        """
        if name not in self._loggers:
            self._loggers[name] = ContextLogger(name, context)
        return self._loggers[name]

    def set_global_context(self, **kwargs):
        """Set global context for all loggers."""
        for logger in self._loggers.values():
            logger.context.update(kwargs)


# Global logger manager instance
logger_manager = LoggerManager()


def configure_logging(
    level: str = "INFO",
    use_colors: bool = True,
    log_file: Optional[str] = None,
    structured: bool = False,
    show_timestamp: bool = True
):
    """
    Configure the logging system.

    Args:
        level: Logging level
        use_colors: Whether to use colored output
        log_file: Optional log file path
        structured: Whether to use JSON structured logging
        show_timestamp: Whether to show timestamps
    """
    logger_manager.configure(level, use_colors, log_file, structured, show_timestamp)


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> ContextLogger:
    """
    Get a context logger instance.

    Args:
        name: Logger name
        context: Default context

    Returns:
        ContextLogger instance
    """
    return logger_manager.get_logger(name, context)


def set_global_context(**kwargs):
    """Set global context for all loggers."""
    logger_manager.set_global_context(**kwargs)


# Convenience functions
def remove_color_codes(text: str) -> str:
    """
    Remove ANSI color codes from text.

    Args:
        text: Text with potential ANSI codes

    Returns:
        Text without ANSI codes
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)