#!/bin/bash
set -euo pipefail

# Validate GitHub Actions workflow files
# Checks for common issues and ensures consistency

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 Validating GitHub Actions workflows..."

# Check if yamllint is available
if ! command -v yamllint >/dev/null 2>&1; then
    echo "⚠️  yamllint not found, installing..."
    pip install yamllint
fi

ERRORS=0

# Validate all workflow YAML files
WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
if [[ -d "$WORKFLOW_DIR" ]]; then
    echo "📝 Checking YAML syntax and structure..."

    # Use yamllint for basic YAML validation
    if ! yamllint --config-file <(echo "
extends: default
rules:
  line-length: disable  # Allow long lines for GitHub Actions
  truthy: disable       # Allow 'on' as boolean
  indentation:
    spaces: 2
    indent-sequences: true
") "$WORKFLOW_DIR"/*.yml 2>/dev/null; then
        echo "❌ YAML syntax errors found"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for common workflow issues
    while IFS= read -r workflow_file; do
        filename=$(basename "$workflow_file")

        # Check VERSION_BASE consistency
        if ! grep -q "VERSION_BASE: \"2\.0\.3\"" "$workflow_file"; then
            echo "❌ $filename: Missing or incorrect VERSION_BASE (should be 2.0.3)"
            ERRORS=$((ERRORS + 1))
        fi

        # Check for required concurrency control
        if ! grep -q "concurrency:" "$workflow_file"; then
            echo "⚠️  $filename: Missing concurrency control"
        fi

        # Check for timeout settings on long-running jobs
        if grep -q "runs-on: ubuntu-latest\|runs-on:.*-latest" "$workflow_file"; then
            if ! grep -q "timeout-minutes:" "$workflow_file"; then
                echo "⚠️  $filename: Long-running job missing timeout"
            fi
        fi

        # Check for proper permissions
        if grep -q "contents: write\|actions: write\|security-events: write" "$workflow_file"; then
            if ! grep -q "permissions:" "$workflow_file"; then
                echo "⚠️  $filename: Uses write permissions but missing permissions block"
            fi
        fi

    done < <(find "$WORKFLOW_DIR" -name "*.yml" -type f)
else
    echo "⚠️  .github/workflows directory not found"
fi

# Check for orphaned workflow files
if [[ -d "$WORKFLOW_DIR" ]]; then
    ORPHANED=$(find "$WORKFLOW_DIR" -name "*.yml" -exec grep -l "TEMPLATE\|DISABLED\|OLD" {} \; 2>/dev/null || true)
    if [[ -n "$ORPHANED" ]]; then
        echo "⚠️  Found potentially orphaned workflow files:"
        echo "$ORPHANED"
    fi
fi

# Summary
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ Workflow validation passed"
    exit 0
else
    echo "❌ Workflow validation failed with $ERRORS errors"
    echo ""
    echo "💡 Common fixes:"
    echo "   - Update VERSION_BASE to '2.0.3'"
    echo "   - Add concurrency control"
    echo "   - Add timeout-minutes to long-running jobs"
    exit 1
fi