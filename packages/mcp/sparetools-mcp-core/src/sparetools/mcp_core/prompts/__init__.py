"""Prompts management for SpareTools MCP Core.

This module provides prompt template management, loading, and rendering capabilities.
"""

from sparetools.mcp_core.prompts.template import (
    PromptTemplate,
    PromptMetadata,
    PromptCategory,
)
from sparetools.mcp_core.prompts.loader import PromptLoader
from sparetools.mcp_core.prompts.manager import PromptManager

__all__ = [
    "PromptTemplate",
    "PromptMetadata",
    "PromptCategory",
    "PromptLoader",
    "PromptManager",
]
