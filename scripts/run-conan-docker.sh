#!/bin/bash
# Script to run Conan commands in Docker environment
# Usage: ./scripts/run-conan-docker.sh [conan command args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if the container is running
check_container() {
    if ! docker ps --format 'table {{.Names}}' | grep -q "^sparetools-conan$"; then
        log_warning "Conan container is not running. Starting it..."
        start_container
    fi
}

# Start the Conan container
start_container() {
    log_info "Starting Conan Docker environment..."

    # Ensure the image is built
    if ! docker images sparetools-conan-env --format "{{.Repository}}" | grep -q "sparetools-conan-env"; then
        log_info "Building Conan Docker image..."
        docker build -f Dockerfile.conan -t sparetools-conan-env .
    fi

    # Start the container
    docker run -d \
        --name sparetools-conan \
        --volume "$WORKSPACE_ROOT:/workspace" \
        --volume "sparetools-conan-cache:/home/conan/.conan2" \
        --workdir /workspace \
        --env CONAN_NON_INTERACTIVE=true \
        --env "CLOUDSMITH_API_KEY=${CLOUDSMITH_API_KEY:-}" \
        --rm \
        sparetools-conan-env \
        tail -f /dev/null

    # Wait for container to be healthy
    log_info "Waiting for container to be ready..."
    for i in {1..30}; do
        if docker exec sparetools-conan conan --version >/dev/null 2>&1; then
            log_success "Conan container is ready!"
            return 0
        fi
        sleep 2
    done

    log_error "Container failed to start properly"
    exit 1
}

# Execute Conan command in container
run_conan_command() {
    log_info "Running: conan $@"

    if ! docker exec -t sparetools-conan conan "$@"; then
        log_error "Conan command failed"
        exit 1
    fi
}

# Main execution
main() {
    check_docker
    check_container

    if [ $# -eq 0 ]; then
        log_info "No Conan command provided. Entering interactive shell..."
        docker exec -it sparetools-conan /bin/bash
    else
        run_conan_command "$@"
    fi
}

# Show usage if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "SpareTools Conan Docker Runner"
    echo ""
    echo "Usage:"
    echo "  $0 [conan command args...]"
    echo "  $0                    # Enter interactive shell"
    echo ""
    echo "Examples:"
    echo "  $0 --version"
    echo "  $0 list 'sparetools-*'"
    echo "  $0 create packages/foundation/sparetools-base --version=2.0.3"
    echo "  $0 upload 'sparetools-*/*' -r sparesparrow-conan --confirm"
    echo ""
    exit 0
fi

main "$@"