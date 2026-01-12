#!/bin/bash
# Unified deployment script for MCP Transport Telegram
# Builds package, uploads to Cloudsmith, and deploys to MIA server

set -e  # Exit on any error

# Configuration
REMOTE_NAME="sparetools"
PACKAGE_NAME="sparetools-mcp-transport-telegram"
PACKAGE_VERSION="1.0.0"
MIA_HOST="mia@192.168.200.134"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if conan is installed
    if ! command -v conan &> /dev/null; then
        log_error "Conan is not installed or not in PATH"
        exit 1
    fi

    # Check if authenticated with remote
    if ! conan remote list-users | grep -q "$REMOTE_NAME.*authenticated"; then
        log_error "Not authenticated with $REMOTE_NAME remote"
        log_info "Please run: conan remote login $REMOTE_NAME <your-cloudsmith-username>"
        exit 1
    fi

    # Check if SSH key is available for MIA deployment
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 $MIA_HOST "echo 'SSH connection test'" &> /dev/null; then
        log_warning "SSH connection to $MIA_HOST failed"
        log_info "Please ensure your SSH key is configured for $MIA_HOST"
        log_info "You can test with: ssh $MIA_HOST 'echo \"SSH test\"'"
    fi

    log_success "Prerequisites check passed"
}

# Function to build the MCP Transport Telegram package
build_package() {
    log_info "Building $PACKAGE_NAME package..."

    cd "$PROJECT_ROOT"

    # Build the package
    if ! python build_all_packages.py --export-local --remote "$REMOTE_NAME" --verbose | grep "$PACKAGE_NAME"; then
        log_error "Failed to build $PACKAGE_NAME package"
        exit 1
    fi

    log_success "Package built successfully"
}

# Function to upload package to Cloudsmith
upload_package() {
    log_info "Uploading $PACKAGE_NAME to Cloudsmith..."

    # Upload the package
    if ! conan upload "$PACKAGE_NAME/$PACKAGE_VERSION" -r "$REMOTE_NAME" -c --force; then
        log_error "Failed to upload $PACKAGE_NAME to Cloudsmith"
        exit 1
    fi

    log_success "Package uploaded to Cloudsmith successfully"
}

# Function to deploy to MIA server
deploy_to_mia() {
    log_info "Deploying to MIA server ($MIA_HOST)..."

    # Create deployment script for remote execution
    cat > /tmp/mia_deploy.sh << 'EOF'
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Install the package from Cloudsmith
log_info "Installing sparetools-mcp-transport-telegram from Cloudsmith..."
if ! conan install "sparetools-mcp-transport-telegram/1.0.0" --build=missing; then
    log_error "Failed to install package from Cloudsmith"
    exit 1
fi

# Check if MIA orchestrator is running and restart if needed
log_info "Checking MIA orchestrator status..."
if systemctl is-active --quiet mia-orchestrator; then
    log_info "Restarting MIA orchestrator to pick up new MCP transport..."
    sudo systemctl restart mia-orchestrator
else
    log_warning "MIA orchestrator service not found or not running"
    log_info "You may need to manually restart MIA or configure the service"
fi

# Verify the installation
log_info "Verifying installation..."
if command -v sparetools-mcp-transport-telegram &> /dev/null; then
    log_success "sparetools-mcp-transport-telegram command is available"
else
    log_error "sparetools-mcp-transport-telegram command not found"
    exit 1
fi

log_success "MCP Transport Telegram deployed successfully on MIA server!"
log_info "Next steps:"
log_info "1. Configure Telegram API credentials in MIA environment"
log_info "2. Update MIA orchestrator configuration to include Telegram transport"
log_info "3. Test Telegram bot integration"
EOF

    # Make the script executable and copy to MIA server
    chmod +x /tmp/mia_deploy.sh

    # Execute the deployment on MIA server
    if ! scp /tmp/mia_deploy.sh $MIA_HOST:/tmp/; then
        log_error "Failed to copy deployment script to MIA server"
        exit 1
    fi

    # Execute the deployment script on MIA server
    if ! ssh $MIA_HOST "bash /tmp/mia_deploy.sh"; then
        log_error "Failed to execute deployment on MIA server"
        exit 1
    fi

    # Clean up
    rm -f /tmp/mia_deploy.sh
    ssh $MIA_HOST "rm -f /tmp/mia_deploy.sh" || true

    log_success "Deployment to MIA server completed successfully"
}

# Function to run integration tests
run_integration_tests() {
    log_info "Running integration tests..."

    # Test local installation
    if ! conan install "$PACKAGE_NAME/$PACKAGE_VERSION" --build=missing; then
        log_error "Local integration test failed"
        exit 1
    fi

    # Test that the command is available
    if ! which sparetools-mcp-transport-telegram &> /dev/null; then
        log_error "sparetools-mcp-transport-telegram command not available after installation"
        exit 1
    fi

    log_success "Integration tests passed"
}

# Main deployment function
main() {
    log_info "🚀 Starting MCP Transport Telegram unified deployment"
    log_info "Package: $PACKAGE_NAME/$PACKAGE_VERSION"
    log_info "Remote: $REMOTE_NAME"
    log_info "MIA Host: $MIA_HOST"
    echo

    # Run deployment steps
    check_prerequisites
    echo
    build_package
    echo
    upload_package
    echo
    run_integration_tests
    echo
    deploy_to_mia
    echo

    log_success "🎉 MCP Transport Telegram deployment completed successfully!"
    log_info ""
    log_info "The Telegram MCP transport is now:"
    log_info "  ✅ Built and packaged"
    log_info "  ✅ Uploaded to Cloudsmith"
    log_info "  ✅ Deployed to MIA server"
    log_info ""
    log_info "Next steps:"
    log_info "1. Configure Telegram API credentials on MIA server"
    log_info "2. Update MIA orchestrator configuration"
    log_info "3. Test Telegram bot functionality"
    log_info ""
    log_info "Useful commands:"
    log_info "  ssh $MIA_HOST 'sparetools-mcp-transport-telegram --help'"
    log_info "  ssh $MIA_HOST 'systemctl status mia-orchestrator'"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "MCP Transport Telegram Unified Deployment Script"
        echo ""
        echo "This script builds the MCP Transport Telegram package, uploads it to Cloudsmith,"
        echo "and deploys it to the MIA server."
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --skip-build        Skip the build step (use existing package)"
        echo "  --skip-upload       Skip the upload step"
        echo "  --skip-deploy       Skip the MIA deployment step"
        echo "  --test-only         Only run integration tests"
        echo ""
        echo "Environment Variables:"
        echo "  REMOTE_NAME         Conan remote name (default: sparetools)"
        echo "  MIA_HOST           MIA server SSH host (default: mia@192.168.200.134)"
        echo ""
        exit 0
        ;;
    "--test-only")
        run_integration_tests
        ;;
    *)
        main "$@"
        ;;
esac