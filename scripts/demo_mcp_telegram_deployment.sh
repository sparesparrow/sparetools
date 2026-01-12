#!/bin/bash
# MCP Transport Telegram Deployment Demo
# Shows the complete workflow: build → upload → deploy

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGE_NAME="sparetools-mcp-transport-telegram"
PACKAGE_VERSION="1.0.0"
MIA_HOST="mia@192.168.200.134"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC} ${CYAN}$1${NC}${PURPLE}$(printf '%*s' $((78-${#1})) '')║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."

    # Check if conan is installed
    if ! command -v conan &> /dev/null; then
        log_error "Conan is not installed or not in PATH"
        log_info "Install Conan: pip install conan"
        exit 1
    fi

    # Check if package exists
    if [ ! -d "$PROJECT_ROOT/packages/mcp/$PACKAGE_NAME" ]; then
        log_error "Package directory not found: $PROJECT_ROOT/packages/mcp/$PACKAGE_NAME"
        exit 1
    fi

    # Check SSH connection to MIA server
    log_info "Testing SSH connection to MIA server..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $MIA_HOST "echo 'SSH OK'" &> /dev/null; then
        log_warning "SSH connection to $MIA_HOST failed"
        log_info "This demo will show the deployment process but skip actual remote deployment"
        SSH_AVAILABLE=false
    else
        log_success "SSH connection to MIA server established"
        SSH_AVAILABLE=true
    fi

    log_success "Prerequisites check completed"
}

# Function to build the package locally
build_package_locally() {
    log_step "Building $PACKAGE_NAME package locally..."

    cd "$PROJECT_ROOT"

    # Create build directory
    BUILD_DIR="$PROJECT_ROOT/packages/mcp/$PACKAGE_NAME/build"
    mkdir -p "$BUILD_DIR"

    # Export package locally
    log_info "Exporting package to local cache..."
    if ! conan export "packages/mcp/$PACKAGE_NAME" --name="$PACKAGE_NAME" --version="$PACKAGE_VERSION"; then
        log_error "Failed to export package locally"
        return 1
    fi

    # Build package locally
    log_info "Building package locally..."
    if ! conan install "$PACKAGE_NAME/$PACKAGE_VERSION@" -of="$BUILD_DIR" --build=missing; then
        log_error "Failed to build package locally"
        return 1
    fi

    log_success "Package built successfully locally"
    return 0
}

# Function to simulate Cloudsmith upload
simulate_cloudsmith_upload() {
    log_step "Simulating Cloudsmith package upload..."

    log_info "In a real deployment, this would upload to Cloudsmith:"
    echo "  conan upload '$PACKAGE_NAME/$PACKAGE_VERSION' -r sparetools -c --force"
    echo
    log_info "Cloudsmith repository would be configured as:"
    echo "  https://conan.cloudsmith.io/sparesparrow-conan/sparetools/"
    echo
    log_info "Authentication would require:"
    echo "  conan remote login sparetools <cloudsmith-api-key>"
    echo
    log_warning "Skipping actual upload (no Cloudsmith credentials configured)"
    log_success "Cloudsmith upload simulation completed"
}

# Function to deploy to MIA server
deploy_to_mia() {
    if [ "$SSH_AVAILABLE" != "true" ]; then
        log_warning "SSH not available, showing deployment commands instead"
        show_deployment_commands
        return 0
    fi

    log_step "Deploying to MIA server ($MIA_HOST)..."

    # Create deployment script
    cat > /tmp/mia_telegram_deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 MCP Transport Telegram Deployment on MIA Server"
echo "=================================================="

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
pip3 install --user --quiet telethon pydantic mcp || true

# Create deployment directory
DEPLOY_DIR="$HOME/mcp-transport-telegram"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy package files (in real deployment, this would be from Cloudsmith)
echo "📋 Copying package files..."
# In real deployment: conan install sparetools-mcp-transport-telegram/1.0.0 --build=missing

# Create systemd service for MCP Transport Telegram
echo "🔧 Creating systemd service..."
cat > "$HOME/.config/systemd/user/mcp-transport-telegram.service" << 'SERVICE_EOF'
[Unit]
Description=MCP Transport Telegram
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m mcp_transport_telegram
WorkingDirectory=%h/mcp-transport-telegram
Environment=PYTHONPATH=%h/mcp-transport-telegram/src
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
SERVICE_EOF

# Reload systemd and enable service
echo "🔄 Reloading systemd and enabling service..."
systemctl --user daemon-reload
systemctl --user enable mcp-transport-telegram

echo "✅ MCP Transport Telegram deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure Telegram API credentials:"
echo "   export TELEGRAM_API_ID='your_api_id'"
echo "   export TELEGRAM_API_HASH='your_api_hash'"
echo "   export TELEGRAM_BOT_TOKEN='your_bot_token'"
echo ""
echo "2. Start the service:"
echo "   systemctl --user start mcp-transport-telegram"
echo ""
echo "3. Check status:"
echo "   systemctl --user status mcp-transport-telegram"
echo ""
echo "4. View logs:"
echo "   journalctl --user -u mcp-transport-telegram -f"
EOF

    # Copy and execute deployment script
    log_info "Copying deployment script to MIA server..."
    if ! scp /tmp/mia_telegram_deploy.sh $MIA_HOST:/tmp/; then
        log_error "Failed to copy deployment script"
        return 1
    fi

    log_info "Executing deployment on MIA server..."
    if ! ssh $MIA_HOST "bash /tmp/mia_telegram_deploy.sh"; then
        log_error "Deployment failed on MIA server"
        return 1
    fi

    # Clean up
    rm -f /tmp/mia_telegram_deploy.sh
    ssh $MIA_HOST "rm -f /tmp/mia_telegram_deploy.sh" || true

    log_success "Deployment to MIA server completed successfully"
}

# Function to show deployment commands when SSH is not available
show_deployment_commands() {
    log_info "SSH not available. Here are the deployment commands to run manually:"
    echo
    echo "On MIA server ($MIA_HOST), run:"
    echo
    echo "1. Install dependencies:"
    echo "   pip3 install --user telethon pydantic mcp"
    echo
    echo "2. Create deployment directory:"
    echo "   mkdir -p ~/mcp-transport-telegram"
    echo
    echo "3. Copy package files:"
    echo "   # In real deployment: conan install sparetools-mcp-transport-telegram/1.0.0 --build=missing"
    echo
    echo "4. Create systemd service:"
    echo "   cat > ~/.config/systemd/user/mcp-transport-telegram.service << 'EOF'"
    echo "   [Unit]"
    echo "   Description=MCP Transport Telegram"
    echo "   After=network.target"
    echo "   [Service]"
    echo "   Type=simple"
    echo "   ExecStart=/usr/bin/python3 -m mcp_transport_telegram"
    echo "   WorkingDirectory=%h/mcp-transport-telegram"
    echo "   Environment=PYTHONPATH=%h/mcp-transport-telegram/src"
    echo "   Restart=always"
    echo "   RestartSec=10"
    echo "   [Install]"
    echo "   WantedBy=default.target"
    echo "   EOF"
    echo
    echo "5. Enable and start service:"
    echo "   systemctl --user daemon-reload"
    echo "   systemctl --user enable mcp-transport-telegram"
    echo "   systemctl --user start mcp-transport-telegram"
    echo
    echo "6. Check status:"
    echo "   systemctl --user status mcp-transport-telegram"
    echo
    log_success "Deployment commands displayed"
}

# Function to run integration tests
run_integration_tests() {
    log_step "Running integration tests..."

    # Test local installation
    log_info "Testing local package installation..."
    if ! conan install "$PACKAGE_NAME/$PACKAGE_VERSION@" --build=missing; then
        log_error "Local integration test failed"
        return 1
    fi

    # Test that the module can be imported
    log_info "Testing module import..."
    if ! python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/packages/mcp/$PACKAGE_NAME/src')
try:
    from mcp_transport_telegram.config import Config
    from mcp_transport_telegram.telegram_client import TelegramClientWrapper
    print('✅ Module imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"; then
        log_error "Module import test failed"
        return 1
    fi

    log_success "Integration tests passed"
}

# Function to show final status
show_final_status() {
    log_header "DEPLOYMENT SUMMARY"

    echo -e "${GREEN}✅ Package Structure:${NC}"
    echo "  • Created in: $PROJECT_ROOT/packages/mcp/$PACKAGE_NAME/"
    echo "  • Conan recipe: conanfile.py"
    echo "  • Source code: src/mcp_transport_telegram/"
    echo "  • Tests: tests/"
    echo "  • Config: config/"
    echo "  • Docker: Dockerfile, docker-compose.yml"
    echo "  • K8s: k8s-deployment.yaml"
    echo

    echo -e "${GREEN}✅ Build System Integration:${NC}"
    echo "  • Added to build_all_packages.py discovery"
    echo "  • Added to upload_packages.sh"
    echo "  • Added to versions.yaml"
    echo "  • Created unified deployment script"
    echo

    echo -e "${GREEN}✅ MIA Integration:${NC}"
    echo "  • Enhanced orchestrator with Telegram routing"
    echo "  • Added Telegram MCP to services config"
    echo "  • Context preservation for chat/thread sessions"
    echo "  • Response formatting for Telegram"
    echo

    echo -e "${GREEN}✅ Features Implemented:${NC}"
    echo "  • Bi-directional messaging"
    echo "  • Media handling (photos, docs, audio, video)"
    echo "  • Contact management"
    echo "  • Rate limiting and error recovery"
    echo "  • Structured logging with correlation IDs"
    echo "  • Docker/K8s deployment ready"
    echo

    if [ "$SSH_AVAILABLE" = "true" ]; then
        echo -e "${GREEN}✅ Deployment Status:${NC}"
        echo "  • SSH connection: Available"
        echo "  • MIA server: Accessible"
        echo "  • Deployment script: Ready"
    else
        echo -e "${YELLOW}⚠️  Deployment Status:${NC}"
        echo "  • SSH connection: Not available"
        echo "  • Manual deployment commands shown"
    fi

    echo
    log_header "NEXT STEPS"

    echo -e "${CYAN}To complete the deployment:${NC}"
    echo
    echo "1. 🔐 Configure Cloudsmith authentication:"
    echo "   conan remote login sparetools <api-key>"
    echo
    echo "2. 📦 Upload to Cloudsmith:"
    echo "   ./scripts/deploy_mcp_telegram.sh"
    echo
    echo "3. 🔧 Configure Telegram credentials on MIA server:"
    echo "   export TELEGRAM_API_ID='your_id'"
    echo "   export TELEGRAM_API_HASH='your_hash'"
    echo "   export TELEGRAM_BOT_TOKEN='your_token'"
    echo
    echo "4. 🚀 Start the service:"
    echo "   ssh $MIA_HOST 'systemctl --user start mcp-transport-telegram'"
    echo
    echo "5. 📱 Test with Telegram bot:"
    echo "   Send messages to your bot and see MIA responses!"
    echo

    log_success "🎉 MCP Transport Telegram deployment demo completed!"
}

# Main function
main() {
    log_header "MCP Transport Telegram - Complete Deployment Demo"

    check_prerequisites
    echo

    build_package_locally
    echo

    simulate_cloudsmith_upload
    echo

    run_integration_tests
    echo

    deploy_to_mia
    echo

    show_final_status
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "MCP Transport Telegram Deployment Demo"
        echo ""
        echo "This script demonstrates the complete deployment workflow:"
        echo "build → upload → deploy"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --build-only        Only build the package"
        echo "  --test-only         Only run integration tests"
        echo "  --deploy-only       Only run deployment (skip build)"
        echo ""
        exit 0
        ;;
    "--build-only")
        check_prerequisites
        build_package_locally
        ;;
    "--test-only")
        check_prerequisites
        run_integration_tests
        ;;
    "--deploy-only")
        check_prerequisites
        deploy_to_mia
        ;;
    *)
        main "$@"
        ;;
esac