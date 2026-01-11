#!/bin/bash
# Multi-Agent Cursor Environment Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")")"

# Colors
RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
MAGENTA='\e[35m'
CYAN='\e[36m'
WHITE='\e[37m'
NC='\e[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                 MULTI-AGENT CURSOR ENVIRONMENT SETUP                      ║"
echo "║                 Real Programming Multi-Terminal Setup                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check required packages
echo -e "${BLUE}Checking required packages...${NC}"
MISSING_PACKAGES=""

for pkg in terminator xdotool; do
    if ! command -v "$pkg" &> /dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    echo -e "${YELLOW}Installing missing packages:$MISSING_PACKAGES${NC}"
    sudo apt update && sudo apt install -y $MISSING_PACKAGES
else
    echo -e "${GREEN}All required packages are installed.${NC}"
fi

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x "$SCRIPT_DIR/scripts/"*.sh

# Create desktop entry
echo -e "${BLUE}Creating desktop entry...${NC}"
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/cursor-agent-multi.desktop << EOF
[Desktop Entry]
Name=Cursor Agent Multi-Terminal
Comment=Multi-agent cursor environment with real programming setup
Exec=$SCRIPT_DIR/scripts/launch-multi-agent.sh
Type=Application
Categories=Development;System;
Terminal=false
Icon=terminal
EOF

# Setup aliases
echo -e "${BLUE}Setting up aliases...${NC}"
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

if [ -f "$SHELL_RC" ]; then
    cp "$SHELL_RC" "$SHELL_RC.backup.$(date +%Y%m%d_%H%M%S)"
fi

cat >> "$SHELL_RC" << EOF

# Multi-Agent Cursor Environment Aliases
# Added on $(date)
alias cursor-multi='$SCRIPT_DIR/scripts/launch-multi-agent.sh'
alias ca='$SCRIPT_DIR/scripts/ca-command.sh'
alias mcp-coord='$SCRIPT_DIR/scripts/mcp-simple-coord.sh'
EOF

# Create prompt templates directory
echo -e "${BLUE}Setting up MCP prompt templates...${NC}"
mkdir -p "$SCRIPT_DIR/prompts"

echo -e "${GREEN}Setup completed successfully!${NC}"
echo ""
echo -e "${CYAN}Available commands:${NC}"
echo "  cursor-multi         - Launch multi-agent environment"
echo "  ca <agent> \"<cmd>\"   - Send command to agent"
echo "  mcp-coord <cmd>      - MCP coordination commands"
echo ""
echo -e "${CYAN}MCP Coordination commands:${NC}"
echo "  mcp-coord test       - Test all agents"
echo "  mcp-coord workflow   - Start development workflow"
echo "  mcp-coord send <agent> <instruction>"
echo ""
echo -e "${CYAN}Agent Commands:${NC}"
echo "  ca primary \"<cmd>\"    - Send to coordination agent"
echo "  ca secondary \"<cmd>\"  - Send to execution agent"
echo "  ca research \"<cmd>\"   - Send to analysis agent"
echo "  ca execution \"<cmd>\"  - Send to operations agent"
echo ""
echo -e "${YELLOW}To apply aliases immediately:${NC}"
echo "  source $SHELL_RC"
echo ""
echo -e "${GREEN}Launch the environment with:${NC}"
echo "  cursor-multi"
echo ""
echo -e "${MAGENTA}Agent Specialties (MCP Integration):${NC}"
echo "  🔵 PRIMARY   - Coordination & Planning (MCP coordination tools)"
echo "  🔷 SECONDARY - Code Execution & Development (MCP filesystem/code tools)"
echo "  🟣 RESEARCH  - Analysis & Information Gathering (MCP analysis tools)"
echo "  🔴 EXECUTION - System Operations & Deployment (MCP deployment tools)"
echo ""
echo -e "${BLUE}MCP Integration Features:${NC}"
echo "  ✓ Systematic use of MCP prompt templates"
echo "  ✓ Real MCP tools for file operations, code analysis, deployment"
echo "  ✓ Structured agent communication via MCP protocols"
echo "  ✓ Result verification and prompt improvement tracking"
echo "  ✓ Workflow orchestration using MCP coordination tools"
echo ""
echo -e "${CYAN}MCP Commands:${NC}"
echo "  mcp-coord primary \"task\"     - Apply MCP template to primary agent"
echo "  mcp-coord secondary \"task\"   - Apply MCP template to secondary agent"
echo "  ca primary \"instruction\"     - Direct command to primary agent"
echo "  ca secondary \"instruction\"   - Direct command to secondary agent"
echo ""
echo -e "${CYAN}🎯 Perfect for:${NC}"
echo "  • Multi-agent development workflows"
echo "  • Distributed task processing"
echo "  • Real-time collaboration between agents"
echo "  • Complex project orchestration"
echo "  • AI-assisted development teams"
echo ""
echo -e "${GREEN}🚀 Ready to launch! Run: cursor-multi${NC}"
echo ""
echo -e "${YELLOW}📝 Note: This environment works in any console session${NC}"
echo -e "${YELLOW}   (not bound to specific terminals). Run your own graphical${NC}"
echo -e "${YELLOW}   environment that supports terminator and xdotool.${NC}"