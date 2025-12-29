"""Mock MCP implementation for environments where MCP can't be installed."""

import json
from typing import Any, Dict, List, Optional


class Tool:
    """Mock MCP Tool class."""

    def __init__(self, **kwargs):
        # Accept any keyword arguments to match different MCP versions
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def call(self, arguments: Dict[str, Any]) -> Any:
        """Call the tool. To be implemented by subclasses."""
        raise NotImplementedError("Tool.call() must be implemented by subclass")


class Resource:
    """Mock MCP Resource class."""

    def __init__(self, uri: str, name: str, description: str, mime_type: str = "application/json"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type

    async def read(self) -> str:
        """Read the resource. To be implemented by subclasses."""
        raise NotImplementedError("Resource.read() must be implemented by subclass")


class Server:
    """Mock MCP Server class."""

    def __init__(self, name: str):
        self.name = name
        self._tools: Dict[str, Tool] = {}
        self._resources: Dict[str, Resource] = {}

    def list_tools(self):
        """Decorator to register a tool list handler."""
        def decorator(func):
            self._list_tools_handler = func
            return func
        return decorator

    def call_tool(self):
        """Decorator to register a tool call handler."""
        def decorator(func):
            self._call_tool_handler = func
            return func
        return decorator

    def list_resources(self):
        """Decorator to register a resource list handler."""
        def decorator(func):
            self._list_resources_handler = func
            return func
        return decorator

    def read_resource(self):
        """Decorator to register a resource read handler."""
        def decorator(func):
            self._read_resource_handler = func
            return func
        return decorator

    def stdio_server(self):
        """Mock stdio server context manager."""
        return MockStdioServer(self)

    async def serve(self, read_stream, write_stream):
        """Mock serve method - just run for a short time to simulate MCP protocol."""
        import asyncio
        await asyncio.sleep(0.1)  # Simulate brief server operation


class MockStdioServer:
    """Mock stdio server for testing."""

    def __init__(self, server: Server):
        self.server = server

    async def __aenter__(self):
        return MockStreams(), MockStreams()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockStreams:
    """Mock streams for testing."""
    pass


# Mock MCP types
class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text


class ImageContent:
    def __init__(self, type: str, data: str, mime_type: str = "image/png"):
        self.type = type
        self.data = data
        self.mime_type = mime_type


class EmbeddedResource:
    def __init__(self, type: str, resource):
        self.type = type
        self.resource = resource


# Mock MCP request/response types
class CallToolRequest:
    def __init__(self, params: Dict[str, Any]):
        self.params = MockParams(params)


class ReadResourceRequest:
    def __init__(self, params: Dict[str, Any]):
        self.params = MockParams(params)


class ListResourcesRequest:
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = MockParams(params or {})


class ListToolsRequest:
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = MockParams(params or {})


class MockParams:
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            setattr(self, key, value)