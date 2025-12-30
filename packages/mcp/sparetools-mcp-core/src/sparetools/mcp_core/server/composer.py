"""Server Composer - Combine multiple MCP servers into one unified server.

This enables modular MCP server development where specialized servers
can be composed into larger, feature-rich servers.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServerComposer:
    """Compose multiple MCP servers into a unified server.

    This class allows combining tools and resources from multiple
    MCP server modules into a single server instance.
    """

    def __init__(self, name: str = "composed-server") -> None:
        """Initialize the server composer.

        Args:
            name: Name for the composed server
        """
        self.name = name
        self._server: Any = None
        self._composed_servers: Dict[str, Any] = {}
        self._tool_registry: Dict[str, Dict[str, Any]] = {}
        self._resource_registry: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self.logger = logging.getLogger(f"mcp.composer.{name}")

    def _ensure_server(self) -> Any:
        """Ensure FastMCP server instance exists.

        Returns:
            FastMCP server instance
        """
        if self._server is None:
            try:
                from mcp.server import FastMCP

                self._server = FastMCP(self.name)
            except ImportError:
                raise ImportError(
                    "mcp package is required for ServerComposer. "
                    "Install it with: pip install mcp"
                )
        return self._server

    def add_server(self, server_module: Any, prefix: str = "") -> None:
        """Add all tools from another server with optional prefix.

        Args:
            server_module: Server module with an 'app' attribute
            prefix: Optional prefix for tool names to avoid conflicts
        """
        server_app = getattr(server_module, "app", None)
        if server_app is None:
            raise ValueError(f"Module {server_module} does not have 'app' attribute")

        server_name = prefix or getattr(server_app, "name", "unknown")
        self._composed_servers[server_name] = server_app

        self.logger.info(f"Added server: {server_name}")

    def add_tool(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a standalone tool to the composed server.

        Args:
            name: Tool name
            handler: Tool handler function
            description: Tool description
            schema: Optional parameter schema
        """
        self._tool_registry[name] = {
            "handler": handler,
            "description": description,
            "schema": schema or {},
        }

        # Register with FastMCP if available
        server = self._ensure_server()

        @server.tool()
        async def wrapper(**kwargs: Any) -> Any:
            if asyncio.iscoroutinefunction(handler):
                return await handler(**kwargs)
            return handler(**kwargs)

        wrapper.__name__ = name
        wrapper.__doc__ = description

        self.logger.debug(f"Added tool: {name}")

    def add_resource(
        self,
        uri: str,
        handler: Callable,
        name: str = "",
        description: str = "",
        mime_type: str = "application/json",
    ) -> None:
        """Add a resource to the composed server.

        Args:
            uri: Resource URI
            handler: Resource handler function
            name: Resource name
            description: Resource description
            mime_type: Resource MIME type
        """
        self._resource_registry[uri] = {
            "handler": handler,
            "name": name or uri,
            "description": description,
            "mime_type": mime_type,
        }

        # Register with FastMCP if available
        server = self._ensure_server()

        @server.resource(uri)
        async def wrapper() -> Any:
            if asyncio.iscoroutinefunction(handler):
                return await handler()
            return handler()

        wrapper.__name__ = name or uri.replace("/", "_")
        wrapper.__doc__ = description

        self.logger.debug(f"Added resource: {uri}")

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool configuration or None
        """
        return self._tool_registry.get(name)

    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a registered resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Resource configuration or None
        """
        return self._resource_registry.get(uri)

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tool_registry.keys())

    def list_resources(self) -> List[str]:
        """List all registered resource URIs.

        Returns:
            List of resource URIs
        """
        return list(self._resource_registry.keys())

    def list_composed_servers(self) -> List[str]:
        """List all composed server names.

        Returns:
            List of composed server names
        """
        return list(self._composed_servers.keys())

    def get_server(self) -> Any:
        """Get the composed FastMCP server.

        Returns:
            FastMCP server instance
        """
        return self._ensure_server()

    async def initialize(self) -> None:
        """Initialize the composed server."""
        self._ensure_server()
        self._initialized = True
        self.logger.info(f"Initialized composed server: {self.name}")

    async def cleanup(self) -> None:
        """Clean up composed server resources."""
        self._initialized = False
        self.logger.info(f"Cleaned up composed server: {self.name}")

    def run(self) -> None:
        """Run the composed server."""
        server = self._ensure_server()
        self.logger.info(f"Starting composed server: {self.name}")
        server.run()

    @property
    def server(self) -> Any:
        """Get the FastMCP server instance.

        Returns:
            FastMCP server instance
        """
        return self._ensure_server()
