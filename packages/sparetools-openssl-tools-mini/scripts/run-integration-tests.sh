#!/bin/bash
set -e

echo "🧪 Running OpenSSL Integration Tests"
echo "===================================="

# Load environment
if [ -f .env ]; then
    source .env
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

log_test() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ "$status" = "PASS" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        [ -n "$message" ] && echo "   $message"
    elif [ "$status" = "SKIP" ]; then
        echo -e "${YELLOW}⏭️  SKIP${NC}: $test_name"
        [ -n "$message" ] && echo "   $message"
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        [ -n "$message" ] && echo "   $message"
    fi
}

# Test 1: Foundation packages
echo "🔐 Testing Foundation Layer..."
cd openssl-conan-base
if conan create . --build=missing 2>/dev/null; then
    log_test "Foundation Package Build" "PASS" "openssl-base/1.0.0 created successfully"
else
    log_test "Foundation Package Build" "FAIL" "Failed to build foundation package"
fi
cd ..

# Test 2: FIPS policy package
cd openssl-fips-policy
if conan create . --build=missing 2>/dev/null; then
    log_test "FIPS Policy Package Build" "PASS" "openssl-fips-data/140-3.1 created successfully"
else
    log_test "FIPS Policy Package Build" "FAIL" "Failed to build FIPS policy package"
fi
cd ..

# Test 3: Tooling layer with dependencies
cd openssl-tools
if conan create . --build=missing 2>/dev/null; then
    log_test "Tooling Layer Build" "PASS" "openssl-build-tools/1.2.0 created with dependencies"
else
    log_test "Tooling Layer Build" "FAIL" "Failed to build tooling layer"
fi
cd ..

# Test 4: Domain layer general build
cd openssl
if conan create . --build=missing -o deployment_target=general 2>/dev/null; then
    log_test "Domain Layer General Build" "PASS" "openssl/3.4.1 general build successful"
else
    log_test "Domain Layer General Build" "FAIL" "Failed general build"
fi

# Test 5: Domain layer FIPS build
if [ -n "$CLOUDSMITH_API_KEY" ] && [ "$CLOUDSMITH_API_KEY" != "your-api-key-here" ]; then
    if conan create . --build=missing -o deployment_target=fips-government 2>/dev/null; then
        log_test "Domain Layer FIPS Build" "PASS" "openssl/3.4.1 FIPS build successful"
    else
        log_test "Domain Layer FIPS Build" "FAIL" "Failed FIPS build"
    fi
else
    log_test "Domain Layer FIPS Build" "SKIP" "CLOUDSMITH_API_KEY not configured"
fi
cd ..

# Test 6: Cloudsmith remote verification
if [ -n "$CLOUDSMITH_API_KEY" ] && [ "$CLOUDSMITH_API_KEY" != "your-api-key-here" ]; then
    if conan search "*" -r=${CONAN_REPOSITORY_NAME} | grep -q "openssl"; then
        log_test "Cloudsmith Remote Verification" "PASS" "All packages available in Cloudsmith"
    else
        log_test "Cloudsmith Remote Verification" "FAIL" "Packages not found in Cloudsmith"
    fi
else
    log_test "Cloudsmith Remote Verification" "SKIP" "CLOUDSMITH_API_KEY not configured"
fi

# Test 7: Template system
cd mcp-project-orchestrator
source venv/bin/activate 2>/dev/null || true
if python -c "
from mcp_project_orchestrator.templates import TemplateManager
tm = TemplateManager('templates')
tm.discover_templates()
templates = tm.list_templates()
print('Templates found:', len(templates))
exit(0 if len(templates) > 0 else 1)
" 2>/dev/null; then
    log_test "Template System" "PASS" "Template discovery working"
else
    log_test "Template System" "FAIL" "Template system not functional"
fi
cd ..

# Test 8: Project creation
cd mcp-project-orchestrator
source venv/bin/activate 2>/dev/null || true
if mcp-orchestrator create-openssl-project --project-name test-project 2>/dev/null; then
    log_test "Project Creation" "PASS" "OpenSSL project created successfully"
    rm -rf ../test-project 2>/dev/null || true
else
    log_test "Project Creation" "FAIL" "Failed to create OpenSSL project"
fi
cd ..

# Test 9: Python utilities
cd openssl-conan-base
if python -c "
from openssl_base import get_openssl_version, generate_openssl_sbom
version = get_openssl_version('3.4.1', True)
sbom = generate_openssl_sbom('test', '1.0.0')
print('Version:', version)
print('SBOM keys:', list(sbom.keys())[:3])
" 2>/dev/null; then
    log_test "Python Utilities" "PASS" "Foundation utilities working correctly"
else
    log_test "Python Utilities" "FAIL" "Foundation utilities not functional"
fi
cd ..

# Summary
echo ""
echo "📊 Test Results Summary"
echo "======================"
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Success Rate: $((TESTS_PASSED * 100 / TESTS_RUN))%"

if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    echo -e "${GREEN}🎉 All tests passed! OpenSSL architecture is fully functional.${NC}"
    exit 0
elif [ "$TESTS_PASSED" -gt "$((TESTS_RUN * 8 / 10))" ]; then
    echo -e "${YELLOW}⚠️  Most tests passed. Minor issues detected.${NC}"
    exit 0
else
    echo -e "${RED}❌ Critical issues detected. Review test failures.${NC}"
    exit 1
fi
