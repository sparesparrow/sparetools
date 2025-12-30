"""Base MCP server class for SpareTools MCP Core.

This module provides a base class for building MCP servers with
common functionality and patterns.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseMCPServer(ABC):
    """Base class for MCP servers.

    This abstract class provides common functionality for MCP servers
    including logging, tool registration, and lifecycle management.
    """

    def __init__(self, server_name: str) -> None:
        """Initialize the base MCP server.

        Args:
            server_name: Name of the server
        """
        self.server_name = server_name
        self.logger = logging.getLogger(f"mcp.{server_name}")
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    @abstractmethod
    def setup_tools(self) -> None:
        """Set up the server tools.

        Subclasses must implement this method to register their tools.
        """
        pass

    def register_tool(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a tool with the server.

        Args:
            name: Tool name
            handler: Tool handler function
            description: Tool description
            schema: Optional JSON schema for tool parameters
        """
        self._tools[name] = {
            "handler": handler,
            "description": description,
            "schema": schema or {},
        }
        self.logger.debug(f"Registered tool: {name}")

    def register_resource(
        self,
        uri: str,
        handler: Callable,
        name: str = "",
        description: str = "",
        mime_type: str = "application/json",
    ) -> None:
        """Register a resource with the server.

        Args:
            uri: Resource URI
            handler: Resource handler function
            name: Resource name
            description: Resource description
            mime_type: Resource MIME type
        """
        self._resources[uri] = {
            "handler": handler,
            "name": name or uri,
            "description": description,
            "mime_type": mime_type,
        }
        self.logger.debug(f"Registered resource: {uri}")

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool configuration or None
        """
        return self._tools.get(name)

    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a registered resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Resource configuration or None
        """
        return self._resources.get(uri)

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def list_resources(self) -> List[str]:
        """List all registered resource URIs.

        Returns:
            List of resource URIs
        """
        return list(self._resources.keys())

    async def initialize(self) -> None:
        """Initialize the server.

        This method is called before the server starts handling requests.
        """
        self.setup_tools()
        self._initialized = True
        self.logger.info(f"Initialized {self.server_name}")

    async def cleanup(self) -> None:
        """Clean up server resources.

        This method is called when the server is shutting down.
        """
        self._initialized = False
        self.logger.info(f"Cleaned up {self.server_name}")

    @property
    def is_initialized(self) -> bool:
        """Check if the server is initialized.

        Returns:
            True if initialized, False otherwise
        """
        return self._initialized

    def create_success_response(
        self,
        data: Any,
        message: str = "Success",
    ) -> str:
        """Create a success response.

        Args:
            data: Response data
            message: Success message

        Returns:
            JSON string response
        """
        return json.dumps({
            "status": "success",
            "message": message,
            "data": data,
        })

    def create_error_response(
        self,
        error: str,
        code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create an error response.

        Args:
            error: Error message
            code: Error code
            details: Optional error details

        Returns:
            JSON string response
        """
        response = {
            "status": "error",
            "error": error,
            "code": code,
        }
        if details:
            response["details"] = details
        return json.dumps(response)

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message."""
        if error:
            self.logger.error(f"{message}: {error}")
        else:
            self.logger.error(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)
