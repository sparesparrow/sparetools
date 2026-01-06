#!/bin/bash
# Simple MCP Agent Coordinator
# Demonstrates MCP prompt template application

AGENT="$1"
INSTRUCTION="$2"

if [ -z "$AGENT" ] || [ -z "$INSTRUCTION" ]; then
    echo "Usage: $0 <agent> \"<instruction>\""
    echo "Agents: primary, secondary, research, execution"
    exit 1
fi

# Get agent specialty
case "$AGENT" in
    primary)
        SPECIALTY="coordination"
        COLOR="blue"
        ;;
    secondary)
        SPECIALTY="execution"
        COLOR="cyan"
        ;;
    research)
        SPECIALTY="analysis"
        COLOR="magenta"
        ;;
    execution)
        SPECIALTY="operations"
        COLOR="red"
        ;;
    *)
        echo "Unknown agent: $AGENT"
        exit 1
        ;;
esac

# Create MCP prompt
cat << EOF
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP PROMPT TEMPLATE                               │
│                          Agent: $AGENT (ID: ${AGENT})                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Specialty: $SPECIALTY                                                       │
│ Terminal: $AGENT                                                            │
│ Color Scheme: $COLOR                                                        │
│ Working Directory: $(pwd)                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ INSTRUCTION: $INSTRUCTION                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Response Protocol:                                                          │
│ 1. Acknowledge instruction                                                  │
│ 2. Execute requested action using available tools                          │
│ 3. Report results clearly                                                   │
│ 4. Suggest next steps if applicable                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Available Tools: filesystem, code analysis, MCP integration, system ops    │
└─────────────────────────────────────────────────────────────────────────────┘

EXECUTE: $INSTRUCTION
EOF

# Send to agent via command injection
echo "Sending MCP prompt to $AGENT agent..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/ca-command.sh" "$AGENT" "MCP_PROMPT: $INSTRUCTION"

echo "MCP prompt sent successfully to $AGENT agent."

# Apply MCP tools based on agent specialty
case "$AGENT" in
    primary)
        echo "Applied coordination MCP tools for planning and orchestration"
        ;;
    secondary)
        echo "Applied development MCP tools for code execution and file operations"
        ;;
    research)
        echo "Applied analysis MCP tools for research and validation"
        ;;
    execution)
        echo "Applied operations MCP tools for deployment and monitoring"
        ;;
esac

# Log the MCP interaction for improvement tracking
LOG_FILE="/tmp/mcp_cursor_agent_interactions.log"
echo "$(date): $AGENT <- MCP_PROMPT: $INSTRUCTION" >> "$LOG_FILE"