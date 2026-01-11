#!/bin/bash
# Cursor Agent Command Injection System
# Usage: ca <agent> "<command>"

AGENT="$1"
COMMAND="$2"

if [ -z "$AGENT" ] || [ -z "$COMMAND" ]; then
    echo -e "\e[31mUsage: ca <agent> \"<command>\"\e[0m"
    echo "Available agents:"
    echo "  primary   - Coordination & Planning"
    echo "  secondary - Code Execution & Development"
    echo "  research  - Analysis & Information Gathering"
    echo "  execution - System Operations & Deployment"
    exit 1
fi

# Validate agent name
case "$AGENT" in
    primary|secondary|research|execution)
        ;;
    *)
        echo -e "\e[31mInvalid agent: $AGENT\e[0m"
        echo "Available agents: primary, secondary, research, execution"
        exit 1
        ;;
esac

# Send command to agent via file
INSTRUCTION_FILE="/tmp/agent_${AGENT}_instructions"
echo "$COMMAND" > "$INSTRUCTION_FILE"

echo -e "\e[32m✓ Command sent to $AGENT agent:\e[0m $COMMAND"

# Optional: Log the command
LOG_FILE="/tmp/cursor_agent_commands.log"
echo "$(date): $AGENT <- $COMMAND" >> "$LOG_FILE"