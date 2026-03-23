# Cursor Multi-Agent System

SpareTools includes a four-agent coordination system for Cursor IDE, implemented as an MCP server.
It lets you orchestrate parallel development workflows directly from the Cursor AI chat interface.

## Agents

| Agent | Specialty | Typical Tasks |
|-------|-----------|---------------|
| **Primary** | Coordination & Planning | Break down tasks, assign work, track progress |
| **Secondary** | Code Execution & Development | Write code, run tests, fix bugs |
| **Research** | Analysis & Information Gathering | Search codebase, read docs, gather context |
| **Execution** | System Operations & Deployment | Build packages, run CI, deploy to Cloudsmith |

Communication between agents uses file-based messaging (`~/.sparetools/agents/`), allowing
each agent to run in its own terminal while sharing a common task queue.

## Setup

### 1. Install and configure

```bash
# Install all MCP packages
./scripts/setup-mcp-dev.sh

# Verify Cursor config was written
cat ~/.cursor/mcp.json | python3 -m json.tool
```

The setup script writes `~/.cursor/mcp.json` with all SpareTools servers, including
`cursor-agent-multi-terminal`.

### 2. Restart Cursor

After running setup, restart Cursor IDE. The agent system will appear as tools in the
Cursor MCP panel.

## Available MCP Tools

### `launch_multi_agent_environment`

Opens four coordinated terminals using Terminator (Linux) or iTerm2 (macOS), one per agent.

```
Tool: launch_multi_agent_environment
Args: none
```

### `send_agent_instruction`

Send a direct instruction to a specific agent.

```
Tool: send_agent_instruction
Args:
  agent       - "primary" | "secondary" | "research" | "execution"
  instruction - The task description for that agent
```

### `coordinate_development_workflow`

High-level workflow: describe a task and the Primary agent decomposes it,
assigning subtasks to the appropriate agents.

```
Tool: coordinate_development_workflow
Args:
  task_description - Full description of the development task
```

**Example prompt in Cursor:**
```
Use coordinate_development_workflow to add FIPS 140-3 validation to sparetools-crypto-suite.
```

### `apply_mcp_template`

Apply a predefined MCP prompt template for a common workflow.

```
Tool: apply_mcp_template
Args:
  agent  - Target agent
  task   - Template task name (e.g. "code_review", "build_package", "security_scan")
```

### `get_agent_status`

Check the current status of all four agents.

```
Tool: get_agent_status
Args: none
```

### `get_mcp_usage_guide`

Return the full usage guide for the multi-agent system.

```
Tool: get_mcp_usage_guide
Args: none
```

## Workflow Examples

### Parallel feature implementation

```
1. coordinate_development_workflow("Implement GitHub API tools in repo cleanup server")
   → Primary decomposes into:
     - Research: read existing server code, find integration points
     - Secondary: write github_manager.py tool
     - Execution: run tests, validate with flake8
     - Primary: review and merge
```

### Full CI workflow on a package

```
1. send_agent_instruction("execution", "Run full CI workflow on packages/mcp/sparetools-mcp-core")
2. send_agent_instruction("research", "Analyze any test failures and find root cause")
3. send_agent_instruction("secondary", "Fix the identified issues")
4. send_agent_instruction("execution", "Re-run tests and create a commit")
```

### New package bootstrap

```
1. coordinate_development_workflow(
     "Bootstrap new 'sparetools-ai-gateway' package in category 'mcp',
      version 1.0.0, with Anthropic and OpenAI backend support"
   )
```

## Agent Scripts

Each agent has a corresponding launch script under:
```
packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers/cursor_agent_multi_terminal/scripts/
  agent-primary.sh
  agent-secondary.sh
  agent-research.sh
  agent-execution.sh
  launch-multi-agent.sh
```

These scripts open Claude Code (or any configured shell) pre-loaded with the agent's
system prompt and file-messaging hooks.

## Prompt Templates

Prompt templates for common workflows are stored under:
```
packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers/cursor_agent_multi_terminal/prompts/
```

Use `apply_mcp_template` to load them or reference them directly in Cursor chat.

## Integration with Other Servers

The multi-agent system can invoke any other SpareTools MCP server tool by delegation.
For example, the Execution agent can call:
- `run_full_ci_workflow` from `sparetools-orchestrator`
- `create_conan_package` from `sparetools-conan`
- `repo_cleanup_scan` from `sparetools-repo`

## Troubleshooting

**Agents not appearing in Cursor:**
```bash
cat ~/.cursor/mcp.json   # verify config is present
# Restart Cursor
```

**Agent messaging not working:**
```bash
ls ~/.sparetools/agents/   # check message directory exists
mkdir -p ~/.sparetools/agents/
```

**Terminator not found (Linux):**
```bash
sudo apt install terminator
# or use tmux variant by editing scripts/launch-multi-agent.sh
```
