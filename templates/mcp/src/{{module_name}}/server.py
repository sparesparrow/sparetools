"""MCP server implementation for {{project_name}}."""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp import Server, Tool, Resource
from mcp.types import (
    CallToolRequest,
    ReadResourceRequest,
    ListResourcesRequest,
    ListToolsRequest,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .tools import get_tools
from .resources import get_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {{class_name}}Server:
    """MCP server for {{project_name}}."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.server = Server("{{project_name}}")

        # Initialize tools and resources
        self.tools = get_tools()
        self.resources = get_resources()

        # Set up request handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP request handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            logger.info("Listing tools")
            return list(self.tools.values())

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Call a tool."""
            tool_name = request.params.name
            tool_args = request.params.arguments or {}

            logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

            if tool_name not in self.tools:
                raise ValueError(f"Unknown tool: {tool_name}")

            tool = self.tools[tool_name]
            try:
                result = await tool.call(tool_args)
                return [TextContent(type="text", text=json.dumps(result))]
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                raise

        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            logger.info("Listing resources")
            return list(self.resources.values())

        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Read a resource."""
            uri = request.params.uri

            logger.info(f"Reading resource: {uri}")

            if uri not in self.resources:
                raise ValueError(f"Unknown resource: {uri}")

            resource = self.resources[uri]
            try:
                content = await resource.read()
                return [TextContent(type="text", text=content)]
            except Exception as e:
                logger.error(f"Resource {uri} read failed: {e}")
                raise

    async def run_stdio(self) -> None:
        """Run the server using stdio transport."""
        logger.info("Starting {{project_name}} MCP server with stdio transport")

        try:
            async with self.server.stdio_server() as (read_stream, write_stream):
                await self.server.serve(read_stream, write_stream)
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

    async def run_http(self, host: str = "localhost", port: int = 3000) -> None:
        """Run the server using HTTP transport.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting {{project_name}} MCP server on {host}:{port}")

        try:
            async with self.server.http_server(host=host, port=port) as server:
                await server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="{{project_name}} MCP Server")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--host", type=str, default="localhost", help="HTTP host")
    parser.add_argument("--port", type=int, default=3000, help="HTTP port")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio",
                       help="Transport to use")

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

    # Create and run server
    server = {{class_name}}Server(config)

    if args.transport == "stdio":
        asyncio.run(server.run_stdio())
    else:
        asyncio.run(server.run_http(args.host, args.port))


if __name__ == "__main__":
    main()