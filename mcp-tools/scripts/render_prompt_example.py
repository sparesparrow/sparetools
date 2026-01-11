#!/usr/bin/env python3
"""
renderPrompt Example

This script demonstrates the renderPrompt functionality as specified in the user query.
It shows how to render prompt templates with variable substitution.
"""

from prompt_renderer import PromptRenderer
import json

def render_prompt_example():
    """Demonstrate the renderPrompt functionality."""
    
    # Initialize the prompt renderer
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    print("=== renderPrompt Example ===\n")
    
    # Example 1: Basic renderPrompt usage
    print("1. Basic renderPrompt Usage:")
    print("   Template: mcp-code-generator")
    print("   Variables: {'code_requirements': 'Create a REST API with authentication', 'language': 'Python'}")
    
    try:
        rendered_prompt = renderer.render_prompt(
            "mcp-code-generator",
            {
                "code_requirements": "Create a REST API with authentication",
                "language": "Python"
            }
        )
        print("   ✓ Prompt rendered successfully!")
        print("   Generated Prompt:")
        print("   " + "="*60)
        print(rendered_prompt)
        print("   " + "="*60)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: renderPrompt with all variables
    print("2. renderPrompt with Complete Variables:")
    print("   Template: mcp-code-generator")
    print("   Variables: All available variables")
    
    try:
        rendered_prompt = renderer.render_prompt(
            "mcp-code-generator",
            {
                "code_requirements": "Create a microservices architecture with user management",
                "language": "Python",
                "framework": "FastAPI",
                "complexity": "advanced",
                "include_tests": True,
                "include_docs": True,
                "style_guide": "PEP 8"
            }
        )
        print("   ✓ Prompt rendered successfully!")
        print("   Generated Prompt:")
        print("   " + "="*60)
        print(rendered_prompt)
        print("   " + "="*60)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Example 3: renderPrompt for different template types
    templates_to_test = [
        {
            "template_name": "mcp-analysis-prompt",
            "variables": {
                "analysis_type": "security_review",
                "target_code": "Authentication middleware implementation",
                "focus_areas": ["security", "performance", "maintainability"],
                "context": "Production e-commerce system",
                "urgency": "high",
                "include_recommendations": True
            }
        },
        {
            "template_name": "mcp-documentation-prompt",
            "variables": {
                "doc_type": "API documentation",
                "project_name": "User Management API",
                "target_audience": "frontend developers",
                "scope": "authentication and user management endpoints",
                "format": "OpenAPI/Swagger",
                "include_examples": True,
                "include_diagrams": True
            }
        },
        {
            "template_name": "mcp-testing-prompt",
            "variables": {
                "test_type": "integration tests",
                "code_to_test": "User authentication service with database integration",
                "testing_framework": "pytest",
                "language": "Python",
                "coverage_target": 95,
                "include_edge_cases": True,
                "include_performance_tests": True
            }
        }
    ]
    
    for i, config in enumerate(templates_to_test, 3):
        print(f"{i}. renderPrompt for {config['template_name']}:")
        print(f"   Variables: {json.dumps(config['variables'], indent=2)}")
        
        try:
            rendered_prompt = renderer.render_prompt(
                config["template_name"],
                config["variables"]
            )
            print("   ✓ Prompt rendered successfully!")
            print("   Generated Prompt (first 300 chars):")
            print("   " + "="*60)
            print(rendered_prompt[:300] + "..." if len(rendered_prompt) > 300 else rendered_prompt)
            print("   " + "="*60)
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print("\n" + "="*80 + "\n")
    
    # Example 4: renderPrompt with MCP database prompts
    print("6. renderPrompt with MCP Database Prompts:")
    mcp_prompts = renderer.list_mcp_prompts()
    if mcp_prompts:
        mcp_name = list(mcp_prompts.keys())[0]
        print(f"   Template: {mcp_name} (from MCP database)")
        print("   Variables: Default variables from MCP database")
        
        try:
            # Get default variables from MCP database
            mcp_prompt = mcp_prompts[mcp_name]
            default_vars = mcp_prompt.get('metadata', {}).get('variables', {})
            
            rendered_prompt = renderer.render_prompt(mcp_name, default_vars)
            print("   ✓ MCP prompt rendered successfully!")
            print("   Generated Prompt (first 300 chars):")
            print("   " + "="*60)
            print(rendered_prompt[:300] + "..." if len(rendered_prompt) > 300 else rendered_prompt)
            print("   " + "="*60)
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print("   ⚠ No MCP prompts available")
    
    print("\n" + "="*80 + "\n")
    
    # Example 5: renderPrompt error handling
    print("7. renderPrompt Error Handling:")
    print("   Template: non-existent-template")
    print("   Variables: {'test': 'value'}")
    
    try:
        rendered_prompt = renderer.render_prompt(
            "non-existent-template",
            {"test": "value"}
        )
        print("   ✓ Prompt rendered successfully!")
    except Exception as e:
        print(f"   ✓ Error handled correctly: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Example 6: Available templates
    print("8. Available Templates for renderPrompt:")
    templates = renderer.list_templates()
    mcp_prompts = renderer.list_mcp_prompts()
    
    print("   Local Templates:")
    for name, metadata in templates.items():
        print(f"     - {name}: {metadata.get('description', 'No description')}")
    
    print("   MCP Database Templates:")
    for name, prompt in mcp_prompts.items():
        metadata = prompt.get('metadata', {})
        print(f"     - {name}: {metadata.get('description', 'No description')}")
    
    print(f"\n   Total templates available: {len(templates) + len(mcp_prompts)}")
    
    print("\n=== renderPrompt Example Complete ===")

def demonstrate_json_api():
    """Demonstrate the JSON API format as specified in the user query."""
    
    print("\n=== JSON API Format Examples ===\n")
    
    # Example JSON API calls as specified in the user query
    examples = [
        {
            "description": "Basic renderPrompt usage",
            "json": {
                "template_name": "mcp-code-generator",
                "variables": {
                    "code_requirements": "Create a REST API with authentication",
                    "language": "Python"
                }
            }
        },
        {
            "description": "renderPrompt with analysis template",
            "json": {
                "template_name": "mcp-analysis-prompt",
                "variables": {
                    "analysis_type": "code_review",
                    "target_code": "Authentication middleware",
                    "focus_areas": ["security", "performance"],
                    "context": "Production system",
                    "urgency": "medium",
                    "include_recommendations": True
                }
            }
        },
        {
            "description": "renderPrompt with documentation template",
            "json": {
                "template_name": "mcp-documentation-prompt",
                "variables": {
                    "doc_type": "API documentation",
                    "project_name": "My Project",
                    "target_audience": "developers",
                    "scope": "complete system",
                    "format": "markdown",
                    "include_examples": True,
                    "include_diagrams": False
                }
            }
        }
    ]
    
    renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}:")
        print(f"   JSON Input: {json.dumps(example['json'], indent=2)}")
        
        try:
            rendered = renderer.render_prompt(
                example['json']['template_name'],
                example['json']['variables']
            )
            print("   ✓ Successfully rendered!")
            print("   Output (first 200 chars):")
            print(f"   {rendered[:200]}...")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()

if __name__ == "__main__":
    render_prompt_example()
    demonstrate_json_api()