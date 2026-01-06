#!/usr/bin/env python3
"""
Test script for the Prompt Renderer

This script tests the basic functionality of the PromptRenderer class.
"""

from prompt_renderer import PromptRenderer
import json

def test_basic_functionality():
    """Test basic prompt rendering functionality."""
    print("Testing Prompt Renderer...")
    
    # Initialize renderer
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    # Test 1: List templates
    print("\n1. Testing template listing...")
    templates = renderer.list_templates()
    print(f"Found {len(templates)} local templates:")
    for name, metadata in templates.items():
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Test 2: List MCP prompts
    print("\n2. Testing MCP prompt listing...")
    mcp_prompts = renderer.list_mcp_prompts()
    print(f"Found {len(mcp_prompts)} MCP prompts:")
    for name, prompt in mcp_prompts.items():
        metadata = prompt.get('metadata', {})
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Test 3: Render a local template
    print("\n3. Testing local template rendering...")
    try:
        if "mcp-code-generator" in templates:
            prompt = renderer.render_prompt(
                "mcp-code-generator",
                {
                    "code_requirements": "Create a simple calculator function",
                    "language": "Python",
                    "framework": "None",
                    "complexity": "simple",
                    "include_tests": False,
                    "include_docs": False
                }
            )
            print("✓ Local template rendered successfully")
            print("Generated Prompt (first 200 chars):")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        else:
            print("⚠ No local templates found")
    except Exception as e:
        print(f"✗ Error rendering local template: {e}")
    
    # Test 4: Render an MCP prompt
    print("\n4. Testing MCP prompt rendering...")
    try:
        if "mcp-code-generator" in mcp_prompts:
            prompt = renderer.render_prompt(
                "mcp-code-generator",
                {
                    "code_requirements": "Create a REST API endpoint",
                    "language": "JavaScript",
                    "framework": "Express.js",
                    "complexity": "intermediate",
                    "include_tests": True,
                    "include_docs": True
                }
            )
            print("✓ MCP prompt rendered successfully")
            print("Generated Prompt (first 200 chars):")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        else:
            print("⚠ No MCP prompts found")
    except Exception as e:
        print(f"✗ Error rendering MCP prompt: {e}")
    
    # Test 5: Search functionality
    print("\n5. Testing search functionality...")
    try:
        search_results = renderer.search_prompts("code")
        print(f"✓ Search completed, found {len(search_results)} results")
        for result in search_results[:3]:  # Show first 3 results
            print(f"  - {result['name']} ({result['type']}): {result['metadata'].get('description', 'No description')}")
    except Exception as e:
        print(f"✗ Error searching: {e}")
    
    # Test 6: Categories
    print("\n6. Testing categories...")
    try:
        categories = renderer.get_categories()
        print(f"✓ Found {len(categories)} categories:")
        for category in categories:
            print(f"  - {category}")
    except Exception as e:
        print(f"✗ Error getting categories: {e}")
    
    # Test 7: MCP operations
    print("\n7. Testing MCP operations...")
    try:
        # Add a test prompt
        renderer.add_mcp_prompt(
            "test-prompt",
            "This is a test prompt with {{ variable }}",
            {
                "description": "Test prompt for testing",
                "category": "test",
                "variables": {
                    "variable": "test_value"
                }
            }
        )
        print("✓ Test prompt added to MCP database")
        
        # Render the test prompt
        test_prompt = renderer.render_prompt(
            "test-prompt",
            {"variable": "Hello World"}
        )
        print("✓ Test prompt rendered successfully")
        print(f"  Rendered: {test_prompt}")
        
        # Update the test prompt
        renderer.update_mcp_prompt(
            "test-prompt",
            content="This is an updated test prompt with {{ variable }}",
            metadata={"description": "Updated test prompt"}
        )
        print("✓ Test prompt updated successfully")
        
        # Delete the test prompt
        renderer.delete_mcp_prompt("test-prompt")
        print("✓ Test prompt deleted successfully")
        
    except Exception as e:
        print(f"✗ Error with MCP operations: {e}")
    
    print("\n=== Test Complete ===")

def test_template_loading():
    """Test template loading from files."""
    print("\n=== Testing Template Loading ===")
    
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    # Test loading specific template
    template = renderer.get_template("mcp-code-generator")
    if template:
        print("✓ Code generator template loaded successfully")
        print(f"  Description: {template['metadata'].get('description', 'No description')}")
        print(f"  Category: {template['metadata'].get('category', 'No category')}")
        print(f"  Variables: {list(template['metadata'].get('variables', {}).keys())}")
    else:
        print("✗ Failed to load code generator template")
    
    # Test template content
    if template and template['content']:
        print("✓ Template content loaded successfully")
        print(f"  Content length: {len(template['content'])} characters")
        print(f"  Contains Jinja2 syntax: {'{{' in template['content'] and '}}' in template['content']}")
    else:
        print("✗ Template content is empty or missing")

if __name__ == "__main__":
    test_basic_functionality()
    test_template_loading()