#!/bin/bash

# SpareTools CI/CD Setup Validation Script
# Comprehensively validates that all CI/CD components are properly configured
#
# Usage: bash scripts/validate-ci-setup.sh [--fix] [--verbose]
#
# --fix: Attempt to fix detected issues automatically
# --verbose: Show detailed diagnostic information

set -e

FIX_ISSUES=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_ISSUES=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "SpareTools CI/CD Setup Validation"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_FIXED=0
CHECKS_WARNING=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++))
}

fixed() {
    echo -e "${BLUE}🔧${NC} Fixed: $1"
    ((CHECKS_FIXED++))
}

verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "    ℹ $1"
    fi
}

# ==============================================================================
# CHECK GROUP 1: GitHub Workflows
# ==============================================================================

echo "[1/6] Validating GitHub Workflows..."
echo ""

WORKFLOW_DIR=".github/workflows"
if [ ! -d "$WORKFLOW_DIR" ]; then
    fail "Directory not found: $WORKFLOW_DIR"
    mkdir -p "$WORKFLOW_DIR" && fixed "Created $WORKFLOW_DIR"
else
    pass "Workflow directory exists"
fi

# Check for required workflows
REQUIRED_WORKFLOWS=(
    "openssl-analysis.yml"
    "build-test.yml"
    "integration.yml"
)

WORKFLOWS_FOUND=0
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOW_DIR/$workflow" ]; then
        pass "Found: $workflow"
        ((WORKFLOWS_FOUND++))

        # Validate YAML syntax
        if python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_DIR/$workflow'))" 2>/dev/null; then
            verbose "Valid YAML syntax"
        else
            warn "Invalid YAML syntax: $workflow"
        fi

        # Check file size
        SIZE=$(stat -f%z "$WORKFLOW_DIR/$workflow" 2>/dev/null || stat -c%s "$WORKFLOW_DIR/$workflow" 2>/dev/null)
        if [ $SIZE -gt 1000 ]; then
            verbose "File size: $((SIZE / 1024)) KB"
        else
            warn "Workflow file seems small: $workflow ($SIZE bytes)"
        fi
    else
        warn "Missing workflow: $workflow"
    fi
done

if [ $WORKFLOWS_FOUND -lt 3 ]; then
    fail "Only found $WORKFLOWS_FOUND of 3 required workflows"
fi

# ==============================================================================
# CHECK GROUP 2: CLAUDE.md Documentation
# ==============================================================================

echo ""
echo "[2/6] Validating CLAUDE.md Documentation..."
echo ""

# Main CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    LINES=$(wc -l < "CLAUDE.md")
    if [ $LINES -gt 100 ]; then
        pass "CLAUDE.md exists ($LINES lines)"
    else
        warn "CLAUDE.md seems small ($LINES lines)"
    fi
else
    fail "CLAUDE.md not found in root"
fi

# Docs directory CLAUDE.md files
DOC_CLAUDE_FILES=(
    "docs/CI_CD_MODERNIZATION_GUIDE.md"
    "docs/OPENSSL-360-BUILD-ANALYSIS.md"
    "docs/IMPLEMENTATION_CHECKLIST.md"
)

for doc in "${DOC_CLAUDE_FILES[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        pass "Documentation: $doc ($LINES lines)"
    else
        warn "Missing documentation: $doc"
    fi
done

# Check local clones
CLONE_BASE="_local-clones"
if [ -d "$CLONE_BASE" ]; then
    pass "Clone base directory exists: $CLONE_BASE"

    # Check for CLAUDE.md in clones
    for repo in "cpy-local" "openssl-tools-local" "openssl-local"; do
        if [ -f "$CLONE_BASE/$repo/CLAUDE.md" ]; then
            LINES=$(wc -l < "$CLONE_BASE/$repo/CLAUDE.md")
            pass "Deployed: $CLONE_BASE/$repo/CLAUDE.md ($LINES lines)"
        else
            warn "Not deployed: $CLONE_BASE/$repo/CLAUDE.md"
        fi
    done
else
    warn "Clone base directory not found: $CLONE_BASE"
fi

# ==============================================================================
# CHECK GROUP 3: Repository Structure
# ==============================================================================

echo ""
echo "[3/6] Validating Repository Structure..."
echo ""

