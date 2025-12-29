"""MCP server implementation for repository cleanup."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Lazy imports for optional dependencies
try:
    from mcp.server import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from rich.console import Console
from rich.logging import RichHandler

from .utils.validators import validate_config

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


class RepoCleanupServer:
    """MCP server for intelligent repository cleanup."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server.

        Args:
            config: Optional configuration dictionary
        """
        self.config = validate_config(config or {})

        # Server state
        self._running = False
        self._scan_cache: Dict[str, Any] = {}

        # Initialize server
        self.server = Server("repo-cleanup")

        # Initialize components
        self.tools = get_tools(self.config)
        self.resources = get_resources(self.config)

        # Set up request handlers
        self._setup_handlers()

        logger.info("Repository Cleanup MCP Server initialized")

    def _setup_handlers(self) -> None:
        """Set up MCP request handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            logger.info("Listing available tools")
            return list(self.tools.values())

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Call a tool."""
            tool_name = request.params.name
            tool_args = request.params.arguments or {}

            logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

            if tool_name not in self.tools:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]

            tool = self.tools[tool_name]
            try:
                result = await tool.call(tool_args)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "tool": tool_name,
                    "args": tool_args
                }))]

        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            logger.info("Listing available resources")
            return list(self.resources.values())

        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Read a resource."""
            uri = request.params.uri

            logger.info(f"Reading resource: {uri}")

            if uri not in self.resources:
                error_msg = f"Unknown resource: {uri}"
                logger.error(error_msg)
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]

            resource = self.resources[uri]
            try:
                content = await resource.read()
                return [TextContent(type="text", text=json.dumps(json.loads(content), indent=2))]
            except Exception as e:
                logger.error(f"Resource {uri} read failed: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def _health_check(self) -> Dict[str, Any]:
        """Perform server health check."""
        return {
            "status": "healthy",
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "config_loaded": bool(self.config),
            "cache_size": len(self._scan_cache)
        }

    async def run_stdio(self) -> None:
        """Run the server using stdio transport."""
        logger.info("Starting Repository Cleanup MCP server with stdio transport")

        try:
            self._running = True
            async with self.server.stdio_server() as (read_stream, write_stream):
                await self.server.serve(read_stream, write_stream)
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            self._running = False

    async def run_http(self, host: str = "localhost", port: int = 3000) -> None:
        """Run the server using HTTP transport.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting Repository Cleanup MCP server on {host}:{port}")

        try:
            self._running = True
            async with self.server.http_server(host=host, port=port) as server:
                await server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            self._running = False


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Repository Cleanup MCP Server")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--host", type=str, default="localhost", help="HTTP host")
    parser.add_argument("--port", type=int, default=3000, help="HTTP port")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio",
                       help="Transport to use")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Logging level")

    args = parser.parse_args()

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Load config if provided
    config = {}
    if args.config and Path(args.config).exists():
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    # Get repository path from environment or config
    repo_path = os.getenv("REPO_PATH") or config.get("repository_path")
    if repo_path:
        config["repository_path"] = Path(repo_path).resolve()
        # Validate repository path
        try:
            from .utils.validators import validate_repository_path
            validate_repository_path(config["repository_path"])
        except Exception as e:
            logger.error(f"Invalid repository path: {e}")
            sys.exit(1)

    # Create and run server
    try:
        server = RepoCleanupServer(config)

        if args.transport == "stdio":
            asyncio.run(server.run_stdio())
        else:
            asyncio.run(server.run_http(args.host, args.port))
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()