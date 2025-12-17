"""Example tool for {{project_name}} MCP server."""

import json
from typing import Any, Dict
from mcp import Tool


class ExampleTool(Tool):
    """Example tool that demonstrates basic MCP tool functionality."""

    def __init__(self) -> None:
        """Initialize the example tool."""
        super().__init__(
            name="example_tool",
            description="An example tool that processes input data",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input data to process"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "text", "uppercase"],
                        "default": "text",
                        "description": "Output format"
                    }
                },
                "required": ["input"]
            }
        )

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool.

        Args:
            arguments: Tool arguments

        Returns:
            Tool result
        """
        input_data = arguments.get("input", "")
        output_format = arguments.get("format", "text")

        # Process the input based on format
        if output_format == "json":
            result = {
                "input": input_data,
                "length": len(input_data),
                "processed": True
            }
        elif output_format == "uppercase":
            result = input_data.upper()
        else:  # text
            result = f"Processed: {input_data}"

        return {
            "result": result,
            "format": output_format,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }