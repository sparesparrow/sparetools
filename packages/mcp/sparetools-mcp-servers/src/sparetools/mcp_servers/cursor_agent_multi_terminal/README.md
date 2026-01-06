# Cursor Agent Multi-Terminal MCP Server

A Model Context Protocol (MCP) server that provides a multi-agent cursor environment for coordinated development workflows. This server enables systematic AI-assisted development through specialized cursor agents running in separate terminals.

## Overview

This MCP server creates and manages a multi-agent development environment with four specialized cursor agents:

- **🔵 Primary Agent**: Coordination & Planning
- **🔷 Secondary Agent**: Code Execution & Development
- **🟣 Research Agent**: Analysis & Information Gathering
- **🔴 Execution Agent**: System Operations & Deployment

## Features

### Multi-Agent Coordination
- **File-based messaging** between agents
- **MCP prompt templates** for systematic communication
- **Real-time coordination** via command injection
- **Terminal-agnostic design** (works in any console session)

### MCP Integration
- **Structured prompt templates** for agent instructions
- **Systematic tool usage** across all agents
- **Result verification** and improvement tracking
- **Workflow orchestration** for complete development cycles

### Development Workflows
- **Individual agent commands** for specific tasks
- **Coordinated workflows** for complete feature development
- **Status monitoring** and agent health checks
- **Session management** and persistence

## Installation

### From SpareTools Repository
```bash
cd packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers/cursor_agent_multi_terminal
pip install -e .
```

### Direct Installation
```bash
git clone <repository>
cd cursor-agent-multi-terminal
pip install -e .
```

## MCP Server Registration

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "cursor-agent-multi-terminal": {
      "command": "cursor-agent-multi-terminal"
    }
  }
}
```

## Usage

### Launch Multi-Agent Environment
```python
# Launch the complete environment
result = await mcp.call_tool("launch_multi_agent_environment", {})
print(result)  # "Multi-agent cursor environment launched successfully"
```

### Send Agent Instructions
```python
# Direct instruction to specific agent
result = await mcp.call_tool("send_agent_instruction", {
    "agent": "primary",
    "instruction": "Analyze project structure and create development plan"
})
```

### Apply MCP Templates
```python
# Systematic instruction using MCP templates
result = await mcp.call_tool("apply_mcp_template", {
    "agent": "secondary",
    "task": "Implement user authentication system"
})
```

### Coordinated Workflows
```python
# Complete development workflow
result = await mcp.call_tool("coordinate_development_workflow", {
    "task_description": "Build a REST API with authentication"
})
```

### Monitor Agent Status
```python
# Check all agent statuses
result = await mcp.call_tool("get_agent_status", {})
print(result)  # Shows status of all 4 agents
```

## Agent Specialties

### Primary Agent (Coordination & Planning)
- **High-level planning** and architecture decisions
- **Task coordination** between other agents
- **Workflow orchestration** and milestone tracking
- **Resource allocation** and priority management

### Secondary Agent (Code Execution & Development)
- **Code writing** and implementation
- **File operations** and modifications
- **Development tasks** and debugging
- **Code refactoring** and optimization

### Research Agent (Analysis & Information Gathering)
- **Code analysis** and quality assessment
- **Testing and validation** frameworks
- **Documentation generation** and research
- **Security analysis** and vulnerability assessment

### Execution Agent (System Operations & Deployment)
- **System configuration** and setup
- **Deployment orchestration** and monitoring
- **Infrastructure management** and scaling
- **Operations automation** and maintenance

## MCP Prompt System

The server uses structured MCP prompt templates for systematic agent coordination:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP PROMPT TEMPLATE                               │
│                          Agent: primary (ID: primary)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Specialty: coordination                                                   │
│ Terminal: primary                                                          │
│ Color Scheme: blue                                                         │
│ Working Directory: /current/path                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ INSTRUCTION: [specific task instruction]                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Response Protocol: [structured response format]                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Development Workflow Example

```python
import mcp

# Initialize development of a new feature
await mcp.call_tool("coordinate_development_workflow", {
    "task_description": "Implement user registration and authentication system"
})

# This triggers:
# 1. Primary: Analyze requirements and create plan
# 2. Research: Gather security best practices and research libraries
# 3. Secondary: Implement authentication logic and database models
# 4. Research: Create comprehensive tests and validate implementation
# 5. Execution: Deploy to staging and configure monitoring
```

## Configuration

### Environment Requirements
- **Terminator** terminal emulator
- **xdotool** for automation
- **Graphical environment** support (X11/Wayland)
- **Python 3.8+** with MCP support

### Console Session Note
This environment is designed to run in console sessions (tty1-tty6) rather than being bound to a specific terminal. Users should run their own graphical environment that supports the required tools.

## Architecture

### Communication System
- **File-based messaging**: `/tmp/agent_{agent_id}_instructions`
- **Command injection**: Via `ca` command system
- **Status monitoring**: Real-time agent health checks
- **Session persistence**: Configuration and state management

### MCP Integration
- **Prompt templates**: Structured instruction formatting
- **Tool coordination**: Systematic use of available tools
- **Result tracking**: Performance monitoring and improvement
- **Workflow automation**: Multi-step process orchestration

## Troubleshooting

### Environment Not Launching
```bash
# Check terminator installation
which terminator

# Verify display availability
echo $DISPLAY

# Test manual launch
terminator --config /path/to/config
```

### Agent Communication Issues
```bash
# Check instruction files
ls /tmp/agent_*_instructions

# Verify script permissions
ls -la scripts/*.sh

# Test manual command injection
./scripts/ca-command.sh primary "test instruction"
```

### MCP Tool Errors
```bash
# Verify MCP server registration
cat ~/.mcp.json

# Check Python dependencies
pip list | grep mcp

# Test individual tools
python3 -c "import mcp; print('MCP available')"
```

## Contributing

### Adding New Agents
1. Create agent script in `scripts/agent-{name}.sh`
2. Add agent definition to `AGENTS` dict in MCP server
3. Update terminator config with new layout
4. Add agent specialty handling in coordination logic

### Extending MCP Tools
1. Add new tool function with `@server.tool()` decorator
2. Implement tool logic using available system capabilities
3. Update documentation and usage examples
4. Test tool functionality with MCP client

### Improving Prompt Templates
1. Analyze current template effectiveness
2. Update template structure in prompt files
3. Test improved templates with various tasks
4. Document template improvements and results

## License

Part of the SpareTools project. See main repository for licensing information.