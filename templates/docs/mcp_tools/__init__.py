"""
MCP tools for Mermaid diagram generation.

This package provides MCP tool definitions and integration helpers
for generating diagrams with SpareTools color scheme.
"""

from . import diagram_tools
from .diagram_tools import register_diagram_tools

__all__ = [
    "diagram_tools",
    "register_diagram_tools",
]
