"""
Mermaid diagram generator for SpareTools documentation templates.

This module provides functionality for generating Mermaid diagram
definitions from various inputs and templates. Adapted from mcp-project-orchestrator
to be standalone with SpareTools color scheme integration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

from .diagram_types import DiagramType, DiagramConfig, DiagramMetadata


def get_sparetools_color(layer_type: str) -> dict:
    """Get SpareTools color scheme for a layer type.
    
    Args:
        layer_type: One of 'schema', 'provider', 'consumer', 'tooling', 
                   'success', 'utilities', 'security', 'error'
    
    Returns:
        Dict with 'fill', 'stroke', and 'color' keys
    """
    colors = {
        'schema': {'fill': '#2196F3', 'stroke': '#1565C0', 'color': '#fff'},
        'provider': {'fill': '#FF9800', 'stroke': '#E65100', 'color': '#fff'},
        'consumer': {'fill': '#9C27B0', 'stroke': '#6A1B9A', 'color': '#fff'},
        'tooling': {'fill': '#FFC107', 'stroke': '#F57C00', 'color': '#000'},
        'success': {'fill': '#4CAF50', 'stroke': '#2E7D32', 'color': '#fff'},
        'utilities': {'fill': '#607D8B', 'stroke': '#37474F', 'color': '#fff'},
        'security': {'fill': '#E91E63', 'stroke': '#880E4F', 'color': '#fff'},
        'error': {'fill': '#F44336', 'stroke': '#B71C1C', 'color': '#fff'},
    }
    return colors.get(layer_type.lower(), colors['utilities'])


class MermaidGenerator:
    """Class for generating Mermaid diagram definitions."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the Mermaid generator.
        
        Args:
            templates_dir: Optional path to templates directory. If None, uses default.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "prompts"
        self.templates_dir = templates_dir
        self.templates: Dict[str, Dict[str, Any]] = {}
        
    def initialize(self) -> None:
        """Initialize the generator.
        
        Creates the templates directory if it doesn't exist and
        loads any existing templates.
        """
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.load_templates()
        
    def load_templates(self) -> None:
        """Load Mermaid diagram templates from the templates directory."""
        if not self.templates_dir.exists():
            return
        for file_path in self.templates_dir.glob("*.json"):
            try:
                with open(file_path) as f:
                    template = json.load(f)
                self.templates[file_path.stem] = template
            except Exception:
                pass  # Skip invalid templates
                
    def generate_flowchart(
        self,
        nodes: List[Dict[str, str]] | List[tuple],
        edges: List[Dict[str, str]] | List[tuple],
        direction: str = "TD",
        config: Optional[DiagramConfig] = None,
    ) -> str:
        """Generate a flowchart diagram definition.
        
        Args:
            nodes: List of node definitions
            edges: List of edge definitions
            direction: Flow direction (TD, BT, LR, RL) - TD by default
            config: Optional diagram configuration
            
        Returns:
            Mermaid flowchart definition
        """
        if config is None:
            config = DiagramConfig(type=DiagramType.FLOWCHART)
            
        lines = [f"flowchart {direction}"]
        
        # Add nodes
        for node in nodes:
            if isinstance(node, dict):
                node_id = node["id"]
                node_label = node.get("label", node_id)
            else:
                node_id, node_label = node[0], node[1]
            node_shape = ""
            
            if node_shape:
                lines.append(f"    {node_id}[{node_label}]{{{node_shape}}}")
            else:
                lines.append(f"    {node_id}[{node_label}]")
                
        # Add edges
        for edge in edges:
            if isinstance(edge, dict):
                from_node = edge["from"]
                to_node = edge["to"]
                edge_label = edge.get("label", "")
                edge_style = edge.get("style", "-->")
            else:
                from_node, to_node, edge_label = edge
                edge_style = "-->"
            
            if edge_label:
                lines.append(f"    {from_node} {edge_style}|{edge_label}| {to_node}")
            else:
                lines.append(f"    {from_node} {edge_style} {to_node}")
                
        return "\n".join(lines)
        
    def generate_class(
        self,
        classes: List[Dict[str, Any]],
        relationships: List[tuple],
        config: Optional[DiagramConfig] = None,
    ) -> str:
        """Generate a class diagram definition.
        
        Args:
            classes: List of class definitions
            relationships: List of class relationships
            config: Optional diagram configuration
            
        Returns:
            Mermaid class diagram definition
        """
        if config is None:
            config = DiagramConfig(type=DiagramType.CLASS)
            
        lines = ["classDiagram"]
        
        # Add classes
        for class_def in classes:
            class_name = class_def["name"]
            
            # Class definition
            lines.append(f"    class {class_name} {{")
            
            # Properties
            for prop in class_def.get("attributes", []) or class_def.get("properties", []):
                if isinstance(prop, str):
                    lines.append(f"        +{prop}")
                    continue
                prop_name = prop.get("name", prop)
                prop_type = prop.get("type", "")
                prop_visibility = prop.get("visibility", "+")
                
                if prop_type:
                    lines.append(f"        {prop_visibility}{prop_name}: {prop_type}")
                else:
                    lines.append(f"        {prop_visibility}{prop_name}")
                    
            # Methods
            for method in class_def.get("methods", []):
                if isinstance(method, str):
                    lines.append(f"        +{method}")
                    continue
                method_name = method.get("name", method)
                method_params = method.get("params", "")
                method_return = method.get("return", "")
                method_visibility = method.get("visibility", "+")
                
                if method_return:
                    lines.append(
                        f"        {method_visibility}{method_name}({method_params}) {method_return}"
                    )
                else:
                    lines.append(f"        {method_visibility}{method_name}({method_params})")
                    
            lines.append("    }")
            
        # Add relationships
        for rel in relationships:
            if isinstance(rel, tuple):
                from_class, to_class, rel_type = rel
                # Map relationship type to Mermaid syntax
                rel_symbol = "--"
                if rel_type == "extends":
                    rel_symbol = "--|>"
                elif rel_type == "implements":
                    rel_symbol = "..|>"
                elif rel_type == "composition":
                    rel_symbol = "*--"
                elif rel_type == "aggregation":
                    rel_symbol = "o--"
                lines.append(f"    {from_class} {rel_symbol} {to_class}")
            else:
                from_class = rel["from"]
                to_class = rel["to"]
                rel_type = rel.get("type", "--")
                rel_label = rel.get("label", "")
                
                if rel_label:
                    lines.append(f"    {from_class} {rel_type} {to_class}: {rel_label}")
                else:
                    lines.append(f"    {from_class} {rel_type} {to_class}")
                
        return "\n".join(lines)
        
    def generate_sequence(
        self,
        participants: List[str],
        messages: List[tuple],
        config: Optional[DiagramConfig] = None,
    ) -> str:
        """Generate a sequence diagram definition.
        
        Args:
            participants: List of participant definitions
            messages: List of message definitions
            config: Optional diagram configuration
            
        Returns:
            Mermaid sequence diagram definition
        """
        if config is None:
            config = DiagramConfig(type=DiagramType.SEQUENCE)
            
        lines = ["sequenceDiagram"]
        
        # Add participants
        for participant in participants:
            if isinstance(participant, dict):
                participant_id = participant["id"]
                participant_label = participant.get("label", participant_id)
                lines.append(f"    participant {participant_id} as {participant_label}")
            else:
                participant_id = participant
                lines.append(f"    participant {participant_id}")
            
        # Add messages
        for message in messages:
            if isinstance(message, dict):
                from_participant = message["from"]
                to_participant = message["to"]
                message_text = message["text"]
                message_type = message.get("type", "->")
                activate = message.get("activate", False)
                deactivate = message.get("deactivate", False)
            else:
                # Support tuples/lists with variable lengths
                if not isinstance(message, (tuple, list)) or len(message) < 2:
                    continue
                from_participant = message[0]
                to_participant = message[1]
                message_text = message[2] if len(message) >= 3 else ""
                message_type = message[3] if len(message) >= 4 else "->>"
                activate = bool(message[4]) if len(message) >= 5 else False
                deactivate = bool(message[5]) if len(message) >= 6 else False
            
            lines.append(f"    {from_participant}{message_type}{to_participant}: {message_text}")
            
            # Add optional activation/deactivation
            if activate:
                lines.append(f"    activate {to_participant}")
            if deactivate:
                lines.append(f"    deactivate {to_participant}")
                
        return "\n".join(lines)
    
    def get_sparetools_style(
        self, 
        component_type: str, 
        stroke_width: int = 2
    ) -> str:
        """Get SpareTools color style for a component type.
        
        Args:
            component_type: Type of component (schema, provider, consumer, tooling, success, utility, error)
            stroke_width: Stroke width in pixels (default: 2)
        
        Returns:
            Mermaid style string
        """
        colors = get_sparetools_color(component_type)
        return f"fill:{colors['fill']},stroke:{colors['stroke']},color:{colors['color']},stroke-width:{stroke_width}px"
    
    def generate_package_dependencies(
        self,
        package_name: str,
        dependencies: List[str],
        node_colors: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generate a package dependency diagram.
        
        Args:
            package_name: Name of the main package
            dependencies: List of dependency package names
            node_colors: Optional dictionary mapping package names to component types
            
        Returns:
            Mermaid flowchart showing package dependencies
        """
        nodes = [{"id": package_name.replace("-", "_"), "label": package_name}]
        edges = []
        
        for dep in dependencies:
            dep_id = dep.replace("-", "_").replace(".", "_")
            nodes.append({"id": dep_id, "label": dep})
            edges.append({
                "from": package_name.replace("-", "_"),
                "to": dep_id,
                "label": "depends on"
            })
        
        # Default colors if not provided
        if node_colors is None:
            node_colors = {package_name.replace("-", "_"): "provider"}
            for dep in dependencies:
                dep_id = dep.replace("-", "_").replace(".", "_")
                if dep_id not in node_colors:
                    node_colors[dep_id] = "schema" if "schema" in dep.lower() else "utilities"
        
        diagram = self.generate_flowchart(nodes, edges)
        return self.apply_sparetools_colors(diagram, node_colors)
        
    def generate_architecture_layers(
        self,
        layers: List[Dict[str, Any]],
        dependencies: Optional[List[tuple]] = None,
    ) -> str:
        """Generate an architecture layer diagram.
        
        Args:
            layers: List of layer definitions, each with 'name' and 'packages'
            dependencies: Optional list of dependency tuples (from_layer, to_layer)
            
        Returns:
            Mermaid flowchart showing architecture layers
        """
        lines = ["graph TB"]
        
        # Add layers as subgraphs
        layer_ids = {}
        for i, layer in enumerate(layers):
            layer_name = layer["name"]
            layer_id = f"layer_{i}"
            layer_ids[layer_name] = layer_id
            
            lines.append(f'    subgraph "{layer_name}"')
            for package in layer.get("packages", []):
                pkg_id = package.replace("-", "_").replace(".", "_")
                lines.append(f"        {pkg_id}[{package}]")
            lines.append("    end")
        
        # Add dependencies between layers
        if dependencies:
            for from_layer, to_layer in dependencies:
                # Connect first package of each layer
                from_packages = layers[next(i for i, l in enumerate(layers) if l["name"] == from_layer)].get("packages", [])
                to_packages = layers[next(i for i, l in enumerate(layers) if l["name"] == to_layer)].get("packages", [])
                if from_packages and to_packages:
                    from_id = from_packages[0].replace("-", "_").replace(".", "_")
                    to_id = to_packages[0].replace("-", "_").replace(".", "_")
                    lines.append(f"    {from_id} --> {to_id}")
        
        # Apply SpareTools colors based on layer type
        node_colors = {}
        for layer in layers:
            layer_type = layer.get("type", "utilities").lower()
            for package in layer.get("packages", []):
                pkg_id = package.replace("-", "_").replace(".", "_")
                node_colors[pkg_id] = layer_type
        
        diagram = "\n".join(lines)
        return self.apply_sparetools_colors(diagram, node_colors)
        
    def apply_sparetools_colors(
        self,
        diagram: str,
        node_mapping: Dict[str, str]
    ) -> str:
        """Apply SpareTools color scheme to a diagram.
        
        Args:
            diagram: Mermaid diagram definition
            node_mapping: Dict mapping node IDs to layer types (schema, provider, etc.)
            
        Returns:
            Diagram with SpareTools colors applied
        """
        lines = diagram.split("\n")
        style_lines = []
        
        for node_id, layer_type in node_mapping.items():
            colors = get_sparetools_color(layer_type)
            style_lines.append(
                f"    style {node_id} fill:{colors['fill']},stroke:{colors['stroke']},color:{colors['color']}"
            )
        
        if style_lines:
            lines.extend(style_lines)
        
        return "\n".join(lines)
        
    def generate_from_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        config: Optional[DiagramConfig] = None,
    ) -> Optional[str]:
        """Generate a diagram definition from a template.
        
        Args:
            template_name: Name of the template to use
            variables: Variables to substitute in the template
            config: Optional diagram configuration
            
        Returns:
            Generated diagram definition or None if template not found
        """
        template = self.templates.get(template_name)
        if not template:
            return None
        
        return self.generate_from_template_impl(template, variables, config)

    def validate_diagram(self, definition: str, diagram_type: DiagramType) -> bool:
        """Validate a diagram definition.
        
        Args:
            definition: Diagram definition to validate
            diagram_type: Expected type of diagram
            
        Returns:
            True if valid, False otherwise
        """
        try:
            definition = definition.strip()
            
            if diagram_type == DiagramType.FLOWCHART:
                if definition.count('[') != definition.count(']'):
                    return False
                return definition.startswith("flowchart")
            elif diagram_type == DiagramType.SEQUENCE:
                if "participant" not in definition:
                    return False
                return definition.startswith("sequenceDiagram")
            elif diagram_type == DiagramType.CLASS:
                return definition.startswith("classDiagram")
            
            return False
        except Exception:
            return False
    
    def save_diagram(self, metadata: DiagramMetadata, definition: str, path: Path) -> None:
        """Save a diagram to disk.
        
        Args:
            metadata: Diagram metadata
            definition: Diagram definition
            path: Path to save to
        """
        path.write_text(definition)

    def load_diagram(self, path: Path) -> tuple:
        """Load a diagram from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            Tuple of (metadata, definition)
        """
        definition = path.read_text()
        meta = DiagramMetadata(
            name=path.stem,
            description="",
            type=DiagramType.FLOWCHART,
            version="0.1.0",
            author="",
            tags=[],
        )
        return meta, definition
            
    def generate_from_template_impl(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any],
        config: Optional[DiagramConfig],
    ) -> Optional[str]:
        """Internal implementation of template generation."""
        try:
            content = template.get("content", "")
            diagram_type = template.get("type", "flowchart")
            
            # Replace variables in the template
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                content = content.replace(placeholder, str(var_value))
                
            # Add configuration if provided
            if config:
                config_dict = config.to_dict()
                for key, value in config_dict.items():
                    if key in template.get("config", {}):
                        content = content.replace(f"{{{key}}}", str(value))
                        
            return content
            
        except Exception:
            return None
            
    def save_template(
        self,
        name: str,
        content: str,
        diagram_type: DiagramType,
        variables: Optional[Dict[str, str]] = None,
    ) -> None:
        """Save a new diagram template.
        
        Args:
            name: Template name
            content: Template content
            diagram_type: Type of diagram
            variables: Optional dictionary of variable descriptions
        """
        template = {
            "name": name,
            "type": str(diagram_type),
            "content": content,
            "variables": variables or {},
        }
        
        file_path = self.templates_dir / f"{name}.json"
        with open(file_path, 'w') as f:
            json.dump(template, f, indent=2)
        self.templates[name] = template
