#!/bin/bash
# Conan CI/CD Helper Scripts
# Enterprise-grade utilities for Conan package management in CI/CD pipelines

set -euo pipefail

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

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Configuration
CONAN_VERSION="${CONAN_VERSION:-2.21.0}"
CONAN_REMOTE="${CONAN_REMOTE:-conancenter}"
CONAN_USER="${CONAN_USER:-}"
CONAN_TOKEN="${CONAN_TOKEN:-}"

# Setup Conan environment
setup_conan() {
    log_info "Setting up Conan ${CONAN_VERSION}..."

    # Install Conan if not available
    if ! command -v conan &> /dev/null; then
        pip install conan==${CONAN_VERSION}
    fi

    # Configure Conan
    conan config set general.revisions_enabled=True
    conan config set general.default_profile=default
    conan config set core.upload:retry=3
    conan config set core.upload:retry_wait=10
    conan config set core.download:parallel=8

    # Detect and configure profile
    conan profile detect --force

    # Login if credentials provided
    if [[ -n "${CONAN_USER}" && -n "${CONAN_TOKEN}" ]]; then
        log_info "Logging in to ${CONAN_REMOTE} as ${CONAN_USER}"
        echo "${CONAN_TOKEN}" | conan remote login -p "${CONAN_TOKEN}" "${CONAN_REMOTE}" "${CONAN_USER}"
    fi

    log_success "Conan setup completed"
}

# Install dependencies with caching
conan_install_cached() {
    local conanfile="${1:-conanfile.py}"
    local profile="${2:-default}"
    local build_policy="${3:-missing}"

    log_info "Installing Conan dependencies..."
    log_info "  Conanfile: ${conanfile}"
    log_info "  Profile: ${profile}"
    log_info "  Build Policy: ${build_policy}"

    # Create cache key based on conanfile and profile
    local cache_key
    cache_key=$(sha256sum "${conanfile}" | cut -d' ' -f1)
    cache_key="${cache_key}_$(echo "${profile}" | sha256sum | cut -d' ' -f1)"

    # Try to restore cached installation
    if [[ -d ".conan_cache/${cache_key}" ]]; then
        log_info "Restoring cached Conan installation..."
        cp -r ".conan_cache/${cache_key}" .
    fi

    # Install dependencies
    conan install "${conanfile}" \
        --profile "${profile}" \
        --build="${build_policy}" \
        --update \
        --output-folder=.

    # Cache the installation
    mkdir -p .conan_cache
    cp -r .conan_cache/"${cache_key}" 2>/dev/null || true
    cp -r . ".conan_cache/${cache_key}"

    log_success "Conan dependencies installed"
}

# Build package
conan_build() {
    local conanfile="${1:-conanfile.py}"

    log_info "Building Conan package..."

    conan build "${conanfile}"

    log_success "Conan package built"
}

# Create and upload package
conan_create_upload() {
    local conanfile="${1:-conanfile.py}"
    local profile="${2:-default}"
    local remote="${3:-${CONAN_REMOTE}}"

    log_info "Creating and uploading Conan package..."
    log_info "  Remote: ${remote}"

    # Create package
    conan create "${conanfile}" --profile "${profile}"

    # Upload if we have credentials and remote is configured
    if [[ -n "${CONAN_USER}" && -n "${CONAN_TOKEN}" && "${remote}" != "conancenter" ]]; then
        log_info "Uploading package to ${remote}"
        conan upload "*" --remote "${remote}" --confirm
    fi

    log_success "Conan package created and uploaded"
}

# Generate SBOM (Software Bill of Materials)
generate_sbom() {
    local output_file="${1:-sbom.json}"
    local format="${2:-cyclonedx}"

    log_info "Generating Software Bill of Materials..."

    # Install CycloneDX tool if not available
    if ! command -v cyclonedx-conan &> /dev/null; then
        pip install cyclonedx-conan
    fi

    # Generate SBOM
    cyclonedx-conan \
        --conanfile conanfile.py \
        --output "${output_file}" \
        --format "${format}"

    log_success "SBOM generated: ${output_file}"
}

# Security scan dependencies
scan_dependencies() {
    log_info "Scanning dependencies for security issues..."

    # Check for known vulnerabilities
    conan inspect . > conan-inspect.txt

    # Look for security issues
    if grep -i -E "(vulnerable|exploit|cve|security)" conan-inspect.txt; then
        log_error "Security issues found in dependencies!"
        cat conan-inspect.txt
        return 1
    fi

    log_success "Dependency security scan passed"
}

# Clean Conan cache and artifacts
cleanup_conan() {
    log_info "Cleaning up Conan artifacts..."

    # Remove build artifacts
    rm -rf build/
    rm -rf .conan/

    # Clean old cache entries (keep last 5)
    if [[ -d ".conan_cache" ]]; then
        ls -t .conan_cache | tail -n +6 | xargs -I {} rm -rf .conan_cache/{}
    fi

    log_success "Conan cleanup completed"
}

# Get package information
get_package_info() {
    local conanfile="${1:-conanfile.py}"

    log_info "Extracting package information..."

    # Extract name and version from conanfile
    local name version
    name=$(grep -oP "name = \"\K[^\"]+" "${conanfile}")
    version=$(grep -oP "version = \"\K[^\"]+" "${conanfile}")

    echo "name=${name}"
    echo "version=${version}"

    # Export for GitHub Actions
    if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
        echo "package_name=${name}" >> "${GITHUB_OUTPUT}"
        echo "package_version=${version}" >> "${GITHUB_OUTPUT}"
    fi
}

# Main function dispatcher
main() {
    local command="${1:-help}"
    shift

    case "${command}" in
        setup)
            setup_conan "$@"
            ;;
        install)
            conan_install_cached "$@"
            ;;
        build)
            conan_build "$@"
            ;;
        create-upload)
            conan_create_upload "$@"
            ;;
        sbom)
            generate_sbom "$@"
            ;;
        scan)
            scan_dependencies "$@"
            ;;
        cleanup)
            cleanup_conan "$@"
            ;;
        info)
            get_package_info "$@"
            ;;
        help|--help|-h)
            echo "Conan CI/CD Helper Scripts"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  setup                    Setup Conan environment"
            echo "  install [conanfile] [profile] [build_policy]"
            echo "                           Install dependencies with caching"
            echo "  build [conanfile]        Build package"
            echo "  create-upload [conanfile] [profile] [remote]"
            echo "                           Create and upload package"
            echo "  sbom [output_file] [format]"
            echo "                           Generate Software Bill of Materials"
            echo "  scan                     Scan dependencies for security issues"
            echo "  cleanup                  Clean up Conan artifacts"
            echo "  info [conanfile]          Get package information"
            echo "  help                     Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  CONAN_VERSION           Conan version to install (default: 2.21.0)"
            echo "  CONAN_REMOTE           Conan remote to use (default: conancenter)"
            echo "  CONAN_USER             ConanCenter username"
            echo "  CONAN_TOKEN            ConanCenter token"
            ;;
        *)
            log_error "Unknown command: ${command}"
            log_info "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi