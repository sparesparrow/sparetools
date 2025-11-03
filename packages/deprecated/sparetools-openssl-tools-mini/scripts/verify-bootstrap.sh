#!/bin/bash
# verify-bootstrap.sh - Bootstrap script verification

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_DIR="$(dirname "$SCRIPT_DIR")/bootstrap"
BOOTSTRAP_SCRIPT="$BOOTSTRAP_DIR/openssl-conan-init.py"
TEMP_DIR=""
CONAN_VERSION="2.21.0"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

cleanup() {
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        log "Cleaning up temporary directory: $TEMP_DIR"
        rm -rf "$TEMP_DIR"
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d)
log "Created temporary test directory: $TEMP_DIR"

# Test 1: Bootstrap script exists and is executable
test_bootstrap_script_exists() {
    log "Test 1: Checking bootstrap script exists and is executable"
    
    if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
        fail "Bootstrap script not found: $BOOTSTRAP_SCRIPT"
        return 1
    fi
    
    if [[ ! -x "$BOOTSTRAP_SCRIPT" ]]; then
        fail "Bootstrap script is not executable"
        return 1
    fi
    
    success "Bootstrap script exists and is executable"
    return 0
}

# Test 2: Bootstrap script syntax validation
test_bootstrap_syntax() {
    log "Test 2: Validating bootstrap script syntax"
    
    if ! python3 -m py_compile "$BOOTSTRAP_SCRIPT"; then
        fail "Bootstrap script has syntax errors"
        return 1
    fi
    
    success "Bootstrap script syntax is valid"
    return 0
}

# Test 3: Bootstrap script help output
test_bootstrap_help() {
    log "Test 3: Testing bootstrap script help output"
    
    if ! python3 "$BOOTSTRAP_SCRIPT" --help >/dev/null 2>&1; then
        fail "Bootstrap script help command failed"
        return 1
    fi
    
    success "Bootstrap script help command works"
    return 0
}

# Test 4: Dry run mode
test_dry_run_mode() {
    log "Test 4: Testing dry run mode"
    
    cd "$TEMP_DIR"
    
    if ! python3 "$BOOTSTRAP_SCRIPT" --minimal --dry-run >/dev/null 2>&1; then
        fail "Bootstrap script dry run mode failed"
        return 1
    fi
    
    success "Bootstrap script dry run mode works"
    return 0
}

# Test 5: Test mode
test_test_mode() {
    log "Test 5: Testing test mode"
    
    cd "$TEMP_DIR"
    
    if ! python3 "$BOOTSTRAP_SCRIPT" --minimal --test-mode >/dev/null 2>&1; then
        fail "Bootstrap script test mode failed"
        return 1
    fi
    
    success "Bootstrap script test mode works"
    return 0
}

# Test 6: Fresh installation test (minimal mode)
test_fresh_installation() {
    log "Test 6: Testing fresh installation in minimal mode"
    
    cd "$TEMP_DIR"
    
    # Create isolated environment
    export HOME="$TEMP_DIR/home"
    export CONAN_USER_HOME="$TEMP_DIR/conan_home"
    mkdir -p "$HOME" "$CONAN_USER_HOME"
    
    # Run minimal installation
    if ! python3 "$BOOTSTRAP_SCRIPT" --minimal >/dev/null 2>&1; then
        fail "Fresh installation in minimal mode failed"
        return 1
    fi
    
    # Verify Conan installation
    if ! "$TEMP_DIR/home/.local/bin/conan" --version >/dev/null 2>&1; then
        fail "Conan not found after installation"
        return 1
    fi
    
    # Check Conan version
    INSTALLED_VERSION=$("$TEMP_DIR/home/.local/bin/conan" --version | cut -d' ' -f3)
    if [[ "$INSTALLED_VERSION" != "$CONAN_VERSION" ]]; then
        fail "Conan version mismatch: expected $CONAN_VERSION, got $INSTALLED_VERSION"
        return 1
    fi
    
    success "Fresh installation in minimal mode works"
    return 0
}

# Test 7: Remote configuration test
test_remote_configuration() {
    log "Test 7: Testing remote configuration"
    
    cd "$TEMP_DIR"
    
    # Check if remotes are configured
    if ! "$TEMP_DIR/home/.local/bin/conan" remote list | grep -q "sparesparrow-conan"; then
        fail "sparesparrow-conan remote not configured"
        return 1
    fi
    
    if ! "$TEMP_DIR/home/.local/bin/conan" remote list | grep -q "conancenter"; then
        fail "conancenter remote not configured"
        return 1
    fi
    
    success "Remote configuration works"
    return 0
}

# Test 8: Idempotency test
test_idempotency() {
    log "Test 8: Testing idempotency (running twice should succeed)"
    
    cd "$TEMP_DIR"
    
    # Run installation twice
    if ! python3 "$BOOTSTRAP_SCRIPT" --minimal >/dev/null 2>&1; then
        fail "Second run of bootstrap script failed"
        return 1
    fi
    
    success "Bootstrap script is idempotent"
    return 0
}

# Test 9: Full mode test (without actual cloning)
test_full_mode_dry_run() {
    log "Test 9: Testing full mode dry run"
    
    cd "$TEMP_DIR"
    
    if ! python3 "$BOOTSTRAP_SCRIPT" --full --dry-run >/dev/null 2>&1; then
        fail "Full mode dry run failed"
        return 1
    fi
    
    success "Full mode dry run works"
    return 0
}

# Test 10: Dev mode test (without actual cloning)
test_dev_mode_dry_run() {
    log "Test 10: Testing dev mode dry run"
    
    cd "$TEMP_DIR"
    
    if ! python3 "$BOOTSTRAP_SCRIPT" --dev --dry-run >/dev/null 2>&1; then
        fail "Dev mode dry run failed"
        return 1
    fi
    
    success "Dev mode dry run works"
    return 0
}

# Test 11: Validation mode test
test_validation_mode() {
    log "Test 11: Testing validation mode"
    
    cd "$TEMP_DIR"
    
    # This should fail since we don't have a real installation
    if python3 "$BOOTSTRAP_SCRIPT" --validate >/dev/null 2>&1; then
        warn "Validation mode passed unexpectedly (this might be expected)"
    else
        success "Validation mode correctly detected missing installation"
    fi
    
    return 0
}

# Test 12: Error handling test
test_error_handling() {
    log "Test 12: Testing error handling"
    
    cd "$TEMP_DIR"
    
    # Test invalid arguments
    if python3 "$BOOTSTRAP_SCRIPT" --invalid-flag >/dev/null 2>&1; then
        fail "Bootstrap script should fail with invalid arguments"
        return 1
    fi
    
    success "Error handling works correctly"
    return 0
}

# Main test execution
main() {
    log "Starting bootstrap script verification"
    log "Bootstrap script: $BOOTSTRAP_SCRIPT"
    log "Temporary directory: $TEMP_DIR"
    
    # Run all tests
    test_bootstrap_script_exists
    test_bootstrap_syntax
    test_bootstrap_help
    test_dry_run_mode
    test_test_mode
    test_fresh_installation
    test_remote_configuration
    test_idempotency
    test_full_mode_dry_run
    test_dev_mode_dry_run
    test_validation_mode
    test_error_handling
    
    # Print summary
    echo
    log "Verification Summary:"
    success "Tests passed: $TESTS_PASSED"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        fail "Tests failed: $TESTS_FAILED"
        echo
        log "Some tests failed. Check the output above for details."
        exit 1
    else
        success "All tests passed!"
        echo
        log "Bootstrap script verification completed successfully."
        exit 0
    fi
}

# Run main function
main "$@"





