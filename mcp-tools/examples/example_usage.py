#!/usr/bin/env python3
"""
Example usage of the Mermaid Diagram Generator

This script demonstrates how to use the DiagramGenerator class
to create various types of diagrams from templates.
"""

import json
from pathlib import Path
from diagram_generator import DiagramGenerator

def main():
    """Demonstrate various diagram generation examples."""
    
    # Initialize the generator
    generator = DiagramGenerator("diagram_templates")
    
    # Load example configurations
    config_file = Path("config/diagram_configs.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            examples = json.load(f)
    else:
        print("Configuration file not found. Using basic examples.")
        examples = {}
    
    print("=== Mermaid Diagram Generator Examples ===\n")
    
    # Example 1: Simple Flowchart
    print("1. Generating Simple Flowchart...")
    try:
        flowchart_code = generator.generate_diagram(
            "flowchart-template",
            {
                "title": "User Login Process",
                "steps": ["Start", "Enter Credentials", "Validate", "Access Granted", "End"],
                "connections": [
                    {"from": "Start", "to": "Enter Credentials", "label": ""},
                    {"from": "Enter Credentials", "to": "Validate", "label": ""},
                    {"from": "Validate", "to": "Access Granted", "label": "Valid"},
                    {"from": "Validate", "to": "Enter Credentials", "label": "Invalid"},
                    {"from": "Access Granted", "to": "End", "label": ""}
                ]
            }
        )
        print("✓ Flowchart generated successfully")
        print("Mermaid Code:")
        print(flowchart_code)
        print()
    except Exception as e:
        print(f"✗ Error generating flowchart: {e}")
    
    # Example 2: Sequence Diagram
    print("2. Generating Sequence Diagram...")
    try:
        sequence_code = generator.generate_diagram(
            "sequence-template",
            {
                "title": "User Authentication Flow",
                "actors": ["User", "Web App", "Auth Service", "Database"],
                "interactions": [
                    {"from": "User", "to": "Web App", "message": "Login Request", "type": "solid"},
                    {"from": "Web App", "to": "Auth Service", "message": "Validate Credentials", "type": "solid"},
                    {"from": "Auth Service", "to": "Database", "message": "Check User", "type": "solid"},
                    {"from": "Database", "to": "Auth Service", "message": "User Data", "type": "dashed"},
                    {"from": "Auth Service", "to": "Web App", "message": "Token", "type": "dashed"},
                    {"from": "Web App", "to": "User", "message": "Success", "type": "solid"}
                ]
            }
        )
        print("✓ Sequence diagram generated successfully")
        print("Mermaid Code:")
        print(sequence_code)
        print()
    except Exception as e:
        print(f"✗ Error generating sequence diagram: {e}")
    
    # Example 3: Class Diagram
    print("3. Generating Class Diagram...")
    try:
        class_code = generator.generate_diagram(
            "class-template",
            {
                "title": "E-commerce System",
                "classes": [
                    {
                        "name": "Product",
                        "methods": ["+getName()", "+getPrice()", "+getDescription()"],
                        "attributes": ["-id: int", "-name: String", "-price: double"]
                    },
                    {
                        "name": "Cart",
                        "methods": ["+addItem()", "+removeItem()", "+getTotal()"],
                        "attributes": ["-items: List<Product>", "-total: double"]
                    },
                    {
                        "name": "Order",
                        "methods": ["+process()", "+getStatus()"],
                        "attributes": ["-orderId: String", "-items: List<Product>", "-status: OrderStatus"]
                    }
                ],
                "relationships": [
                    {"from": "Cart", "to": "Product", "type": "uses", "label": "contains"},
                    {"from": "Order", "to": "Product", "type": "uses", "label": "includes"},
                    {"from": "Order", "to": "Cart", "type": "uses", "label": "created from"}
                ]
            }
        )
        print("✓ Class diagram generated successfully")
        print("Mermaid Code:")
        print(class_code)
        print()
    except Exception as e:
        print(f"✗ Error generating class diagram: {e}")
    
    # Example 4: State Diagram
    print("4. Generating State Diagram...")
    try:
        state_code = generator.generate_diagram(
            "state-template",
            {
                "title": "Order Lifecycle",
                "states": ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"],
                "transitions": [
                    {"from": "Pending", "to": "Confirmed", "trigger": "payment", "condition": "payment_valid"},
                    {"from": "Confirmed", "to": "Shipped", "trigger": "ship", "condition": "inventory_ready"},
                    {"from": "Shipped", "to": "Delivered", "trigger": "deliver", "condition": "delivery_success"},
                    {"from": "Pending", "to": "Cancelled", "trigger": "cancel", "condition": "cancellation_allowed"}
                ]
            }
        )
        print("✓ State diagram generated successfully")
        print("Mermaid Code:")
        print(state_code)
        print()
    except Exception as e:
        print(f"✗ Error generating state diagram: {e}")
    
    # Example 5: Gantt Chart
    print("5. Generating Gantt Chart...")
    try:
        gantt_code = generator.generate_diagram(
            "gantt-template",
            {
                "title": "Project Timeline",
                "tasks": [
                    {"name": "Planning", "start": "2024-01-01", "end": "2024-01-14", "status": "done"},
                    {"name": "Development", "start": "2024-01-15", "end": "2024-02-15", "status": "active"},
                    {"name": "Testing", "start": "2024-02-16", "end": "2024-02-28", "status": "pending"},
                    {"name": "Deployment", "start": "2024-03-01", "end": "2024-03-07", "status": "pending"}
                ]
            }
        )
        print("✓ Gantt chart generated successfully")
        print("Mermaid Code:")
        print(gantt_code)
        print()
    except Exception as e:
        print(f"✗ Error generating Gantt chart: {e}")
    
    # Example 6: Pie Chart
    print("6. Generating Pie Chart...")
    try:
        pie_code = generator.generate_diagram(
            "pie-template",
            {
                "title": "Project Time Distribution",
                "data": [
                    {"label": "Development", "value": 40},
                    {"label": "Testing", "value": 25},
                    {"label": "Documentation", "value": 15},
                    {"label": "Meetings", "value": 10},
                    {"label": "Other", "value": 10}
                ]
            }
        )
        print("✓ Pie chart generated successfully")
        print("Mermaid Code:")
        print(pie_code)
        print()
    except Exception as e:
        print(f"✗ Error generating pie chart: {e}")
    
    # Example 7: Mind Map
    print("7. Generating Mind Map...")
    try:
        mindmap_code = generator.generate_diagram(
            "mindmap-template",
            {
                "title": "Software Architecture",
                "branches": [
                    {
                        "name": "Frontend",
                        "subbranches": ["React", "Vue", "Angular", "Svelte"]
                    },
                    {
                        "name": "Backend",
                        "subbranches": ["Node.js", "Python", "Java", "Go"]
                    },
                    {
                        "name": "Database",
                        "subbranches": ["PostgreSQL", "MongoDB", "Redis", "MySQL"]
                    },
                    {
                        "name": "DevOps",
                        "subbranches": ["Docker", "Kubernetes", "AWS", "CI/CD"]
                    }
                ]
            }
        )
        print("✓ Mind map generated successfully")
        print("Mermaid Code:")
        print(mindmap_code)
        print()
    except Exception as e:
        print(f"✗ Error generating mind map: {e}")
    
    # List available templates
    print("8. Available Templates:")
    templates = generator.list_templates()
    for name, metadata in templates.items():
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    print("\n=== Examples Complete ===")

if __name__ == "__main__":
    main()