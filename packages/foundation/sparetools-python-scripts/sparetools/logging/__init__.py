"""
Structured Logging Module

Provides structured logging with ANSI coloring, context management,
and various output formats for the SpareTools ecosystem.
"""

from .core import (
    Colors,
    ColoredFormatter,
    StructuredFormatter,
    ContextLogger,
    LoggerManager,
    configure_logging,
    get_logger,
    set_global_context,
    remove_color_codes,
    logger_manager,
)

__all__ = [
    "Colors",
    "ColoredFormatter",
    "StructuredFormatter",
    "ContextLogger",
    "LoggerManager",
    "configure_logging",
    "get_logger",
    "set_global_context",
    "remove_color_codes",
    "logger_manager",
]