#!/usr/bin/env python3
"""
Mermaid Diagram Generator

A comprehensive tool for generating Mermaid diagrams from templates.
Supports multiple diagram types and export formats.
"""

import os
import json
import yaml
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
import base64
import io

class DiagramGenerator:
    """Main class for generating Mermaid diagrams from templates."""
    
    def __init__(self, templates_dir: str = "diagram_templates"):
        """Initialize the diagram generator.
        
        Args:
            templates_dir: Directory containing Mermaid template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self.load_templates()
        
    def load_templates(self):
        """Load all available templates from the templates directory."""
        if not self.templates_dir.exists():
            print(f"Warning: Templates directory {self.templates_dir} not found")
            return
            
        for template_file in self.templates_dir.glob("*.mmd"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Split YAML frontmatter and template content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        yaml_content = parts[1].strip()
                        template_content = parts[2].strip()
                        
                        # Parse YAML metadata
                        metadata = yaml.safe_load(yaml_content)
                        template_name = metadata.get('template_name', template_file.stem)
                        
                        self.templates[template_name] = {
                            'metadata': metadata,
                            'content': template_content,
                            'file': template_file
                        }
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    
    def list_templates(self) -> Dict[str, Dict]:
        """List all available templates.
        
        Returns:
            Dictionary of template names and their metadata
        """
        return {name: info['metadata'] for name, info in self.templates.items()}
    
    def generate_diagram(self, template_name: str, variables: Dict[str, Any] = None) -> str:
        """Generate a Mermaid diagram from a template.
        
        Args:
            template_name: Name of the template to use
            variables: Variables to substitute in the template
            
        Returns:
            Generated Mermaid diagram as string
            
        Raises:
            ValueError: If template not found
        """
        if template_name not in self.templates:
            available = list(self.templates.keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
        
        template_info = self.templates[template_name]
        template_content = template_info['content']
        metadata = template_info['metadata']
        
        # Merge default variables with provided variables
        default_vars = metadata.get('variables', {})
        if variables:
            default_vars.update(variables)
        
        # Create Jinja2 template
        template = Template(template_content)
        
        # Render the template
        try:
            rendered = template.render(**default_vars)
            return rendered
        except Exception as e:
            raise ValueError(f"Error rendering template: {e}")
    
    def export_diagram(self, mermaid_code: str, output_format: str = "svg", 
                      output_file: Optional[str] = None) -> str:
        """Export a Mermaid diagram to various formats.
        
        Args:
            mermaid_code: The Mermaid diagram code
            output_format: Export format (svg, png, pdf)
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        if output_format not in ["svg", "png", "pdf"]:
            raise ValueError("Output format must be 'svg', 'png', or 'pdf'")
        
        # Create temporary file for Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            temp_mmd_file = f.name
        
        try:
            # Generate output filename if not provided
            if not output_file:
                output_file = f"diagram.{output_format}"
            
            # Use Mermaid CLI to generate the diagram
            cmd = [
                "npx", "mermaid-cli", 
                temp_mmd_file, 
                "-o", output_file,
                "-f", output_format
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Mermaid CLI error: {result.stderr}")
            
            return output_file
            
        finally:
            # Clean up temporary file
            os.unlink(temp_mmd_file)
    
    def generate_and_export(self, template_name: str, variables: Dict[str, Any] = None,
                           output_format: str = "svg", output_file: Optional[str] = None) -> str:
        """Generate a diagram and export it in one step.
        
        Args:
            template_name: Name of the template to use
            variables: Variables to substitute in the template
            output_format: Export format (svg, png, pdf)
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        mermaid_code = self.generate_diagram(template_name, variables)
        return self.export_diagram(mermaid_code, output_format, output_file)

def main():
    """Command-line interface for the diagram generator."""
    parser = argparse.ArgumentParser(description="Generate Mermaid diagrams from templates")
    parser.add_argument("template_name", help="Name of the template to use")
    parser.add_argument("-v", "--variables", type=str, help="JSON string of variables")
    parser.add_argument("-f", "--format", choices=["svg", "png", "pdf"], 
                       default="svg", help="Output format")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--templates-dir", default="diagram_templates", 
                       help="Directory containing templates")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = DiagramGenerator(args.templates_dir)
    
    # List templates if requested
    if args.list:
        templates = generator.list_templates()
        print("Available templates:")
        for name, metadata in templates.items():
            print(f"  {name}: {metadata.get('description', 'No description')}")
        return
    
    # Parse variables
    variables = {}
    if args.variables:
        try:
            variables = json.loads(args.variables)
        except json.JSONDecodeError as e:
            print(f"Error parsing variables JSON: {e}")
            return
    
    try:
        # Generate and export diagram
        output_file = generator.generate_and_export(
            args.template_name,
            variables,
            args.format,
            args.output
        )
        print(f"Diagram generated: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())