#!/bin/bash
set -euo pipefail

# Check for accidentally committed secrets and sensitive data
# Scans common patterns that might indicate leaked credentials

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔐 Checking for potential secret leaks..."

# Patterns that might indicate secrets (but could be false positives)
SECRET_PATTERNS=(
    "password.*=.*[a-zA-Z0-9]{8,}"  # password = something
    "token.*=.*[a-zA-Z0-9]{20,}"    # token = something
    "secret.*=.*[a-zA-Z0-9]{16,}"   # secret = something
    "key.*=.*[a-zA-Z0-9]{16,}"      # key = something
    "api.*key.*=.*[a-zA-Z0-9]{16,}" # api key = something
)

# Files to exclude from secret checking
EXCLUDE_PATTERNS=(
    "*.pyc"
    "*.pyo"
    "__pycache__/*"
    ".git/*"
    "*.log"
    "node_modules/*"
    "*.min.js"
    "*.min.css"
    "dist/*"
    "build/*"
    "*.svg"
    "*.png"
    "*.jpg"
    "*.jpeg"
    "*.gif"
    "*.pdf"
    "*.zip"
    "*.tar.gz"
    "*.lock"
    "package-lock.json"
    "yarn.lock"
    "pnpm-lock.yaml"
)

WARNINGS=0

# Function to check if file should be excluded
should_exclude() {
    local file="$1"
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]] || [[ "$file" == */$pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Check text files for potential secrets
while IFS= read -r -d '' file; do
    # Skip excluded files
    if should_exclude "$file"; then
        continue
    fi

    # Check file size (skip very large files)
    if [[ $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0") -gt 10485760 ]]; then
        continue
    fi

    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -n "$pattern" "$file" >/dev/null 2>&1; then
            echo "⚠️  Potential secret pattern found in $file"
            echo "   Pattern: $pattern"
            grep -n "$pattern" "$file" | head -3 | sed 's/^/     /'
            WARNINGS=$((WARNINGS + 1))
        fi
    done
done < <(find "$REPO_ROOT" -type f -size -10M \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.txt" -o -name "*.sh" -o -name "*.cfg" -o -name "*.ini" \) -print0)

# Check for hardcoded API keys in environment files
ENV_FILES=$(find "$REPO_ROOT" -name "*.env*" -o -name ".env*" -o -name "env.*" 2>/dev/null || true)
if [[ -n "$ENV_FILES" ]]; then
    echo "🔍 Checking environment files..."
    for env_file in $ENV_FILES; do
        if [[ -f "$env_file" ]] && grep -i "key\|token\|secret\|password" "$env_file" >/dev/null 2>&1; then
            echo "⚠️  Environment file contains sensitive patterns: $env_file"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
fi

# Summary
if [[ $WARNINGS -eq 0 ]]; then
    echo "✅ No potential secret leaks detected"
    exit 0
else
    echo ""
    echo "⚠️  Found $WARNINGS potential secret leaks"
    echo ""
    echo "💡 Review the flagged files and:"
    echo "   - Use repository secrets instead of hardcoded values"
    echo "   - Add sensitive files to .gitignore"
    echo "   - Use environment variables for configuration"
    echo ""
    echo "If these are false positives, add exclusion patterns to check_secrets.sh"
    exit 1
fi