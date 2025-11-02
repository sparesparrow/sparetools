#!/bin/bash

# SpareTools CI/CD Prerequisites Checker
# Validates that all required tools and configurations are present
#
# Usage: bash scripts/check-prerequisites.sh [--strict]
# --strict: Fail on any warning (not just errors)

set -e

STRICT_MODE=false
if [ "$1" = "--strict" ]; then
    STRICT_MODE=true
fi

echo "=========================================="
echo "SpareTools CI/CD Prerequisites Check"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
WARNED=0
FAILED=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNED++))
}

check_fail() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED++))
}

# Test: Git
echo "[1/10] Checking Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    GIT_MAJOR=$(echo $GIT_VERSION | cut -d. -f1)
    GIT_MINOR=$(echo $GIT_VERSION | cut -d. -f2)

    if [ $GIT_MAJOR -gt 2 ] || ([ $GIT_MAJOR -eq 2 ] && [ $GIT_MINOR -ge 30 ]); then
        check_pass "Git $GIT_VERSION (2.30+ required)"
    else
        check_warn "Git $GIT_VERSION (2.30+ recommended)"
    fi
else
    check_fail "Git not installed"
fi

# Test: GitHub CLI
echo ""
echo "[2/10] Checking GitHub CLI..."
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -1 | awk '{print $3}')
    check_pass "GitHub CLI $GH_VERSION"

    # Check authentication
    if gh auth status &>/dev/null; then
        GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
        check_pass "GitHub authenticated as: $GH_USER"
    else
        check_warn "GitHub CLI not authenticated - Run: gh auth login"
    fi
else
    check_fail "GitHub CLI not installed - Install from https://cli.github.com"
fi

# Test: Conan
echo ""
echo "[3/10] Checking Conan Package Manager..."
if command -v conan &> /dev/null; then
    CONAN_VERSION=$(conan --version | head -1 | awk '{print $NF}')
    CONAN_MAJOR=$(echo $CONAN_VERSION | cut -d. -f1)

    if [ $CONAN_MAJOR -ge 2 ]; then
        check_pass "Conan $CONAN_VERSION (2.0+ required)"

        # Check for profiles
        if [ -d "$HOME/.conan2" ]; then
            PROFILE_COUNT=$(find "$HOME/.conan2/profiles" -name "*.profile" 2>/dev/null | wc -l)
            if [ $PROFILE_COUNT -gt 0 ]; then
                check_pass "Found $PROFILE_COUNT Conan profiles"
            else
                check_warn "No Conan profiles found in ~/.conan2/profiles"
            fi
        fi
    else
        check_fail "Conan $CONAN_VERSION (2.0+ required)"
    fi
else
    check_fail "Conan not installed - Install: pip install conan>=2.0"
fi

# Test: CMake
echo ""
echo "[4/10] Checking CMake..."
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -1 | awk '{print $3}')
    CMAKE_MAJOR=$(echo $CMAKE_VERSION | cut -d. -f1)
    CMAKE_MINOR=$(echo $CMAKE_VERSION | cut -d. -f2)

    if [ $CMAKE_MAJOR -gt 3 ] || ([ $CMAKE_MAJOR -eq 3 ] && [ $CMAKE_MINOR -ge 22 ]); then
        check_pass "CMake $CMAKE_VERSION (3.22+ required)"
    else
        check_warn "CMake $CMAKE_VERSION (3.22+ recommended)"
    fi
else
    check_fail "CMake not installed - Install: apt-get install cmake (or brew, etc.)"
fi

