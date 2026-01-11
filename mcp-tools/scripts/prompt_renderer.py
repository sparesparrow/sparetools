#!/usr/bin/env python3
"""
Prompt Template Renderer

A comprehensive system for rendering prompt templates with variable substitution.
Supports MCP prompt database integration and various prompt types.
"""

import os
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
import re

class PromptRenderer:
    """Main class for rendering prompt templates with variable substitution."""
    
    def __init__(self, templates_dir: str = "prompt_templates", mcp_db_path: str = "mcp_prompts.json"):
        """Initialize the prompt renderer.
        
        Args:
            templates_dir: Directory containing prompt template files
            mcp_db_path: Path to MCP prompt database JSON file
        """
        self.templates_dir = Path(templates_dir)
        self.mcp_db_path = Path(mcp_db_path)
        self.templates = {}
        self.mcp_database = {}
        self.load_templates()
        self.load_mcp_database()
        
    def load_templates(self):
        """Load all available prompt templates from the templates directory."""
        if not self.templates_dir.exists():
            print(f"Warning: Templates directory {self.templates_dir} not found")
            return
            
        for template_file in self.templates_dir.glob("*.prompt"):
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
    
    def load_mcp_database(self):
        """Load MCP prompt database if it exists."""
        if self.mcp_db_path.exists():
            try:
                with open(self.mcp_db_path, 'r', encoding='utf-8') as f:
                    self.mcp_database = json.load(f)
            except Exception as e:
                print(f"Error loading MCP database: {e}")
        else:
            # Create a basic MCP database structure
            self.mcp_database = {
                "prompts": {},
                "categories": {},
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2024-01-01"
                }
            }
            self.save_mcp_database()
    
    def save_mcp_database(self):
        """Save the MCP database to file."""
        try:
            with open(self.mcp_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.mcp_database, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving MCP database: {e}")
    
    def list_templates(self) -> Dict[str, Dict]:
        """List all available prompt templates.
        
        Returns:
            Dictionary of template names and their metadata
        """
        return {name: info['metadata'] for name, info in self.templates.items()}
    
    def list_mcp_prompts(self) -> Dict[str, Dict]:
        """List all prompts in the MCP database.
        
        Returns:
            Dictionary of MCP prompt names and their metadata
        """
        return self.mcp_database.get("prompts", {})
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a specific template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Template dictionary or None if not found
        """
        return self.templates.get(template_name)
    
    def render_prompt(self, template_name: str, variables: Dict[str, Any] = None) -> str:
        """Render a prompt template with variable substitution.
        
        Args:
            template_name: Name of the template to render
            variables: Variables to substitute in the template
            
        Returns:
            Rendered prompt as string
            
        Raises:
            ValueError: If template not found
        """
        # First check local templates
        if template_name in self.templates:
            template_info = self.templates[template_name]
            template_content = template_info['content']
            metadata = template_info['metadata']
        # Then check MCP database
        elif template_name in self.mcp_database.get("prompts", {}):
            mcp_prompt = self.mcp_database["prompts"][template_name]
            template_content = mcp_prompt.get("content", "")
            metadata = mcp_prompt.get("metadata", {})
        else:
            available = list(self.templates.keys()) + list(self.mcp_database.get("prompts", {}).keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
        
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
    
    def add_mcp_prompt(self, name: str, content: str, metadata: Dict[str, Any] = None):
        """Add a new prompt to the MCP database.
        
        Args:
            name: Name of the prompt
            content: Prompt content
            metadata: Optional metadata for the prompt
        """
        if metadata is None:
            metadata = {}
            
        self.mcp_database["prompts"][name] = {
            "content": content,
            "metadata": metadata,
            "created_at": "2024-01-01"  # In real implementation, use current timestamp
        }
        self.save_mcp_database()
    
    def update_mcp_prompt(self, name: str, content: str = None, metadata: Dict[str, Any] = None):
        """Update an existing MCP prompt.
        
        Args:
            name: Name of the prompt to update
            content: New content (optional)
            metadata: New metadata (optional)
        """
        if name not in self.mcp_database["prompts"]:
            raise ValueError(f"Prompt '{name}' not found in MCP database")
        
        if content is not None:
            self.mcp_database["prompts"][name]["content"] = content
        if metadata is not None:
            self.mcp_database["prompts"][name]["metadata"].update(metadata)
        
        self.mcp_database["prompts"][name]["updated_at"] = "2024-01-01"  # In real implementation, use current timestamp
        self.save_mcp_database()
    
    def delete_mcp_prompt(self, name: str):
        """Delete a prompt from the MCP database.
        
        Args:
            name: Name of the prompt to delete
        """
        if name not in self.mcp_database["prompts"]:
            raise ValueError(f"Prompt '{name}' not found in MCP database")
        
        del self.mcp_database["prompts"][name]
        self.save_mcp_database()
    
    def search_prompts(self, query: str, category: str = None) -> List[Dict]:
        """Search for prompts by content or metadata.
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching prompts
        """
        results = []
        query_lower = query.lower()
        
        # Search local templates
        for name, info in self.templates.items():
            metadata = info['metadata']
            if category and metadata.get('category') != category:
                continue
                
            if (query_lower in name.lower() or 
                query_lower in metadata.get('description', '').lower() or
                query_lower in info['content'].lower()):
                results.append({
                    'name': name,
                    'type': 'template',
                    'metadata': metadata,
                    'content': info['content'][:200] + "..." if len(info['content']) > 200 else info['content']
                })
        
        # Search MCP database
        for name, prompt in self.mcp_database.get("prompts", {}).items():
            metadata = prompt.get('metadata', {})
            if category and metadata.get('category') != category:
                continue
                
            if (query_lower in name.lower() or 
                query_lower in metadata.get('description', '').lower() or
                query_lower in prompt.get('content', '').lower()):
                results.append({
                    'name': name,
                    'type': 'mcp',
                    'metadata': metadata,
                    'content': prompt.get('content', '')[:200] + "..." if len(prompt.get('content', '')) > 200 else prompt.get('content', '')
                })
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available prompt categories.
        
        Returns:
            List of category names
        """
        categories = set()
        
        # From local templates
        for info in self.templates.values():
            category = info['metadata'].get('category')
            if category:
                categories.add(category)
        
        # From MCP database
        for prompt in self.mcp_database.get("prompts", {}).values():
            category = prompt.get('metadata', {}).get('category')
            if category:
                categories.add(category)
        
        return sorted(list(categories))
    
    def export_prompt(self, template_name: str, output_file: str, format: str = "txt"):
        """Export a rendered prompt to a file.
        
        Args:
            template_name: Name of the template to export
            output_file: Output file path
            format: Output format (txt, md, json)
        """
        # Get template metadata to determine default variables
        if template_name in self.templates:
            metadata = self.templates[template_name]['metadata']
        elif template_name in self.mcp_database.get("prompts", {}):
            metadata = self.mcp_database["prompts"][template_name].get("metadata", {})
        else:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Use default variables for export
        variables = metadata.get('variables', {})
        rendered = self.render_prompt(template_name, variables)
        
        if format == "json":
            output_data = {
                "template_name": template_name,
                "variables": variables,
                "rendered_content": rendered,
                "metadata": metadata
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)

def main():
    """Command-line interface for the prompt renderer."""
    parser = argparse.ArgumentParser(description="Render prompt templates with variable substitution")
    parser.add_argument("template_name", help="Name of the template to render")
    parser.add_argument("-v", "--variables", type=str, help="JSON string of variables")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-f", "--format", choices=["txt", "md", "json"], 
                       default="txt", help="Output format")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--list-mcp", action="store_true", help="List MCP database prompts")
    parser.add_argument("--search", help="Search prompts by query")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--templates-dir", default="prompt_templates", 
                       help="Directory containing templates")
    parser.add_argument("--mcp-db", default="mcp_prompts.json", 
                       help="MCP database file path")
    
    args = parser.parse_args()
    
    # Initialize renderer
    renderer = PromptRenderer(args.templates_dir, args.mcp_db)
    
    # List templates if requested
    if args.list:
        templates = renderer.list_templates()
        print("Available templates:")
        for name, metadata in templates.items():
            print(f"  {name}: {metadata.get('description', 'No description')}")
        return
    
    # List MCP prompts if requested
    if args.list_mcp:
        mcp_prompts = renderer.list_mcp_prompts()
        print("MCP database prompts:")
        for name, prompt in mcp_prompts.items():
            metadata = prompt.get('metadata', {})
            print(f"  {name}: {metadata.get('description', 'No description')}")
        return
    
    # Search prompts if requested
    if args.search:
        results = renderer.search_prompts(args.search, args.category)
        print(f"Search results for '{args.search}':")
        for result in results:
            print(f"  {result['name']} ({result['type']}): {result['metadata'].get('description', 'No description')}")
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
        # Render prompt
        rendered = renderer.render_prompt(args.template_name, variables)
        
        if args.output:
            renderer.export_prompt(args.template_name, args.output, args.format)
            print(f"Prompt exported to: {args.output}")
        else:
            print(rendered)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())