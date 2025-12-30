#!/bin/bash
set -euo pipefail

# SpareTools Version Synchronization Script
# Fixes VERSION_BASE mismatch between CI workflows and packages
#
# Usage: ./scripts/sync_version.sh
#
# This script:
# 1. Extracts the current version from conanfile.py
# 2. Updates all GitHub workflow files
# 3. Updates profile references
# 4. Validates the changes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 SpareTools Version Synchronization"
echo "===================================="

# Function to extract version from conanfile.py
extract_conan_version() {
    local conanfile="$1"
    if [[ -f "$conanfile" ]]; then
        # Extract version using grep and sed
        grep -oP 'version\s*=\s*["'"'"']\K[^"'"'"']+' "$conanfile" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Find the main conanfile.py (prefer foundation/sparetools-base)
MAIN_CONANFILE="$REPO_ROOT/packages/foundation/sparetools-base/conanfile.py"
if [[ ! -f "$MAIN_CONANFILE" ]]; then
    MAIN_CONANFILE="$REPO_ROOT/conanfile.py"
fi

if [[ ! -f "$MAIN_CONANFILE" ]]; then
    echo "❌ Error: No conanfile.py found in expected locations"
    exit 1
fi

# Extract current version
CURRENT_VERSION=$(extract_conan_version "$MAIN_CONANFILE")
if [[ -z "$CURRENT_VERSION" ]]; then
    echo "❌ Error: Could not extract version from $MAIN_CONANFILE"
    exit 1
fi

echo "📋 Current version: $CURRENT_VERSION"

# Update GitHub workflow files
echo "🔧 Updating GitHub workflow files..."
WORKFLOW_FILES=$(find "$REPO_ROOT/.github/workflows" -name "*.yml" -o -name "*.yaml" 2>/dev/null || true)

if [[ -n "$WORKFLOW_FILES" ]]; then
    while IFS= read -r workflow_file; do
        if [[ -f "$workflow_file" ]]; then
            echo "  📝 Updating $workflow_file"

            # Update VERSION_BASE references
            sed -i "s/VERSION_BASE: .*/VERSION_BASE: $CURRENT_VERSION/g" "$workflow_file"

            # Update sparetools-base version references in workflows
            sed -i "s|sparetools-base/[^@\"']*|sparetools-base/$CURRENT_VERSION|g" "$workflow_file"
        fi
    done <<< "$WORKFLOW_FILES"
fi

# Update profile files
echo "🔧 Updating Conan profile files..."
PROFILE_FILES=$(find "$REPO_ROOT/profiles" -name "*.profile" -o -name "*.txt" 2>/dev/null || true)

if [[ -n "$PROFILE_FILES" ]]; then
    while IFS= read -r profile_file; do
        if [[ -f "$profile_file" ]]; then
            echo "  📝 Updating $profile_file"

            # Update sparetools-base references
            sed -i "s|sparetools-base/[^@\"']*|sparetools-base/$CURRENT_VERSION|g" "$profile_file"
        fi
    done <<< "$PROFILE_FILES"
fi

# Update any VERSION files
if [[ -f "$REPO_ROOT/VERSION" ]]; then
    echo "🔧 Updating VERSION file..."
    echo "$CURRENT_VERSION" > "$REPO_ROOT/VERSION"
fi

# Validate changes
echo "✅ Validating changes..."
VALIDATION_ERRORS=0

# Check for any remaining old version references
OLD_REFS=$(grep -r "sparetools-base/2\.0\.0" "$REPO_ROOT/.github/workflows/" "$REPO_ROOT/profiles/" 2>/dev/null || true)
if [[ -n "$OLD_REFS" ]]; then
    echo "⚠️  Warning: Found remaining old version references:"
    echo "$OLD_REFS"
    echo "   These may need manual review."
fi

# Check VERSION_BASE references
VERSION_BASE_REFS=$(grep -r "VERSION_BASE:" "$REPO_ROOT/.github/workflows/" 2>/dev/null | grep -v "$CURRENT_VERSION" || true)
if [[ -n "$VERSION_BASE_REFS" ]]; then
    echo "❌ Error: Found VERSION_BASE references that don't match current version:"
    echo "$VERSION_BASE_REFS"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# Final status
echo ""
if [[ $VALIDATION_ERRORS -eq 0 ]]; then
    echo "✅ Version synchronization completed successfully!"
    echo "   Updated to version: $CURRENT_VERSION"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Review and commit the changes"
    echo "   2. Push to trigger CI with corrected versions"
    echo "   3. Monitor CI builds for any remaining issues"
else
    echo "❌ Version synchronization completed with errors!"
    echo "   Please review the error messages above."
    exit 1
fi