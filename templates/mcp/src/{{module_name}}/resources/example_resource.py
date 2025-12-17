"""Example resource for {{project_name}} MCP server."""

import json
from mcp import Resource


class ExampleResource(Resource):
    """Example resource that provides static data."""

    def __init__(self) -> None:
        """Initialize the example resource."""
        super().__init__(
            uri="resource://{{module_name}}/example",
            name="Example Resource",
            description="An example resource providing static data",
            mimeType="application/json"
        )

    async def read(self) -> str:
        """Read the resource content.

        Returns:
            Resource content as string
        """
        data = {
            "name": "{{project_name}}",
            "version": "{{version}}",
            "description": "{{project_description}}",
            "capabilities": [
                "tool_execution",
                "resource_providing",
                "data_processing"
            ],
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }

        return json.dumps(data, indent=2)