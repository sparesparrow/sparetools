#!/bin/bash
# Multi-Agent Cursor Environment Launcher
# Launches terminator with multiple cursor-agent instances

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/configs"

# Colors for output
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
echo "║                    MULTI-AGENT CURSOR ENVIRONMENT                         ║"
echo "║                    Real Programming Setup                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in a console session (not bound to specific terminal)
if [ -n "$DISPLAY" ]; then
    echo -e "${YELLOW}Warning: Running in graphical session. For best experience, run in console (Ctrl+Alt+F1-F6).${NC}"
    echo -e "${YELLOW}The environment will still work but may have display conflicts.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}Running in console session - perfect!${NC}"
fi

# Check if display is available
if [ -z "$DISPLAY" ]; then
    echo -e "${RED}No DISPLAY variable set. Make sure you're running this from a graphical session.${NC}"
    exit 1
fi

# Check required tools
missing_tools=()
for tool in terminator xdotool; do
    if ! command -v "$tool" &> /dev/null; then
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -ne 0 ]; then
    echo -e "${RED}Missing required tools: ${missing_tools[*]}${NC}"
    echo -e "${YELLOW}Install with: sudo apt install ${missing_tools[*]}${NC}"
    exit 1
fi

echo -e "${GREEN}Starting Multi-Agent Cursor Environment...${NC}"

# Clean up any existing instruction files
rm -f /tmp/agent_*_instructions

# Launch terminator with custom config
echo -e "${BLUE}Launching terminator with multi-agent layout...${NC}"
terminator --config="$CONFIG_DIR/terminator-config" --layout=cursor_agent_multi &
TERMINATOR_PID=$!

# Wait for terminator to start
sleep 5

echo -e "${BLUE}Initializing cursor agents...${NC}"

# Get window IDs for different terminals
sleep 2
WIDS=$(xdotool search --class "terminator" | head -4)

if [ -n "$WIDS" ]; then
    WID_ARRAY=($WIDS)

    if [ ${#WID_ARRAY[@]} -ge 4 ]; then
        echo -e "${GREEN}Found ${#WID_ARRAY[@]} terminal windows. Initializing agents...${NC}"

        # Start agents in each terminal
        xdotool windowactivate ${WID_ARRAY[0]} && \
        xdotool type --window ${WID_ARRAY[0]} "$SCRIPT_DIR/agent-primary.sh" && \
        xdotool key --window ${WID_ARRAY[0]} Return &

        sleep 1

        xdotool windowactivate ${WID_ARRAY[1]} && \
        xdotool type --window ${WID_ARRAY[1]} "$SCRIPT_DIR/agent-secondary.sh" && \
        xdotool key --window ${WID_ARRAY[1]} Return &

        sleep 1

        xdotool windowactivate ${WID_ARRAY[2]} && \
        xdotool type --window ${WID_ARRAY[2]} "$SCRIPT_DIR/agent-research.sh" && \
        xdotool key --window ${WID_ARRAY[2]} Return &

        sleep 1

        xdotool windowactivate ${WID_ARRAY[3]} && \
        xdotool type --window ${WID_ARRAY[3]} "$SCRIPT_DIR/agent-execution.sh" && \
        xdotool key --window ${WID_ARRAY[3]} Return &

        sleep 2

        echo -e "${GREEN}Multi-Agent Cursor Environment is now running!${NC}"
    else
        echo -e "${YELLOW}Warning: Could not find all 4 terminal windows. Starting agents manually.${NC}"
        # Fallback: Start agents in current terminal
        echo -e "${GREEN}Starting agents in background...${NC}"
        "$SCRIPT_DIR/agent-primary.sh" &
        "$SCRIPT_DIR/agent-secondary.sh" &
        "$SCRIPT_DIR/agent-research.sh" &
        "$SCRIPT_DIR/agent-execution.sh" &
    fi
else
    echo -e "${YELLOW}Warning: Could not find terminator windows. Starting agents manually.${NC}"
    # Fallback
    "$SCRIPT_DIR/agent-primary.sh" &
    "$SCRIPT_DIR/agent-secondary.sh" &
    "$SCRIPT_DIR/agent-research.sh" &
    "$SCRIPT_DIR/agent-execution.sh" &
fi

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                              AGENT CONTROLS                               ║"
echo "║                                                                          ║"
echo "║  Ctrl+Shift+E: Split terminal horizontally                               ║"
echo "║  Ctrl+Shift+O: Split terminal vertically                                 ║"
echo "║  Ctrl+Shift+W: Close current terminal                                    ║"
echo "║  Ctrl+Tab: Switch between terminals                                      ║"
echo "║  Ctrl+Shift+Q: Quit terminator                                           ║"
echo "║                                                                          ║"
echo "║  Command Injection:                                                      ║"
echo "║  ca primary \"<command>\"     - Send to Primary agent                     ║"
echo "║  ca secondary \"<command>\"   - Send to Secondary agent                   ║"
echo "║  ca research \"<command>\"    - Send to Research agent                    ║"
echo "║  ca execution \"<command>\"   - Send to Execution agent                   ║"
echo "║                                                                          ║"
echo "║  Agent Specialties:                                                      ║"
echo "║  PRIMARY   (Blue):   Coordination & Planning                            ║"
echo "║  SECONDARY (Cyan):   Code Execution & Development                       ║"
echo "║  RESEARCH (Magenta): Analysis & Information Gathering                   ║"
echo "║  EXECUTION (Red):    System Operations & Deployment                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create command injection alias
cat > /tmp/ca_command << 'EOF'
#!/bin/bash
# Cursor Agent command injection
AGENT="$1"
COMMAND="$2"

if [ -z "$AGENT" ] || [ -z "$COMMAND" ]; then
    echo "Usage: ca <agent> \"<command>\""
    echo "Agents: primary, secondary, research, execution"
    exit 1
fi

INSTRUCTION_FILE="/tmp/agent_${AGENT}_instructions"
echo "$COMMAND" > "$INSTRUCTION_FILE"
echo "Command sent to $AGENT agent: $COMMAND"
EOF
chmod +x /tmp/ca_command

# Wait for user input to exit
echo -e "${YELLOW}Press Ctrl+C to stop the multi-agent environment${NC}"
trap 'echo -e "\n${GREEN}Shutting down Multi-Agent Cursor Environment...${NC}"; kill $TERMINATOR_PID 2>/dev/null; rm -f /tmp/agent_*_instructions /tmp/ca_command; exit 0' INT

# Keep the script running
while true; do
    sleep 1
done