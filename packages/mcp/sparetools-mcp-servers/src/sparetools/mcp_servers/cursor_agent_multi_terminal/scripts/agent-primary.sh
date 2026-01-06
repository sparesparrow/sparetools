#!/bin/bash
# Primary Cursor Agent - Main coordination and planning
# Terminal ID: primary
# Specialty: Coordination, planning, high-level decisions

echo -e "\e[34m╔══════════════════════════════════════════════════════════╗\e[0m"
echo -e "\e[34m║              CURSOR AGENT - PRIMARY                     ║\e[0m"
echo -e "\e[34m║              Coordination & Planning                    ║\e[0m"
echo -e "\e[34m╚══════════════════════════════════════════════════════════╝\e[0m"
echo ""

export AGENT_ID="primary"
export AGENT_SPECIALTY="coordination"
export AGENT_TERMINAL="primary"

echo "Agent Primary initialized. Specialty: $AGENT_SPECIALTY"
echo "Terminal: $AGENT_TERMINAL"
echo "Working Directory: $(pwd)"
echo ""
echo "Ready for MCP prompt instructions..."
echo "Use 'ca primary <command>' from other terminals to send instructions"
echo ""

# Main agent loop - wait for MCP instructions
while true; do
    # Check for new instructions via file
    if [ -f "/tmp/agent_primary_instructions" ]; then
        echo -e "\e[33m[$(date)] New instruction received:\e[0m"
        INSTRUCTION=$(cat "/tmp/agent_primary_instructions")

        # Use MCP prompts to process the instruction systematically
        echo "Processing via MCP: $INSTRUCTION"

        # Apply coordination template
        echo "Applying MCP coordination template..."
        mcp-coord primary "$INSTRUCTION"

        # Use MCP tools for coordination tasks
        case "$INSTRUCTION" in
            *"analyze"*|*"plan"*|*"coordinate"*)
                echo -e "\e[32m[PRIMARY] Using MCP analysis tools for coordination\e[0m"
                # Use filesystem tools to analyze project structure
                find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -10
                ;;
            *"create"*|*"design"*)
                echo -e "\e[32m[PRIMARY] Using MCP design templates\e[0m"
                # Use code generation tools
                echo "Generating project structure..."
                ;;
            *"workflow"*|*"orchestrate"*)
                echo -e "\e[32m[PRIMARY] Coordinating multi-agent workflow\e[0m"
                # Send instructions to other agents
                echo "coordination_plan" > /tmp/agent_secondary_instructions
                echo "analysis_request" > /tmp/agent_research_instructions
                echo "deployment_prep" > /tmp/agent_execution_instructions
                ;;
            *)
                echo -e "\e[32m[PRIMARY] Processing general coordination task\e[0m"
                ;;
        esac

        rm "/tmp/agent_primary_instructions"
        echo ""
    fi

    # Heartbeat
    echo -e "\e[32m[PRIMARY] $(date '+%H:%M:%S') - Agent active, ready for MCP coordination\e[0m"
    sleep 10
done