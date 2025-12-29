"""
MCP server tools for diagram generation.

This module provides MCP tool definitions for generating Mermaid diagrams.
Can be integrated into any MCP server that supports tool registration.
"""

from typing import Any, Dict, Optional
from pathlib import Path

from ..generators import MermaidGenerator, DiagramType, DiagramConfig


def register_diagram_tools(mcp_server, templates_dir: Optional[Path] = None):
    """Register diagram generation tools with an MCP server.
    
    Args:
        mcp_server: MCP server instance with register_tool method
        templates_dir: Optional path to templates directory
    """
    generator = MermaidGenerator(templates_dir)
    generator.initialize()
    
    # Register generateDiagram tool
    mcp_server.register_tool(
        name="generateDiagram",
        description="Generate a Mermaid diagram from a template or structure",
        parameters={
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Name of the diagram template (optional if using structure)"
                },
                "diagram_type": {
                    "type": "string",
                    "enum": ["flowchart", "sequence", "class", "state"],
                    "description": "Type of diagram to generate"
                },
                "nodes": {
                    "type": "array",
                    "description": "List of nodes for flowchart diagrams",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "layer_type": {
                                "type": "string",
                                "enum": ["schema", "provider", "consumer", "tooling", "success", "utilities", "security", "error"],
                                "description": "SpareTools layer type for color application"
                            }
                        }
                    }
                },
                "edges": {
                    "type": "array",
                    "description": "List of edges/relationships",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "label": {"type": "string"}
                        }
                    }
                },
                "direction": {
                    "type": "string",
                    "enum": ["TD", "BT", "LR", "RL"],
                    "default": "TD",
                    "description": "Flow direction for flowchart"
                },
                "variables": {
                    "type": "object",
                    "description": "Variables to use for template rendering"
                },
                "apply_colors": {
                    "type": "boolean",
                    "default": true,
                    "description": "Apply SpareTools color scheme"
                }
            }
        },
        handler=lambda params: _handle_generate_diagram(generator, params)
    )


def _handle_generate_diagram(generator: MermaidGenerator, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generateDiagram tool call.
    
    Args:
        generator: MermaidGenerator instance
        params: Tool parameters
        
    Returns:
        Dict with diagram definition and metadata
    """
    try:
        template_name = params.get("template_name")
        diagram_type = params.get("diagram_type", "flowchart")
        nodes = params.get("nodes", [])
        edges = params.get("edges", [])
        direction = params.get("direction", "TD")
        variables = params.get("variables", {})
        apply_colors = params.get("apply_colors", True)
        
        # Generate diagram
        if template_name:
            # Use template
            diagram = generator.generate_from_template(template_name, variables)
            if not diagram:
                return {"error": f"Template '{template_name}' not found"}
        elif nodes and edges:
            # Generate from structure
            diagram_type_enum = DiagramType.FLOWCHART
            if diagram_type == "sequence":
                diagram_type_enum = DiagramType.SEQUENCE
            elif diagram_type == "class":
                diagram_type_enum = DiagramType.CLASS
                
            config = DiagramConfig(type=diagram_type_enum)
            diagram = generator.generate_flowchart(nodes, edges, direction, config)
            
            # Apply colors if requested
            if apply_colors:
                node_mapping = {
                    node["id"]: node.get("layer_type", "utilities")
                    for node in nodes
                    if isinstance(node, dict) and "id" in node
                }
                diagram = generator.apply_sparetools_colors(diagram, node_mapping)
        else:
            return {"error": "Either template_name or nodes/edges must be provided"}
        
        if not diagram:
            return {"error": "Failed to generate diagram"}
        
        return {
            "diagram": diagram,
            "type": diagram_type,
            "valid": generator.validate_diagram(diagram, DiagramType.FLOWCHART)
        }
    except Exception as e:
        return {"error": str(e)}
