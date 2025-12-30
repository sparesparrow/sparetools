#!/bin/bash
#
# SpareTools MCP Development Setup Script
# Sets up MCP servers for development use
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_header() {
    echo -e "${PURPLE}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}  $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}========================================${NC}" | tee -a "$LOG_FILE"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/tmp/sparetools-mcp-setup-$(date +%Y%m%d-%H%M%S).log"

# Function to check prerequisites
check_prerequisites() {
    log_header "Checking Prerequisites"

    local missing_tools=()

    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_tools+=("Node.js")
    else
        log_success "✓ Node.js found: $(node --version)"
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        missing_tools+=("npm")
    else
        log_success "✓ npm found: $(npm --version)"
    fi

    # Check Conan
    if ! command -v conan &> /dev/null; then
        missing_tools+=("Conan")
    else
        log_success "✓ Conan found: $(conan --version)"
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("Python 3")
    else
        log_success "✓ Python found: $(python3 --version)"
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install missing tools and run this script again"
        exit 1
    fi

    log_success "✓ All prerequisites satisfied"
}

# Function to build MCP packages
build_mcp_packages() {
    log_header "Building MCP Packages"

    cd "$PROJECT_ROOT"

    # Build core packages first
    log_info "Building sparetools-mcp-core..."
    conan create packages/mcp/sparetools-mcp-core --build=missing

    log_info "Building sparetools-mcp-servers..."
    conan create packages/mcp/sparetools-mcp-servers --build=missing

    log_info "Building sparetools-mcp-prompts..."
    conan create packages/mcp/sparetools-mcp-prompts --build=missing

    log_info "Building sparetools-mcp-ecosystem..."
    conan create packages/mcp/sparetools-mcp-ecosystem --build=missing

    log_info "Building sparetools-prompt-system..."
    conan create packages/prompt/sparetools-prompt-system --build=missing

    log_success "✓ All MCP packages built successfully"
}

# Function to install Node.js dependencies
install_nodejs_deps() {
    log_header "Installing Node.js Dependencies"

    cd "$PROJECT_ROOT/packages/mcp/sparetools-mcp-prompts"

    log_info "Installing dependencies for sparetools-mcp-prompts..."
    if command -v pnpm &> /dev/null && [ -f "pnpm-lock.yaml" ]; then
        log_info "Using pnpm..."
        pnpm install --frozen-lockfile
    else
        log_info "Using npm..."
        npm ci
    fi

    log_success "✓ Node.js dependencies installed"
}

# Function to install Python dependencies
install_python_deps() {
    log_header "Installing Python Dependencies"

    cd "$PROJECT_ROOT"

    # Install sparetools-cpython and get environment
    log_info "Setting up bundled CPython environment..."
    conan install --requires=sparetools-cpython/3.12.7 --build=missing >/dev/null 2>&1

    # Source the environment
    if [ -f "conanrun.sh" ]; then
        source conanrun.sh
        log_success "✓ Bundled CPython environment activated"
    else
        log_warning "⚠ Could not find conanrun.sh, using system Python"
    fi

    # Install dependencies for each MCP server
    MCP_SERVERS_DIR="packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers"

    if [ -f "$MCP_SERVERS_DIR/esp32_serial_monitor/requirements.txt" ]; then
        log_info "Installing ESP32 serial monitor dependencies..."
        python3 -m pip install -r "$MCP_SERVERS_DIR/esp32_serial_monitor/requirements.txt"
    fi

    if [ -f "$MCP_SERVERS_DIR/android_dev_tools/requirements.txt" ]; then
        log_info "Installing Android dev tools dependencies..."
        python3 -m pip install -r "$MCP_SERVERS_DIR/android_dev_tools/requirements.txt"
    fi

    if [ -f "$MCP_SERVERS_DIR/conan_cloudsmith/requirements.txt" ]; then
        log_info "Installing Conan Cloudsmith dependencies..."
        python3 -m pip install -r "$MCP_SERVERS_DIR/conan_cloudsmith/requirements.txt"
    fi

    log_success "✓ Python dependencies installed"
}

# Function to configure Cursor IDE
configure_cursor() {
    log_header "Configuring Cursor IDE"

    local cursor_config="$HOME/.cursor/mcp.json"

    # Create Cursor config directory if it doesn't exist
    mkdir -p "$(dirname "$cursor_config")"

    # Generate MCP configuration
    cat > "$cursor_config" << 'EOF'
{
  "mcpServers": {
    "sparetools-mcp-prompts": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-prompts"],
      "env": {
        "MODE": "mcp",
        "LOG_LEVEL": "info",
        "PORT": "3001"
      }
    },
    "sparetools-esp32": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "esp32"],
      "env": {
        "ESP32_LOG_LEVEL": "info",
        "ESP32_LOG_DIR": "~/.sparetools/esp32/logs",
        "ESP32_SESSION_STORAGE": "~/.sparetools/esp32/sessions.json"
      }
    },
    "sparetools-android": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "android"],
      "env": {
        "ANDROID_LOG_LEVEL": "info",
        "ANDROID_LOG_DIR": "~/.sparetools/android/logs",
        "ANDROID_SESSION_STORAGE": "~/.sparetools/android/sessions.json"
      }
    },
    "sparetools-conan": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "conan"],
      "env": {
        "CONAN_LOG_LEVEL": "info",
        "CONAN_LOG_DIR": "~/.sparetools/conan/logs",
        "CONAN_SESSION_STORAGE": "~/.sparetools/conan/sessions.json",
        "CLOUDSMITH_API_KEY": "${CLOUDSMITH_API_KEY}",
        "CLOUDSMITH_ORG": "sparesparrow-conan"
      }
    },
    "sparetools-repo": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "repo"],
      "env": {
        "LOG_LEVEL": "info",
        "REPO_LOG_DIR": "~/.sparetools/repo/logs"
      }
    }
  }
}
EOF

    log_success "✓ Cursor MCP configuration created: $cursor_config"
    log_info "Restart Cursor IDE to load the MCP servers"
}