REQUIRED_DIRS=(
    "packages/sparetools-openssl"
    "profiles"
    "scripts"
    "docs"
    ".github"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        pass "Directory exists: $dir"
        verbose "Path: $(pwd)/$dir"
    else
        fail "Missing directory: $dir"
    fi
done

# Check for key files
REQUIRED_FILES=(
    "conanfile.py"
    "packages/sparetools-openssl/conanfile.py"
    ".clang-tidy"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "File exists: $file"
    else
        warn "Missing file: $file"
    fi
done

# ==============================================================================
# CHECK GROUP 4: Conan Configuration
# ==============================================================================

echo ""
echo "[4/6] Validating Conan Configuration..."
echo ""

# Check Conan installation
if command -v conan &> /dev/null; then
    CONAN_VERSION=$(conan --version | head -1 | awk '{print $NF}')
    CONAN_MAJOR=$(echo $CONAN_VERSION | cut -d. -f1)

    if [ $CONAN_MAJOR -ge 2 ]; then
        pass "Conan $CONAN_VERSION installed"
    else
        fail "Conan $CONAN_VERSION (2.0+ required)"
    fi
else
    fail "Conan not installed"
fi

# Check Conan home
CONAN_HOME="${CONAN_HOME:=$HOME/.conan2}"
if [ -d "$CONAN_HOME" ]; then
    pass "Conan home exists: $CONAN_HOME"

    # Check for profiles
    PROFILES_DIR="$CONAN_HOME/profiles"
    if [ -d "$PROFILES_DIR" ]; then
        PROFILE_COUNT=$(find "$PROFILES_DIR" -maxdepth 1 -type f | wc -l)
        if [ $PROFILE_COUNT -gt 0 ]; then
            pass "Found $PROFILE_COUNT Conan profiles"
            verbose "Profiles directory: $PROFILES_DIR"
        else
            warn "No profiles found in: $PROFILES_DIR"
        fi
    else
        warn "Profiles directory not found: $PROFILES_DIR"
    fi
else
    fail "Conan home not found: $CONAN_HOME"
fi

# Check for project profiles
if [ -d "profiles" ]; then
    PROJECT_PROFILES=$(find profiles -name "*.profile" 2>/dev/null | wc -l)
    if [ $PROJECT_PROFILES -gt 0 ]; then
        pass "Found $PROJECT_PROFILES project profiles"
    else
        warn "No profiles found in projects/profiles/ directory"
    fi
fi

# ==============================================================================
# CHECK GROUP 5: Git Configuration
# ==============================================================================

echo ""
echo "[5/6] Validating Git Configuration..."
echo ""

# Check git repo
if [ -d ".git" ]; then
    pass "Git repository initialized"

    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    verbose "Current branch: $CURRENT_BRANCH"

    # Check for remote
    if git remote get-url origin > /dev/null 2>&1; then
        REMOTE=$(git remote get-url origin)
        pass "Remote configured: $REMOTE"
    else
        warn "No remote configured"
    fi
else
    fail "Not a git repository (no .git directory)"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    pass ".gitignore exists"

    # Check for important entries
    if grep -q "^_local-clones" .gitignore 2>/dev/null; then
        pass "_local-clones excluded from git"
    else
        warn "_local-clones not in .gitignore (should be excluded)"

        if [ "$FIX_ISSUES" = true ]; then
            echo "" >> .gitignore
            echo "# Local clones with CLAUDE.md" >> .gitignore
            echo "_local-clones/" >> .gitignore
            fixed "Added _local-clones to .gitignore"
        fi
    fi
else
    fail ".gitignore not found"
fi

# Check git config
if git config user.name > /dev/null 2>&1; then
    GIT_USER=$(git config user.name)
    pass "Git user configured: $GIT_USER"
else
    warn "Git user.name not configured"
fi

# ==============================================================================
# CHECK GROUP 6: GitHub Integration
# ==============================================================================

echo ""
echo "[6/6] Validating GitHub Integration..."
echo ""

# Check GitHub CLI
if command -v gh &> /dev/null; then
    pass "GitHub CLI installed"

    # Check authentication
    if gh auth status &>/dev/null; then
        GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
        pass "GitHub authenticated as: $GH_USER"

        # Check repository access
        if gh repo view &>/dev/null; then
            GH_REPO=$(gh repo view --json nameWithOwner -q)
            pass "Repository access verified: $GH_REPO"
        else
            fail "Cannot access GitHub repository"
        fi
    else
        warn "GitHub CLI not authenticated - Run: gh auth login"
    fi
else
    warn "GitHub CLI not installed"
fi

# ==============================================================================
# Summary and Recommendations
# ==============================================================================

echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo ""

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))

echo "Results:"
echo -e "  ${GREEN}Passed:${NC}   $CHECKS_PASSED"
echo -e "  ${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "  ${RED}Failed:${NC}    $CHECKS_FAILED"

if [ $CHECKS_FIXED -gt 0 ]; then
    echo -e "  ${BLUE}Fixed:${NC}    $CHECKS_FIXED"
fi

echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
        echo ""
        echo "Your CI/CD setup is complete and ready!"
        echo ""
        echo "Next steps:"
        echo "  1. Commit changes: git add . && git commit -m 'ci: complete CI/CD setup'"
        echo "  2. Push to develop: git push origin develop"
        echo "  3. Monitor workflows: gh run watch -w openssl-analysis.yml"
        echo "  4. Check artifacts: gh run list --limit 5"
        exit 0
    else
        echo -e "${YELLOW}⚠ PASSED with WARNINGS${NC}"
        echo ""
        echo "Your CI/CD setup is mostly complete, but has some recommendations:"
        echo "  - Address warnings above"
        echo "  - Rerun: bash scripts/validate-ci-setup.sh --verbose"
        exit 0
    fi
else
    echo -e "${RED}✗ VALIDATION FAILED${NC}"
    echo ""
    echo "There are critical issues that need to be resolved:"
    echo "  - Address failures above"
    echo "  - Refer to docs/IMPLEMENTATION_CHECKLIST.md for guidance"

    if [ "$FIX_ISSUES" = false ]; then
        echo ""
        echo "Attempt automatic fixes:"
        echo "  bash scripts/validate-ci-setup.sh --fix"
    fi
    exit 1
fi
