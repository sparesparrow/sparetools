"""Resources for {{project_name}} MCP server."""

from typing import Dict
from mcp import Resource

from .example_resource import ExampleResource


def get_resources() -> Dict[str, Resource]:
    """Get all available resources.

    Returns:
        Dictionary mapping resource URIs to Resource instances
    """
    return {
        "resource://{{module_name}}/example": ExampleResource(),
    }