#!/bin/bash
# Master validation script that runs all validation scripts
# Aggregates results and exits with appropriate code
# Can be used in CI/CD

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
FAILED=0
PASSED=0
WARNINGS=0

echo "=========================================="
echo "SpareTools Master Validation Suite"
echo "=========================================="
echo ""

# Function to run a validation script
run_validation() {
    local script_name=$1
    local script_path=$2
    local description=$3
    
    echo "Running: $description"
    echo "----------------------------------------"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${YELLOW}⚠️  Script not found: $script_path${NC}"
        ((WARNINGS++))
        return 1
    fi
    
    # Make executable if needed
    chmod +x "$script_path" 2>/dev/null || true
    
    # Run the script
    if python3 "$script_path" 2>&1; then
        echo -e "${GREEN}✅ PASSED: $description${NC}"
        echo ""
        ((PASSED++))
        return 0
    else
        local exit_code=$?
        echo -e "${RED}❌ FAILED: $description (exit code: $exit_code)${NC}"
        echo ""
        ((FAILED++))
        return 1
    fi
}

# Function to run shell script validation
run_shell_validation() {
    local script_name=$1
    local script_path=$2
    local description=$3
    
    echo "Running: $description"
    echo "----------------------------------------"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${YELLOW}⚠️  Script not found: $script_path${NC}"
        ((WARNINGS++))
        return 1
    fi
    
    # Make executable if needed
    chmod +x "$script_path" 2>/dev/null || true
    
    # Run the script
    if bash "$script_path" 2>&1; then
        echo -e "${GREEN}✅ PASSED: $description${NC}"
        echo ""
        ((PASSED++))
        return 0
    else
        local exit_code=$?
        echo -e "${RED}❌ FAILED: $description (exit code: $exit_code)${NC}"
        echo ""
        ((FAILED++))
        return 1
    fi
}

# 1. Conan recipe audit
run_validation \
    "audit-conan-recipes.py" \
    "$SCRIPT_DIR/audit-conan-recipes.py" \
    "Conan Recipe Audit"

# 2. OpenSSL compatibility validation
run_validation \
    "validate-openssl-compatibility.py" \
    "$SCRIPT_DIR/validate-openssl-compatibility.py" \
    "OpenSSL 3.3.2 Compatibility Validation"

# 3. Conan-Python integration validation
run_validation \
    "validate-conan-python-integration.py" \
    "$REPO_ROOT/validate-conan-python-integration.py" \
    "Conan-Python Integration Validation"

# 4. SpareTools OpenSSL validation
run_validation \
    "validate-sparetools-openssl.py" \
    "$REPO_ROOT/validate-sparetools-openssl.py" \
    "SpareTools OpenSSL Validation"

# Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi
echo ""

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Validation failed!${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with warnings${NC}"
    exit 0
else
    echo -e "${GREEN}✅ All validations passed!${NC}"
    exit 0
fi