# Test: Perl
echo ""
echo "[5/10] Checking Perl..."
if command -v perl &> /dev/null; then
    PERL_VERSION=$(perl -v | grep "version" | head -1 | awk '{print $4}')
    PERL_MAJOR=$(echo $PERL_VERSION | cut -d. -f1)
    PERL_MINOR=$(echo $PERL_VERSION | cut -d. -f2 | cut -c1-2)

    if [ $PERL_MAJOR -gt 5 ] || ([ $PERL_MAJOR -eq 5 ] && [ $PERL_MINOR -ge 30 ]); then
        check_pass "Perl $PERL_VERSION (5.30+ required)"

        # Check for critical Perl modules
        PERL_MODULES=()
        for module in "Data::Dumper" "File::Temp" "Text::Template"; do
            if perl -e "use $module" 2>/dev/null; then
                PERL_MODULES+=("$module")
            fi
        done

        if [ ${#PERL_MODULES[@]} -eq 3 ]; then
            check_pass "All critical Perl modules available"
        else
            check_warn "Some Perl modules missing: ${PERL_MODULES[@]}"
        fi
    else
        check_fail "Perl $PERL_VERSION (5.30+ required)"
    fi
else
    check_fail "Perl not installed"
fi

# Test: Python
echo ""
echo "[6/10] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 9 ]; then
        check_pass "Python $PYTHON_VERSION (3.9+ required)"

        # Check for key modules
        if python3 -c "import yaml" 2>/dev/null; then
            check_pass "PyYAML module available"
        else
            check_warn "PyYAML not installed (optional, for advanced automation)"
        fi
    else
        check_fail "Python $PYTHON_VERSION (3.9+ required)"
    fi
else
    check_fail "Python 3 not installed"
fi

# Test: Docker (optional but recommended)
echo ""
echo "[7/10] Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    check_pass "Docker $DOCKER_VERSION (optional, for multi-platform builds)"
else
    check_warn "Docker not installed (optional, for CI/CD multi-platform builds)"
fi

# Test: Repository Structure
echo ""
echo "[8/10] Checking Repository Structure..."

REQUIRED_DIRS=(
    "packages/sparetools-openssl"
    "profiles"
    "scripts"
    "docs"
    ".github/workflows"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory found: $dir"
    else
        check_fail "Missing directory: $dir"
    fi
done

# Test: Documentation Files
echo ""
echo "[9/10] Checking Documentation..."

REQUIRED_DOCS=(
    "CLAUDE.md"
    "docs/CI_CD_MODERNIZATION_GUIDE.md"
    "docs/IMPLEMENTATION_CHECKLIST.md"
    "docs/OPENSSL-360-BUILD-ANALYSIS.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        check_pass "Documentation: $doc ($LINES lines)"
    else
        check_warn "Missing documentation: $doc"
    fi
done

# Test: Git Configuration
echo ""
echo "[10/10] Checking Git Configuration..."

# Check for user.name and user.email
if git config user.name > /dev/null 2>&1; then
    GIT_USER=$(git config user.name)
    check_pass "Git user configured: $GIT_USER"
else
    check_warn "Git user.name not configured - Run: git config --global user.name 'Your Name'"
fi

if git config user.email > /dev/null 2>&1; then
    GIT_EMAIL=$(git config user.email)
    check_pass "Git email configured: $GIT_EMAIL"
else
    check_warn "Git user.email not configured - Run: git config --global user.email 'your@email.com'"
fi

# Check for .github/workflows directory
if [ -d ".github/workflows" ]; then
    WORKFLOW_COUNT=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
    check_pass "Found $WORKFLOW_COUNT GitHub Actions workflows"
else
    check_warn "No .github/workflows directory found"
fi

# Summary
echo ""
echo "=========================================="
echo "Prerequisites Check Summary"
echo "=========================================="
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${YELLOW}Warned:${NC}  $WARNED"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo ""

# Determine exit status
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ FAILED${NC}: Please install missing prerequisites"
    exit 1
elif [ $WARNED -gt 0 ] && [ "$STRICT_MODE" = true ]; then
    echo -e "${YELLOW}⚠ WARNINGS${NC}: Some recommendations not met (strict mode)"
    exit 1
elif [ $WARNED -gt 0 ]; then
    echo -e "${YELLOW}✓ PASSED${NC} (with $WARNED recommendations)"
    echo ""
    echo "Recommendations:"
    echo "  - Install/update missing tools listed above"
    echo "  - Configure missing Git settings"
    echo "  - Review optional components (Docker, PyYAML)"
    echo ""
    exit 0
else
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your environment is ready for CI/CD deployment!"
    echo "Next: bash scripts/setup-documentation.sh"
    echo ""
    exit 0
fi
