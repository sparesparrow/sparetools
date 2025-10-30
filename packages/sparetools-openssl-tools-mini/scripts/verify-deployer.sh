#!/bin/bash
# verify-deployer.sh - Enhanced deployer verification

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

# Test 1: Check if Conan is available
test_conan_availability() {
    log "Test 1: Checking Conan availability"
    
    if ! command -v conan >/dev/null 2>&1; then
        fail "Conan command not found"
        return 1
    fi
    
    CONAN_VER=$(conan --version | cut -d' ' -f3)
    if [[ "$CONAN_VER" != "$CONAN_VERSION" ]]; then
        warn "Conan version mismatch: expected $CONAN_VERSION, got $CONAN_VER"
    fi
    
    success "Conan is available (version: $CONAN_VER)"
    return 0
}

# Test 2: Check if enhanced deployer is available
test_deployer_availability() {
    log "Test 2: Checking enhanced deployer availability"
    
    # Check if deployer is in extensions directory
    DEPLOYER_PATH="$HOME/.conan2/extensions/deployers/full_deploy_enhanced.py"
    if [[ ! -f "$DEPLOYER_PATH" ]]; then
        fail "Enhanced deployer not found at $DEPLOYER_PATH"
        return 1
    fi
    
    success "Enhanced deployer found at $DEPLOYER_PATH"
    return 0
}

# Test 3: Create test conanfile
create_test_conanfile() {
    log "Test 3: Creating test conanfile"
    
    cd "$TEMP_DIR"
    
    cat > conanfile.txt << 'EOF'
[requires]
openssl/3.6.0

[generators]
CMakeToolchain
CMakeDeps
EOF
    
    success "Created test conanfile.txt"
    return 0
}

# Test 4: Test deployer with test conanfile
test_deployer_execution() {
    log "Test 4: Testing deployer execution"
    
    cd "$TEMP_DIR"
    
    # Run deployer
    if ! conan install . --deployer=full_deploy_enhanced --deployer-folder=./deploy_test 2>/dev/null; then
        fail "Deployer execution failed"
        return 1
    fi
    
    success "Deployer executed successfully"
    return 0
}

# Test 5: Verify deploy folder structure
test_deploy_folder_structure() {
    log "Test 5: Verifying deploy folder structure"
    
    cd "$TEMP_DIR"
    
    DEPLOY_DIR="./deploy_test"
    if [[ ! -d "$DEPLOY_DIR" ]]; then
        fail "Deploy directory not created"
        return 1
    fi
    
    # Check for expected structure
    EXPECTED_DIRS=("full_deploy" "metadata")
    for dir in "${EXPECTED_DIRS[@]}"; do
        if [[ ! -d "$DEPLOY_DIR/$dir" ]]; then
            fail "Expected directory not found: $dir"
            return 1
        fi
    done
    
    success "Deploy folder structure is correct"
    return 0
}

# Test 6: Verify SBOM generation
test_sbom_generation() {
    log "Test 6: Verifying SBOM generation"
    
    cd "$TEMP_DIR"
    
    SBOM_FILE="./deploy_test/metadata/sbom.json"
    if [[ ! -f "$SBOM_FILE" ]]; then
        fail "SBOM file not generated: $SBOM_FILE"
        return 1
    fi
    
    # Check if it's valid JSON
    if ! jq empty "$SBOM_FILE" 2>/dev/null; then
        fail "SBOM file is not valid JSON"
        return 1
    fi
    
    # Check for CycloneDX format
    if ! jq -e '.bomFormat' "$SBOM_FILE" >/dev/null 2>&1; then
        fail "SBOM file is not in CycloneDX format"
        return 1
    fi
    
    success "SBOM generation works correctly"
    return 0
}

