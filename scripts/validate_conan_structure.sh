#!/bin/bash
set -euo pipefail

# Validate Conan package structure across the repository
# Ensures all packages have proper conanfile.py files and valid references

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 Validating Conan package structure..."

ERRORS=0

# Check every expected package directory has conanfile.py
EXPECTED_PACKAGES=(
    "packages/foundation/sparetools-base"
    "packages/foundation/sparetools-cpython"
    "packages/foundation/sparetools-bootstrap"
    "packages/foundation/sparetools-shared-dev-tools"
    "packages/foundation/sparetools-test-framework"
    "packages/foundation/sparetools-test-harness"
    "packages/consumers/openssl/sparetools-openssl"
    "packages/consumers/openssl/sparetools-openssl-tools"
)

for package_dir in "${EXPECTED_PACKAGES[@]}"; do
    conanfile="$REPO_ROOT/$package_dir/conanfile.py"
    if [[ ! -f "$conanfile" ]]; then
        echo "❌ Missing conanfile.py in $package_dir"
        ERRORS=$((ERRORS + 1))
    else
        # Basic syntax check
        if ! python3 -c "import ast; ast.parse(open('$conanfile').read())" 2>/dev/null; then
            echo "❌ Syntax error in $conanfile"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# Validate version references in conanfile.py files
echo "🔍 Checking version references..."

find "$REPO_ROOT" -name "conanfile.py" -type f | while read -r conanfile; do
    # Check for outdated version references
    if grep -q "sparetools-base/2\.0\.0" "$conanfile"; then
        echo "❌ Outdated version reference in $conanfile"
        echo "   Found: sparetools-base/2.0.0 (should be 2.0.3)"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for invalid package references
    if grep -q "sparesparrow-protocols" "$conanfile"; then
        echo "❌ Invalid package reference in $conanfile"
        echo "   Found: sparesparrow-protocols (should be sparetools-protocols)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for VERSION file consistency
VERSION_FILE="$REPO_ROOT/VERSION"
if [[ -f "$VERSION_FILE" ]]; then
    VERSION_CONTENT=$(cat "$VERSION_FILE" | tr -d '\n')
    if [[ "$VERSION_CONTENT" != "2.0.3" ]]; then
        echo "❌ VERSION file contains incorrect version: $VERSION_CONTENT (expected: 2.0.3)"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "⚠️  VERSION file not found"
fi

# Summary
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ Conan structure validation passed"
    exit 0
else
    echo "❌ Conan structure validation failed with $ERRORS errors"
    echo ""
    echo "💡 Fix issues and run validation again:"
    echo "   ./scripts/validate_conan_structure.sh"
    exit 1
fi