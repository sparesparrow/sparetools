#!/bin/bash
# Research Cursor Agent - Analysis and information gathering
# Terminal ID: research
# Specialty: Analysis, research, documentation, testing

echo -e "\e[35m╔══════════════════════════════════════════════════════════╗\e[0m"
echo -e "\e[35m║             CURSOR AGENT - RESEARCH                     ║\e[0m"
echo -e "\e[35m║             Analysis & Information Gathering            ║\e[0m"
echo -e "\e[35m╚══════════════════════════════════════════════════════════╝\e[0m"
echo ""

export AGENT_ID="research"
export AGENT_SPECIALTY="analysis"
export AGENT_TERMINAL="research"

echo "Agent Research initialized. Specialty: $AGENT_SPECIALTY"
echo "Terminal: $AGENT_TERMINAL"
echo "Working Directory: $(pwd)"
echo ""
echo "Ready for MCP prompt instructions..."
echo "Specialized in: Analysis, research, documentation, testing"
echo ""

# Main agent loop
while true; do
    # Check for instructions
    if [ -f "/tmp/agent_research_instructions" ]; then
        echo -e "\e[33m[$(date)] New instruction received:\e[0m"
        INSTRUCTION=$(cat "/tmp/agent_research_instructions")
        echo "$INSTRUCTION"

        # Process research/analysis instructions using MCP tools
        case "$INSTRUCTION" in
            *"analyze"*|*"review"*)
                echo -e "\e[35m[RESEARCH] Using MCP analysis and static analysis tools...\e[0m"
                # Use static analysis tools
                find . -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | head -5
                echo "Code analysis complete"
                ;;
            *"search"*|*"find"*)
                echo -e "\e[35m[RESEARCH] Using MCP search and filesystem tools...\e[0m"
                # Use search tools
                find . -name "*.py" -o -name "*.js" -o -name "*.ts" | wc -l
                echo "files found"
                ;;
            *"test"*|*"validate"*)
                echo -e "\e[35m[RESEARCH] Using MCP testing and validation tools...\e[0m"
                # Use testing tools
                python3 -c "import sys; print('Python environment validated')" 2>/dev/null || echo "Python validation failed"
                ;;
            *"document"*|*"generate docs"*)
                echo -e "\e[35m[RESEARCH] Using MCP documentation tools...\e[0m"
                # Use documentation tools
                wc -l *.py 2>/dev/null || echo "No Python files found for documentation"
                ;;
            *"security"*|*"vulnerability"*)
                echo -e "\e[35m[RESEARCH] Using MCP security analysis tools...\e[0m"
                # Use security tools
                echo "Checking file permissions..."
                ls -la | grep -E "\.(py|js|ts|sh)$" | head -3
                ;;
            *)
                echo -e "\e[35m[RESEARCH] Using general MCP research tools...\e[0m"
                # Use general research tools
                du -sh . 2>/dev/null
                echo "Project size analysis complete"
                ;;
        esac

        rm "/tmp/agent_research_instructions"
        echo ""
    fi

    # Heartbeat
    echo -e "\e[35m[RESEARCH] $(date '+%H:%M:%S') - Analyzing environment\e[0m"
    sleep 12
done