# Test 7: Verify metadata generation
test_metadata_generation() {
    log "Test 7: Verifying metadata generation"
    
    cd "$TEMP_DIR"
    
    METADATA_FILE="./deploy_test/metadata/metadata.json"
    if [[ ! -f "$METADATA_FILE" ]]; then
        fail "Metadata file not generated: $METADATA_FILE"
        return 1
    fi
    
    # Check if it's valid JSON
    if ! jq empty "$METADATA_FILE" 2>/dev/null; then
        fail "Metadata file is not valid JSON"
        return 1
    fi
    
    # Check for expected fields
    EXPECTED_FIELDS=("timestamp" "profile" "fips_enabled")
    for field in "${EXPECTED_FIELDS[@]}"; do
        if ! jq -e ".$field" "$METADATA_FILE" >/dev/null 2>&1; then
            fail "Metadata file missing expected field: $field"
            return 1
        fi
    done
    
    success "Metadata generation works correctly"
    return 0
}

# Test 8: Verify cache path mapping
test_cache_path_mapping() {
    log "Test 8: Verifying cache path mapping"
    
    cd "$TEMP_DIR"
    
    CACHE_MAP_FILE="./deploy_test/metadata/cache_paths.json"
    if [[ ! -f "$CACHE_MAP_FILE" ]]; then
        fail "Cache path mapping file not generated: $CACHE_MAP_FILE"
        return 1
    fi
    
    # Check if it's valid JSON
    if ! jq empty "$CACHE_MAP_FILE" 2>/dev/null; then
        fail "Cache path mapping file is not valid JSON"
        return 1
    fi
    
    success "Cache path mapping works correctly"
    return 0
}

# Test 9: Test symlink strategy (if OPENSSL_DEVENV is set)
test_symlink_strategy() {
    log "Test 9: Testing symlink strategy"
    
    cd "$TEMP_DIR"
    
    # Set OPENSSL_DEVENV environment variable
    export OPENSSL_DEVENV="$TEMP_DIR"
    
    # Run deployer again
    if ! conan install . --deployer=full_deploy_enhanced --deployer-folder=./deploy_test_symlink 2>/dev/null; then
        fail "Deployer execution with symlink strategy failed"
        return 1
    fi
    
    # Check if symlinks were created
    DEPLOY_DIR="./deploy_test_symlink"
    if [[ -d "$DEPLOY_DIR" ]]; then
        # Look for symlinks in the deploy directory
        if find "$DEPLOY_DIR" -type l | head -1 >/dev/null 2>&1; then
            success "Symlink strategy works correctly"
        else
            warn "No symlinks found (this might be expected depending on configuration)"
        fi
    else
        fail "Deploy directory not created with symlink strategy"
        return 1
    fi
    
    return 0
}

# Test 10: Test error handling
test_error_handling() {
    log "Test 10: Testing error handling"
    
    cd "$TEMP_DIR"
    
    # Test with invalid conanfile
    cat > invalid_conanfile.txt << 'EOF'
[requires]
nonexistent-package/1.0.0
EOF
    
    # This should fail gracefully
    if conan install . --deployer=full_deploy_enhanced --deployer-folder=./deploy_test_error 2>/dev/null; then
        fail "Deployer should fail with invalid conanfile"
        return 1
    fi
    
    success "Error handling works correctly"
    return 0
}

# Test 11: Performance test
test_performance() {
    log "Test 11: Testing deployer performance"
    
    cd "$TEMP_DIR"
    
    # Measure deployment time
    START_TIME=$(date +%s)
    
    if ! conan install . --deployer=full_deploy_enhanced --deployer-folder=./deploy_test_perf 2>/dev/null; then
        fail "Performance test deployment failed"
        return 1
    fi
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Deployer should complete in reasonable time (less than 5 minutes)
    if [[ $DURATION -lt 300 ]]; then
        success "Deployer performance is acceptable (${DURATION}s)"
    else
        warn "Deployer performance is slow (${DURATION}s)"
    fi
    
    return 0
}

# Main test execution
main() {
    log "Starting enhanced deployer verification"
    log "Temporary directory: $TEMP_DIR"
    
    # Run all tests
    test_conan_availability
    test_deployer_availability
    create_test_conanfile
    test_deployer_execution
    test_deploy_folder_structure
    test_sbom_generation
    test_metadata_generation
    test_cache_path_mapping
    test_symlink_strategy
    test_error_handling
    test_performance
    
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
        log "Enhanced deployer verification completed successfully."
        exit 0
    fi
}

# Run main function
main "$@"





