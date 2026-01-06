#!/bin/bash
# MCP Agent Coordinator
# Uses MCP prompts to coordinate between cursor agents

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_DIR="$(dirname "$SCRIPT_DIR")/prompts"

# Function to apply MCP prompt template
apply_mcp_prompt() {
    local agent="$1"
    local instruction="$2"
    local template_file="$PROMPT_DIR/agent-communication-template"

    if [ ! -f "$template_file" ]; then
        echo "Error: Template file not found: $template_file"
        return 1
    fi

    # Get agent information
    case "$agent" in
        primary)
            specialty="coordination"
            color_scheme="blue"
            ;;
        secondary)
            specialty="execution"
            color_scheme="cyan"
            ;;
        research)
            specialty="analysis"
            color_scheme="magenta"
            ;;
        execution)
            specialty="operations"
            color_scheme="red"
            ;;
        *)
            echo "Unknown agent: $agent"
            return 1
            ;;
    esac

    # Apply template variables
    sed \
        -e "s/{agent_id}/$agent/g" \
        -e "s/{specialty}/$specialty/g" \
        -e "s/{terminal_id}/$agent/g" \
        -e "s/{working_directory}/$(pwd)/g" \
        -e "s/{color_scheme}/$color_scheme/g" \
        -e "s/{current_task}/$instruction/g" \
        -e "s/{instruction}/$instruction/g" \
        "$template_file"
}

# Function to send instruction to agent
send_to_agent() {
    local agent="$1"
    local instruction="$2"

    echo "Sending to $agent agent: $instruction"

    # Generate the full prompt
    local full_prompt=$(apply_mcp_prompt "$agent" "$instruction")

    # Send via command injection
    "$SCRIPT_DIR/ca-command.sh" "$agent" "$full_prompt"

    # Wait a bit for processing
    sleep 2

    echo "Instruction sent. Check agent terminal for response."
}

# Main coordination logic
case "$1" in
    "send")
        send_to_agent "$2" "$3"
        ;;
    "test")
        echo "Testing MCP agent coordination..."
        send_to_agent "primary" "Initialize coordination system"
        sleep 3
        send_to_agent "secondary" "Check system status"
        sleep 3
        send_to_agent "research" "Analyze current environment"
        sleep 3
        send_to_agent "execution" "Report system health"
        ;;
    "workflow")
        echo "Starting development workflow..."
        send_to_agent "research" "Analyze project requirements"
        sleep 5
        send_to_agent "primary" "Create development plan"
        sleep 5
        send_to_agent "secondary" "Implement core functionality"
        sleep 5
        send_to_agent "execution" "Deploy and test system"
        ;;
    *)
        echo "Usage: $0 <command> [args]"
        echo "Commands:"
        echo "  send <agent> <instruction>  - Send instruction to specific agent"
        echo "  test                        - Run coordination test"
        echo "  workflow                    - Start development workflow"
        ;;
esac