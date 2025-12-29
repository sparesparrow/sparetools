"""
Example integration of diagram tools into an MCP server.

This module shows how to integrate the diagram generation tools
into a FastMCP or standard MCP server.
"""

# Example 1: FastMCP Integration
"""
from fastmcp import FastMCP
from pathlib import Path
from .diagram_tools import register_diagram_tools

# Create MCP server
mcp = FastMCP("SpareTools Documentation")

# Register diagram tools
templates_dir = Path(__file__).parent.parent / "prompts"
register_diagram_tools(mcp, templates_dir)

# Server is ready to use
"""

# Example 2: Standard MCP Server Integration
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pathlib import Path
from .diagram_tools import register_diagram_tools

async def main():
    # Create server
    server = Server("sparetools-docs")
    
    # Register diagram tools
    templates_dir = Path(__file__).parent.parent / "prompts"
    register_diagram_tools(server, templates_dir)
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
"""

# Example 3: Using the generator directly
"""
from pathlib import Path
from .generators import MermaidGenerator, DiagramType, DiagramConfig

# Initialize generator
generator = MermaidGenerator()
generator.initialize()

# Generate a simple flowchart
nodes = [
    {"id": "A", "label": "Schema Package", "layer_type": "schema"},
    {"id": "B", "label": "Provider Package", "layer_type": "provider"},
    {"id": "C", "label": "Consumer Package", "layer_type": "consumer"},
]

edges = [
    {"from": "A", "to": "B", "label": "defines"},
    {"from": "B", "to": "C", "label": "implements"},
]

config = DiagramConfig(type=DiagramType.FLOWCHART)
diagram = generator.generate_flowchart(nodes, edges, "TD", config)

# Apply SpareTools colors
node_mapping = {node["id"]: node["layer_type"] for node in nodes}
diagram = generator.apply_sparetools_colors(diagram, node_mapping)

print(diagram)
"""
