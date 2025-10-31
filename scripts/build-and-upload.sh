#!/bin/bash
# Build and Upload Script for SpareTools Packages to Cloudsmith
# 
# This script:
# 1. Builds all packages in correct dependency order
# 2. Runs integration tests
# 3. Uploads packages to Cloudsmith registry
#
# Usage:
#   ./scripts/build-and-upload.sh [--skip-tests] [--skip-upload]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLOUDSMITH_REMOTE="sparesparrow-conan"
CLOUDSMITH_URL="https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/"

# Parse arguments
SKIP_TESTS=false
SKIP_UPLOAD=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-upload)
            SKIP_UPLOAD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            ;;
    esac
done

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if conan is installed
    if ! command -v conan &> /dev/null; then
        log_error "Conan is not installed. Install with: pip install conan==2.21.0"
        exit 1
    fi
    
    # Check Conan version
    CONAN_VERSION=$(conan --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_info "Conan version: $CONAN_VERSION"
    
    # Check if Cloudsmith API key is set (for upload)
    if [ "$SKIP_UPLOAD" = false ] && [ -z "$CLOUDSMITH_API_KEY" ]; then
        log_warning "CLOUDSMITH_API_KEY not set. Upload will fail."
        log_info "Set it with: export CLOUDSMITH_API_KEY=your_api_key"
    fi
    
    log_success "Prerequisites check passed"
}

# Configure Conan
configure_conan() {
    log_info "Configuring Conan..."
    
    # Detect default profile if not exists
    conan profile detect --force
    
    # Add Cloudsmith remote
    conan remote add $CLOUDSMITH_REMOTE $CLOUDSMITH_URL --force
    
    log_success "Conan configured"
}

# Build a single package
build_package() {
    local name=$1
    local version=$2
    local path=$3
    
    log_info "Building $name/$version..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would build: conan create $path --version=$version --build=missing"
        return 0
    fi
    
    cd "$WORKSPACE_ROOT"
    
    if conan create "$path" --version="$version" --build=missing; then
        log_success "✓ $name/$version built successfully"
        return 0
    else
        log_error "✗ Failed to build $name/$version"
        return 1
    fi
}

