"""Template system for SpareTools MCP Core.

This module provides a comprehensive template system with Jinja2 support,
custom filters, and template management capabilities.
"""

from sparetools.mcp_core.templates.types import (
    TemplateType,
    TemplateCategory,
    TemplateMetadata,
    TemplateFile,
)
from sparetools.mcp_core.templates.base import BaseTemplate
from sparetools.mcp_core.templates.renderer import TemplateRenderer
from sparetools.mcp_core.templates.manager import TemplateManager

__all__ = [
    "TemplateType",
    "TemplateCategory",
    "TemplateMetadata",
    "TemplateFile",
    "BaseTemplate",
    "TemplateRenderer",
    "TemplateManager",
]
