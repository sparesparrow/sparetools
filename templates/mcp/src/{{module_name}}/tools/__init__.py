"""Tools for {{project_name}} MCP server."""

from typing import Dict, Any, Awaitable, List
from mcp import Tool

from .example_tool import ExampleTool


def get_tools() -> Dict[str, Tool]:
    """Get all available tools.

    Returns:
        Dictionary mapping tool names to Tool instances
    """
    return {
        "example_tool": ExampleTool(),
    }