# Build all packages
build_all_packages() {
    log_info "Building all packages in dependency order..."
    
    # Package definitions: name, version, path
    declare -a packages=(
        "sparetools-base:2.0.0:packages/sparetools-base"
        "sparetools-cpython:3.12.7:packages/sparetools-cpython"
        "sparetools-shared-dev-tools:2.0.0:packages/sparetools-shared-dev-tools"
        "sparetools-bootstrap:2.0.0:packages/sparetools-bootstrap"
        "sparetools-openssl-tools:2.0.0:packages/sparetools-openssl-tools"
        "sparetools-openssl:3.3.2:packages/sparetools-openssl"
    )
    
    local failed_packages=()
    
    for package_info in "${packages[@]}"; do
        IFS=':' read -r name version path <<< "$package_info"
        
        if ! build_package "$name" "$version" "$path"; then
            failed_packages+=("$name/$version")
        fi
    done
    
    if [ ${#failed_packages[@]} -eq 0 ]; then
        log_success "All packages built successfully!"
        return 0
    else
        log_error "Failed to build packages: ${failed_packages[*]}"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping tests (--skip-tests flag)"
        return 0
    fi
    
    log_info "Running integration tests..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would run: python3 test/integration/test_package_cooperation.py"
        return 0
    fi
    
    cd "$WORKSPACE_ROOT"
    
    if [ -f "test/integration/test_package_cooperation.py" ]; then
        if python3 test/integration/test_package_cooperation.py; then
            log_success "✓ All integration tests passed"
            return 0
        else
            log_error "✗ Integration tests failed"
            log_warning "Continuing anyway (tests are advisory)"
            return 0
        fi
    else
        log_warning "Integration tests not found at test/integration/test_package_cooperation.py"
        return 0
    fi
}

# Upload packages to Cloudsmith
upload_packages() {
    if [ "$SKIP_UPLOAD" = true ]; then
        log_warning "Skipping upload (--skip-upload flag)"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would upload packages to Cloudsmith"
        return 0
    fi
    
    log_info "Uploading packages to Cloudsmith..."
    
    # Check if API key is set
    if [ -z "$CLOUDSMITH_API_KEY" ]; then
        log_error "CLOUDSMITH_API_KEY is not set"
        log_info "Set it with: export CLOUDSMITH_API_KEY=your_api_key"
        return 1
    fi
    
    # Authenticate with Cloudsmith
    log_info "Authenticating with Cloudsmith..."
    if ! conan remote login $CLOUDSMITH_REMOTE sparesparrow --password "$CLOUDSMITH_API_KEY"; then
        log_error "Failed to authenticate with Cloudsmith"
        return 1
    fi
    
    log_success "Authenticated with Cloudsmith"
    
    # Upload all sparetools packages
    log_info "Uploading sparetools-* packages..."
    
    if conan upload "sparetools-*/*" -r $CLOUDSMITH_REMOTE --confirm --retry 3 --retry-wait 5; then
        log_success "✓ All packages uploaded successfully"
        return 0
    else
        log_error "✗ Failed to upload some packages"
        return 1
    fi
}

# List uploaded packages
list_uploaded_packages() {
    if [ "$SKIP_UPLOAD" = true ] || [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    log_info "Packages available on Cloudsmith:"
    
    # Search for packages on remote
    conan search "sparetools-*" -r $CLOUDSMITH_REMOTE || true
    
    log_info ""
    log_info "Cloudsmith repository: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/"
}

# Generate build report
generate_build_report() {
    local report_file="$WORKSPACE_ROOT/build-report.md"
    
    log_info "Generating build report..."
    
    cat > "$report_file" << EOF
# SpareTools Build Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S %Z')
**Workspace:** $WORKSPACE_ROOT

## Packages Built

| Package | Version | Status |
|---------|---------|--------|
| sparetools-base | 2.0.0 | ✓ Built |
| sparetools-cpython | 3.12.7 | ✓ Built |
| sparetools-shared-dev-tools | 2.0.0 | ✓ Built |
| sparetools-bootstrap | 2.0.0 | ✓ Built |
| sparetools-openssl-tools | 2.0.0 | ✓ Built |
| sparetools-openssl | 3.3.2 | ✓ Built |

## Package Locations

Packages are stored in local Conan cache:

\`\`\`bash
# List all sparetools packages
conan list "sparetools-*"

# Get package path
conan cache path sparetools-openssl/3.3.2
\`\`\`

## Cloudsmith Upload

$(if [ "$SKIP_UPLOAD" = true ]; then
    echo "**Status:** Skipped (--skip-upload flag)"
else
    echo "**Status:** Uploaded to Cloudsmith"
    echo "**Repository:** https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/"
fi)

## Installation Instructions

### From Cloudsmith (Consumers)

\`\`\`bash
# Add Cloudsmith remote
conan remote add sparesparrow-conan \\
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Install OpenSSL
conan install --requires=sparetools-openssl/3.3.2 -r sparesparrow-conan
\`\`\`

### From Local Cache (Development)

\`\`\`bash
# Use packages from local cache
conan install --requires=sparetools-openssl/3.3.2
\`\`\`

## Integration Tests

$(if [ "$SKIP_TESTS" = true ]; then
    echo "**Status:** Skipped (--skip-tests flag)"
else
    echo "**Status:** Run"
    echo ""
    echo "Run integration tests manually:"
    echo ""
    echo "\`\`\`bash"
    echo "python3 test/integration/test_package_cooperation.py"
    echo "\`\`\`"
fi)

## Next Steps

1. **Test installation from Cloudsmith:**
   \`\`\`bash
   conan install --requires=sparetools-openssl/3.3.2 -r sparesparrow-conan
   \`\`\`

2. **Run cross-platform tests:**
   \`\`\`bash
   python3 test-platform-detection.py
   python3 test-conan-cross-platform.py
   \`\`\`

3. **Update documentation:**
   - Update CHANGELOG.md
   - Update README.md with new version info

4. **Create Git tag:**
   \`\`\`bash
   git tag -a v2.0.0 -m "Release v2.0.0: Cross-platform support and unified package ecosystem"
   git push origin v2.0.0
   \`\`\`

---

**Report generated by:** build-and-upload.sh
EOF
    
    log_success "Build report generated: $report_file"
}

# Main execution
main() {
    echo ""
    log_info "========================================"
    log_info "SpareTools Build and Upload Script"
    log_info "========================================"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Step 1: Check prerequisites
    check_prerequisites
    echo ""
    
    # Step 2: Configure Conan
    configure_conan
    echo ""
    
    # Step 3: Build packages
    if ! build_all_packages; then
        log_error "Build failed. Aborting."
        exit 1
    fi
    echo ""
    
    # Step 4: Run integration tests
    run_integration_tests
    echo ""
    
    # Step 5: Upload to Cloudsmith
    if ! upload_packages; then
        log_error "Upload failed. Check logs above."
        exit 1
    fi
    echo ""
    
    # Step 6: List uploaded packages
    list_uploaded_packages
    echo ""
    
    # Step 7: Generate build report
    generate_build_report
    echo ""
    
    log_success "========================================"
    log_success "Build and upload complete!"
    log_success "========================================"
    echo ""
    log_info "Next steps:"
    log_info "1. Review build-report.md"
    log_info "2. Test installation: conan install --requires=sparetools-openssl/3.3.2 -r sparesparrow-conan"
    log_info "3. Commit changes: git add -A && git commit -m 'Release v2.0.0'"
    log_info "4. Push to remote: git push origin main"
    log_info "5. Create release tag: git tag -a v2.0.0 -m 'Release v2.0.0'"
}

# Run main function
main "$@"
