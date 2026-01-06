#!/bin/bash
# Secondary Cursor Agent - Code execution and development
# Terminal ID: secondary
# Specialty: Code execution, development tasks, file operations

echo -e "\e[36m╔══════════════════════════════════════════════════════════╗\e[0m"
echo -e "\e[36m║             CURSOR AGENT - SECONDARY                    ║\e[0m"
echo -e "\e[36m║             Code Execution & Development                ║\e[0m"
echo -e "\e[36m╚══════════════════════════════════════════════════════════╝\e[0m"
echo ""

export AGENT_ID="secondary"
export AGENT_SPECIALTY="execution"
export AGENT_TERMINAL="secondary"

echo "Agent Secondary initialized. Specialty: $AGENT_SPECIALTY"
echo "Terminal: $AGENT_TERMINAL"
echo "Working Directory: $(pwd)"
echo ""
echo "Ready for MCP prompt instructions..."
echo "Specialized in: Code execution, file operations, development tasks"
echo ""

# Main agent loop
while true; do
    # Check for instructions
    if [ -f "/tmp/agent_secondary_instructions" ]; then
        echo -e "\e[33m[$(date)] New instruction received:\e[0m"
        INSTRUCTION=$(cat "/tmp/agent_secondary_instructions")
        echo "$INSTRUCTION"

        # Process different instruction types using MCP tools
        case "$INSTRUCTION" in
            *"create file"*|*"implement"*)
                echo -e "\e[32m[SECONDARY] Using MCP code generation tools...\e[0m"
                # Use filesystem tools to create files
                echo "def hello_world():" > test_file.py
                echo "    print('Hello from MCP-generated code')" >> test_file.py
                echo "    return 'success'" >> test_file.py
                ;;
            *"run command"*|*"execute"*)
                echo -e "\e[32m[SECONDARY] Using MCP execution tools...\e[0m"
                # Execute commands safely
                python3 -c "print('MCP execution test successful')"
                ;;
            *"git "*|*"version control"*)
                echo -e "\e[32m[SECONDARY] Using MCP Git management tools...\e[0m"
                # Use Git tools
                git status 2>/dev/null || echo "No git repository found"
                ;;
            *"debug"*|*"fix"*)
                echo -e "\e[32m[SECONDARY] Using MCP debugging tools...\e[0m"
                # Use debugging tools
                python3 -m py_compile test_file.py 2>/dev/null && echo "Syntax check passed" || echo "Syntax errors found"
                ;;
            *)
                echo -e "\e[32m[SECONDARY] Using general MCP development tools...\e[0m"
                # Use general development tools
                ls -la | head -5
                ;;
        esac

        rm "/tmp/agent_secondary_instructions"
        echo ""
    fi

    # Heartbeat
    echo -e "\e[34m[SECONDARY] $(date '+%H:%M:%S') - Ready for execution\e[0m"
    sleep 8
done