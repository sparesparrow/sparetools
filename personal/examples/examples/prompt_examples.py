#!/usr/bin/env python3
"""
Example usage of the Prompt Renderer

This script demonstrates how to use the PromptRenderer class
to render various types of prompts with different variables.
"""

import json
from pathlib import Path
from prompt_renderer import PromptRenderer

def main():
    """Demonstrate various prompt rendering examples."""
    
    # Initialize the renderer
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    print("=== Prompt Renderer Examples ===\n")
    
    # Example 1: Code Generation Prompt
    print("1. Code Generation Prompt...")
    try:
        code_prompt = renderer.render_prompt(
            "mcp-code-generator",
            {
                "code_requirements": "Create a REST API endpoint for user authentication",
                "language": "Python",
                "framework": "FastAPI",
                "complexity": "intermediate",
                "include_tests": True,
                "include_docs": True,
                "style_guide": "PEP 8"
            }
        )
        print("✓ Code generation prompt rendered successfully")
        print("Generated Prompt:")
        print(code_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering code generation prompt: {e}")
    
    # Example 2: Analysis Prompt
    print("2. Analysis Prompt...")
    try:
        analysis_prompt = renderer.render_prompt(
            "mcp-analysis-prompt",
            {
                "analysis_type": "security_review",
                "target_code": "Authentication middleware implementation",
                "focus_areas": ["security", "performance", "maintainability"],
                "context": "Production e-commerce system",
                "urgency": "high",
                "include_recommendations": True
            }
        )
        print("✓ Analysis prompt rendered successfully")
        print("Generated Prompt:")
        print(analysis_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering analysis prompt: {e}")
    
    # Example 3: Documentation Prompt
    print("3. Documentation Prompt...")
    try:
        doc_prompt = renderer.render_prompt(
            "mcp-documentation-prompt",
            {
                "doc_type": "API documentation",
                "project_name": "User Management API",
                "target_audience": "frontend developers",
                "scope": "authentication and user management endpoints",
                "format": "OpenAPI/Swagger",
                "include_examples": True,
                "include_diagrams": True
            }
        )
        print("✓ Documentation prompt rendered successfully")
        print("Generated Prompt:")
        print(doc_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering documentation prompt: {e}")
    
    # Example 4: Testing Prompt
    print("4. Testing Prompt...")
    try:
        test_prompt = renderer.render_prompt(
            "mcp-testing-prompt",
            {
                "test_type": "integration tests",
                "code_to_test": "User authentication service with database integration",
                "testing_framework": "pytest",
                "language": "Python",
                "coverage_target": 95,
                "include_edge_cases": True,
                "include_performance_tests": True
            }
        )
        print("✓ Testing prompt rendered successfully")
        print("Generated Prompt:")
        print(test_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering testing prompt: {e}")
    
    # Example 5: Debugging Prompt
    print("5. Debugging Prompt...")
    try:
        debug_prompt = renderer.render_prompt(
            "mcp-debugging-prompt",
            {
                "issue_description": "API endpoint returns 500 error intermittently",
                "error_message": "Internal Server Error: Database connection timeout",
                "environment": "production",
                "language": "Python",
                "urgency": "critical",
                "include_logs": True,
                "include_solutions": True
            }
        )
        print("✓ Debugging prompt rendered successfully")
        print("Generated Prompt:")
        print(debug_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering debugging prompt: {e}")
    
    # Example 6: Architecture Prompt
    print("6. Architecture Prompt...")
    try:
        arch_prompt = renderer.render_prompt(
            "mcp-architecture-prompt",
            {
                "system_type": "microservices application",
                "requirements": "User management, order processing, payment handling, and notification services",
                "scale": "high",
                "technology_stack": "Python, FastAPI, React, PostgreSQL, Redis, Docker, Kubernetes",
                "constraints": "Must handle 10,000+ concurrent users, 99.9% uptime requirement",
                "include_diagrams": True,
                "include_security": True
            }
        )
        print("✓ Architecture prompt rendered successfully")
        print("Generated Prompt:")
        print(arch_prompt)
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"✗ Error rendering architecture prompt: {e}")
    
    # Example 7: List available templates
    print("7. Available Templates:")
    templates = renderer.list_templates()
    for name, metadata in templates.items():
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Example 8: List MCP prompts
    print("\n8. MCP Database Prompts:")
    mcp_prompts = renderer.list_mcp_prompts()
    for name, prompt in mcp_prompts.items():
        metadata = prompt.get('metadata', {})
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Example 9: Search functionality
    print("\n9. Search Results for 'code':")
    search_results = renderer.search_prompts("code")
    for result in search_results:
        print(f"  - {result['name']} ({result['type']}): {result['metadata'].get('description', 'No description')}")
    
    # Example 10: Categories
    print("\n10. Available Categories:")
    categories = renderer.get_categories()
    for category in categories:
        print(f"  - {category}")
    
    print("\n=== Examples Complete ===")

def demonstrate_mcp_operations():
    """Demonstrate MCP database operations."""
    print("\n=== MCP Database Operations ===\n")
    
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    # Add a new prompt to MCP database
    print("1. Adding new prompt to MCP database...")
    try:
        renderer.add_mcp_prompt(
            "custom-prompt",
            "# Custom Prompt\n\nThis is a custom prompt with variables: {{ variable1 }} and {{ variable2 }}",
            {
                "description": "A custom prompt for demonstration",
                "category": "custom",
                "variables": {
                    "variable1": "default_value_1",
                    "variable2": "default_value_2"
                }
            }
        )
        print("✓ Custom prompt added successfully")
    except Exception as e:
        print(f"✗ Error adding custom prompt: {e}")
    
    # Render the custom prompt
    print("\n2. Rendering custom prompt...")
    try:
        custom_rendered = renderer.render_prompt(
            "custom-prompt",
            {
                "variable1": "Hello",
                "variable2": "World"
            }
        )
        print("✓ Custom prompt rendered successfully")
        print("Generated Prompt:")
        print(custom_rendered)
    except Exception as e:
        print(f"✗ Error rendering custom prompt: {e}")
    
    # Update the custom prompt
    print("\n3. Updating custom prompt...")
    try:
        renderer.update_mcp_prompt(
            "custom-prompt",
            content="# Updated Custom Prompt\n\nThis is an updated custom prompt with {{ variable1 }} and {{ variable2 }}",
            metadata={"description": "An updated custom prompt for demonstration"}
        )
        print("✓ Custom prompt updated successfully")
    except Exception as e:
        print(f"✗ Error updating custom prompt: {e}")
    
    # Delete the custom prompt
    print("\n4. Deleting custom prompt...")
    try:
        renderer.delete_mcp_prompt("custom-prompt")
        print("✓ Custom prompt deleted successfully")
    except Exception as e:
        print(f"✗ Error deleting custom prompt: {e}")

if __name__ == "__main__":
    main()
    demonstrate_mcp_operations()