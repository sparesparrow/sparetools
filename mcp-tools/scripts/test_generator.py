#!/usr/bin/env python3
"""
Test script for the Mermaid Diagram Generator
"""

from diagram_generator import DiagramGenerator
import json

def test_basic_functionality():
    """Test basic diagram generation functionality."""
    print("Testing Mermaid Diagram Generator...")
    
    # Initialize generator
    generator = DiagramGenerator("diagram_templates")
    
    # Test 1: List templates
    print("\n1. Testing template listing...")
    templates = generator.list_templates()
    print(f"Found {len(templates)} templates:")
    for name, metadata in templates.items():
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Test 2: Generate simple flowchart
    print("\n2. Testing flowchart generation...")
    try:
        flowchart = generator.generate_diagram(
            "flowchart-template",
            {
                "title": "Test Process",
                "steps": ["Start", "Process", "End"],
                "connections": [
                    {"from": "Start", "to": "Process", "label": ""},
                    {"from": "Process", "to": "End", "label": ""}
                ]
            }
        )
        print("✓ Flowchart generated successfully")
        print("Generated Mermaid code:")
        print(flowchart)
    except Exception as e:
        print(f"✗ Error generating flowchart: {e}")
    
    # Test 3: Generate sequence diagram
    print("\n3. Testing sequence diagram generation...")
    try:
        sequence = generator.generate_diagram(
            "sequence-template",
            {
                "title": "Test Interaction",
                "actors": ["A", "B"],
                "interactions": [
                    {"from": "A", "to": "B", "message": "Hello", "type": "solid"},
                    {"from": "B", "to": "A", "message": "Hi", "type": "dashed"}
                ]
            }
        )
        print("✓ Sequence diagram generated successfully")
        print("Generated Mermaid code:")
        print(sequence)
    except Exception as e:
        print(f"✗ Error generating sequence diagram: {e}")
    
    # Test 4: Test configuration loading
    print("\n4. Testing configuration loading...")
    try:
        with open("config/diagram_configs.json", 'r') as f:
            configs = json.load(f)
        print(f"✓ Loaded {len(configs)} configuration categories")
        
        # Test one example from config
        if "flowchart_examples" in configs:
            example = configs["flowchart_examples"]["simple_process"]
            diagram = generator.generate_diagram(
                example["template_name"],
                example["variables"]
            )
            print("✓ Configuration-based diagram generated successfully")
    except Exception as e:
        print(f"✗ Error with configuration: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_basic_functionality()