# Function to verify installation
verify_installation() {
    log_header "Verifying Installation"

    local issues_found=0

    # Check if packages are installed
    log_info "Checking Conan packages..."
    if conan list "sparetools-mcp-ecosystem/1.0.0" >/dev/null 2>&1; then
        log_success "✓ sparetools-mcp-ecosystem installed"
    else
        log_error "✗ sparetools-mcp-ecosystem not found"
        ((issues_found++))
    fi

    # Check Node.js dependencies
    if [ -d "$PROJECT_ROOT/packages/mcp/sparetools-mcp-prompts/node_modules" ]; then
        log_success "✓ Node.js dependencies installed"
    else
        log_warning "⚠ Node.js dependencies not found in expected location"
    fi

    # Check Cursor configuration
    if [ -f "$HOME/.cursor/mcp.json" ]; then
        log_success "✓ Cursor MCP configuration created"
    else
        log_warning "⚠ Cursor MCP configuration not found"
    fi

    # Try to run a basic test
    log_info "Testing MCP ecosystem launcher..."
    if command -v sparetools-mcp-ecosystem &> /dev/null; then
        log_success "✓ MCP ecosystem launcher available"
    else
        log_warning "⚠ MCP ecosystem launcher not in PATH"
        log_info "Make sure to add the package bin directory to your PATH"
    fi

    if [ $issues_found -gt 0 ]; then
        log_warning "⚠ $issues_found issues found during verification"
        log_info "Check the log file for details: $LOG_FILE"
    else
        log_success "✓ Installation verification passed"
    fi
}

# Function to show usage instructions
show_usage() {
    log_header "MCP Development Setup Complete"

    cat << 'EOF' | tee -a "$LOG_FILE"

🎉 SpareTools MCP Development Environment Setup Complete!

📋 Next Steps:

1. **Restart Cursor IDE** to load MCP servers
   - The servers will be available in Cursor's MCP interface

2. **Test Individual Servers**:
   # Test MCP Prompts
   sparetools-mcp-ecosystem mcp-prompts --help

   # Test ESP32 Server
   sparetools-mcp-ecosystem mcp-servers esp32 --help

   # Test Android Server
   sparetools-mcp-ecosystem mcp-servers android --help

   # Test Conan Server
   sparetools-mcp-ecosystem mcp-servers conan --help

3. **Configure Environment Variables** (if needed):
   export CLOUDSMITH_API_KEY="your-api-key"
   export CLOUDSMITH_ORG="sparesparrow-conan"

4. **Available MCP Tools**:
   - ESP32 Serial Monitor: Device detection and serial I/O
   - Android Dev Tools: APK building and ADB operations
   - Conan Cloudsmith: Package management and publishing
   - Repository Cleanup: Code maintenance and cleanup
   - MCP Prompts: AI-powered development prompts

📚 Documentation:
- MCP Integration Guide: packages/mcp/sparetools-mcp-ecosystem/SPARETOOLS_MCP_INTEGRATION.md
- Individual server docs: packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers/*/README.md

🔧 Troubleshooting:
- If servers don't appear in Cursor, check: ~/.cursor/mcp.json
- View logs: ~/.sparetools/*/logs/
- Reset setup: rm -rf ~/.sparetools/ && ./scripts/setup-mcp-dev.sh

📝 Log File: LOG_FILE_REPLACE

🚀 Happy coding with AI-assisted development!

EOF

    # Replace the log file placeholder
    sed -i "s|LOG_FILE_REPLACE|$LOG_FILE|g" "$LOG_FILE"
}

# Main execution
main() {
    log_header "SpareTools MCP Development Setup"
    log_info "Log file: $LOG_FILE"
    log_info "Project root: $PROJECT_ROOT"
    echo ""

    check_prerequisites
    echo ""

    build_mcp_packages
    echo ""

    install_nodejs_deps
    echo ""

    install_python_deps
    echo ""

    configure_cursor
    echo ""

    verify_installation
    echo ""

    show_usage
}

# Handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: $0"
            echo ""
            echo "Sets up SpareTools MCP servers for development use."
            echo "This script will:"
            echo "  - Check prerequisites (Node.js, npm, Conan, Python)"
            echo "  - Build all MCP packages via Conan"
            echo "  - Install Node.js dependencies for mcp-prompts"
            echo "  - Install Python dependencies for MCP servers"
            echo "  - Configure Cursor IDE MCP integration"
            echo "  - Verify the installation"
            echo ""
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
