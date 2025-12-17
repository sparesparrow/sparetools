"""Tests for {{module_name}} MCP server."""

import pytest
from {{module_name}} import {{class_name}}Server


class Test{{class_name}}Server:
    """Test cases for {{class_name}}Server."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        server = {{class_name}}Server()
        assert server.config == {}
        assert server.tools is not None
        assert server.resources is not None

    def test_init_with_config(self) -> None:
        """Test initialization with configuration."""
        config = {"key": "value", "number": 42}
        server = {{class_name}}Server(config)
        assert server.config == config

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """Test listing tools."""
        server = {{class_name}}Server()
        tools = await server.server.list_tools()()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that example_tool is present
        tool_names = [tool.name for tool in tools]
        assert "example_tool" in tool_names

    @pytest.mark.asyncio
    async def test_list_resources(self) -> None:
        """Test listing resources."""
        server = {{class_name}}Server()
        resources = await server.server.list_resources()()

        assert isinstance(resources, list)
        assert len(resources) > 0

        # Check that example resource is present
        resource_uris = [resource.uri for resource in resources]
        assert "resource://{{module_name}}/example" in resource_uris

    @pytest.mark.asyncio
    async def test_call_tool_example_tool(self) -> None:
        """Test calling the example tool."""
        from mcp.types import CallToolRequest

        server = {{class_name}}Server()

        # Create a tool call request
        request = CallToolRequest(
            method="tools/call",
            params={
                "name": "example_tool",
                "arguments": {
                    "input": "test data",
                    "format": "json"
                }
            }
        )

        # Call the tool
        results = await server.server.call_tool()(request)

        assert len(results) == 1
        assert results[0].type == "text"

        # Parse the JSON result
        import json
        result_data = json.loads(results[0].text)
        assert result_data["result"]["input"] == "test data"
        assert result_data["result"]["processed"] is True

    @pytest.mark.asyncio
    async def test_read_resource_example(self) -> None:
        """Test reading the example resource."""
        from mcp.types import ReadResourceRequest

        server = {{class_name}}Server()

        # Create a resource read request
        request = ReadResourceRequest(
            method="resources/read",
            params={
                "uri": "resource://{{module_name}}/example"
            }
        )

        # Read the resource
        results = await server.server.read_resource()(request)

        assert len(results) == 1
        assert results[0].type == "text"

        # Parse the JSON content
        import json
        content_data = json.loads(results[0].text)
        assert content_data["name"] == "{{project_name}}"
        assert content_data["version"] == "{{version}}"