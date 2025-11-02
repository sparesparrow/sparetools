#!/bin/bash
# sync-github-secrets.sh
# Sync GitHub secrets from environment variables sourced from ~/.bashrc

set -euo pipefail

REPO="sparesparrow/sparetools"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASHRC="$HOME/.bashrc"

echo "?? GitHub Secrets Sync from ~/.bashrc"
echo "======================================"
echo ""

# Check GitHub CLI authentication
if ! gh auth status > /dev/null 2>&1; then
    echo "? GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo "? GitHub CLI authenticated"
echo ""

# Source bashrc to get environment variables
# We need to source it in a way that gets the exports without interactive features
echo "?? Sourcing environment variables from $BASHRC..."

# Extract export statements from bashrc and source them
# This avoids interactive prompts and other non-export statements
if [ -f "$BASHRC" ]; then
    # Use a subshell to source bashrc safely
    # Extract only export statements and evaluate them
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        
        # Check if it's an export statement
        if [[ "$line" =~ ^[[:space:]]*export[[:space:]]+ ]]; then
            # Evaluate the export statement
            eval "$line" 2>/dev/null || true
        fi
    done < <(grep -E "^[[:space:]]*export[[:space:]]+" "$BASHRC" || true)
else
    echo "??  Warning: $BASHRC not found, trying to source anyway..."
    # Fallback: try to source bashrc directly (may have side effects)
    source "$BASHRC" 2>/dev/null || true
fi

echo "? Environment variables loaded"
echo ""

# Required secrets mapping: GitHub secret name -> Environment variable name
declare -A SECRET_MAP=(
    ["CLOUDSMITH_API_KEY"]="CLOUDSMITH_API_KEY"
)

# Optional secrets (will be set if environment variable exists)
declare -A OPTIONAL_SECRET_MAP=(
    ["GITHUB_TOKEN"]="GITHUB_TOKEN"
    ["CONAN_REMOTE_PASSWORD"]="CONAN_REMOTE_PASSWORD"
)

# Function to set a secret
set_secret() {
    local secret_name=$1
    local env_var_name=$2
    local value="${!env_var_name:-}"
    
    if [ -z "$value" ]; then
        echo "??  Skipping $secret_name: $env_var_name not set in environment"
        return 1
    fi
    
    echo "Setting $secret_name..."
    echo -n "$value" | gh secret set "$secret_name" -R "$REPO"
    
    if [ $? -eq 0 ]; then
        echo "? $secret_name configured successfully"
        return 0
    else
        echo "? Failed to configure $secret_name"
        return 1
    fi
}

# Set required secrets
echo "?? Configuring required secrets..."
echo ""

REQUIRED_FAILED=0
for secret_name in "${!SECRET_MAP[@]}"; do
    env_var="${SECRET_MAP[$secret_name]}"
    if ! set_secret "$secret_name" "$env_var"; then
        REQUIRED_FAILED=1
    fi
    echo ""
done

# Set optional secrets (if they exist)
echo "?? Configuring optional secrets (if available)..."
echo ""

for secret_name in "${!OPTIONAL_SECRET_MAP[@]}"; do
    env_var="${OPTIONAL_SECRET_MAP[$secret_name]}"
    set_secret "$secret_name" "$env_var" || true
    echo ""
done

# Verify secrets
echo "?? Verifying configured secrets..."
echo ""
gh secret list -R "$REPO"

echo ""
if [ $REQUIRED_FAILED -eq 0 ]; then
    echo "? Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Verify secrets in GitHub UI: https://github.com/$REPO/settings/secrets/actions"
    echo "2. Test workflow: gh workflow run publish.yml"
else
    echo "??  Some required secrets failed to configure. Please check the errors above."
    exit 1
fi
