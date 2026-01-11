#!/usr/bin/env python3
"""
Script to create commands for MCP prompts that integrate with workspace tools
"""

import json

# Define commands for each prompt that combine MCP tools with workspace context
prompt_commands = {
    "code_review_assistant": {
        "command": "Integrate filesystem access to read local code files, use mermaid diagrams to visualize code structure, combine with network monitoring for security analysis, and leverage project orchestration for comprehensive code review in the Kali Linux security environment.",
        "workspace_integration": "Access local security scripts, penetration testing tools, and network monitoring utilities; generate architecture diagrams of attack frameworks; review code for security vulnerabilities in the context of offensive security tools.",
        "mcp_tools_used": ["filesystem", "mermaid", "project_orchestrator", "sequential_thinking"],
        "usage_context": "Use when reviewing security tools, penetration testing scripts, or network monitoring utilities in the Kali Linux environment"
    },

    "documentation_writer": {
        "command": "Use filesystem to access project files and scripts, mermaid diagrams to create system architecture visualizations, project orchestration to understand component relationships, and combine with workspace security documentation patterns.",
        "workspace_integration": "Document security tools, network monitoring setups, attack frameworks, and penetration testing methodologies; generate visual diagrams of Kali Linux toolchains and attack workflows.",
        "mcp_tools_used": ["filesystem", "mermaid", "project_orchestrator", "prompt_manager"],
        "usage_context": "Create documentation for security tools, network monitoring systems, or penetration testing procedures in the offensive security workspace"
    },

    "bug_analyzer": {
        "command": "Leverage filesystem to examine error logs and configuration files, use sequential thinking for root cause analysis, integrate with network monitoring data, and generate mermaid diagrams to visualize bug relationships.",
        "workspace_integration": "Analyze bugs in security scripts, network monitoring tools, or attack frameworks; examine packet capture data, system logs, and penetration testing tool outputs for debugging.",
        "mcp_tools_used": ["filesystem", "sequential_thinking", "mermaid", "prompt_manager"],
        "usage_context": "Debug security tools, network monitoring issues, or penetration testing framework problems in the Kali Linux environment"
    },

    "architecture_reviewer": {
        "command": "Use filesystem to examine project structure, mermaid diagrams for architecture visualization, project orchestration for component analysis, and sequential thinking for scalability assessment.",
        "workspace_integration": "Review architectures of security frameworks, network monitoring systems, and attack toolchains; assess scalability of penetration testing setups and monitoring dashboards.",
        "mcp_tools_used": ["filesystem", "mermaid", "project_orchestrator", "sequential_thinking"],
        "usage_context": "Review system architectures for security tools, network monitoring platforms, or penetration testing frameworks"
    },

    "test_case_generator": {
        "command": "Access filesystem for existing test patterns, use project orchestration to understand system components, generate mermaid diagrams for test coverage visualization, and apply sequential thinking for comprehensive test strategy.",
        "workspace_integration": "Generate test cases for security tools, network monitoring utilities, and attack frameworks; create tests for packet analysis, vulnerability scanning, and penetration testing workflows.",
        "mcp_tools_used": ["filesystem", "project_orchestrator", "mermaid", "sequential_thinking"],
        "usage_context": "Generate test cases for security scripts, network monitoring tools, and penetration testing utilities in the Kali Linux environment"
    }
}

def create_command_definitions():
    """Create command definitions for each prompt"""

    commands_output = []

    for prompt_id, command_data in prompt_commands.items():
        command_def = {
            "prompt_id": prompt_id,
            "command": command_data["command"],
            "workspace_integration": command_data["workspace_integration"],
            "mcp_tools_used": command_data["mcp_tools_used"],
            "usage_context": command_data["usage_context"],
            "workspace_context": "Kali Linux security environment with network monitoring, screen casting, and penetration testing tools"
        }
        commands_output.append(command_def)

    return commands_output

def save_commands_to_file(commands):
    """Save command definitions to a JSON file"""
    with open('prompt_commands.json', 'w') as f:
        json.dump(commands, f, indent=2)
    print("✅ Command definitions saved to prompt_commands.json")

if __name__ == "__main__":
    print("🔧 Creating MCP prompt commands for workspace integration...")
    commands = create_command_definitions()
    save_commands_to_file(commands)

    print(f"\n📋 Generated commands for {len(commands)} prompts:")
    for cmd in commands:
        print(f"  • {cmd['prompt_id']}: {cmd['usage_context'][:60]}...")

    print("\n🎯 Commands integrate MCP tools with:")
    print("  • Kali Linux security environment")
    print("  • Network monitoring and packet analysis")
    print("  • Screen casting and DLNA streaming")
    print("  • Penetration testing frameworks")
    print("  • Security tool development and debugging")