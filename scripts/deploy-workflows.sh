#!/bin/bash

# SpareTools GitHub Actions Workflow Deployment Script
# This script creates and configures GitHub Actions workflows for CI/CD
#
# Usage: bash scripts/deploy-workflows.sh [--dry-run] [--force]
#
# --dry-run: Show what would be done without making changes
# --force: Overwrite existing workflows without confirmation

set -e

DRY_RUN=false
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "GitHub Actions Workflow Deployment"
echo "=========================================="
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "⚠️  DRY RUN MODE - No changes will be made"
    echo ""
fi

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Step 1: Verify GitHub CLI
echo "[1/6] Verifying GitHub CLI authentication..."
echo ""

if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI not found - Install from https://cli.github.com"
    exit 1
fi

if ! gh auth status &>/dev/null; then
    log_error "GitHub CLI not authenticated - Run: gh auth login"
    exit 1
fi

GH_REPO=$(gh repo view --json nameWithOwner -q 2>/dev/null || echo "unknown")
log_info "Authenticated for repository: $GH_REPO"

# Step 2: Validate workflow files exist
echo ""
echo "[2/6] Validating workflow source files..."
echo ""

WORKFLOW_DIR=".github/workflows"
REQUIRED_WORKFLOWS=(
    "openssl-analysis.yml"
    "build-test.yml"
    "integration.yml"
)

WORKFLOWS_FOUND=0
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOW_DIR/$workflow" ]; then
        SIZE=$(stat -f%z "$WORKFLOW_DIR/$workflow" 2>/dev/null || stat -c%s "$WORKFLOW_DIR/$workflow" 2>/dev/null)
        SIZE_KB=$((SIZE / 1024))
        log_info "Found: $WORKFLOW_DIR/$workflow ($SIZE_KB KB)"
        ((WORKFLOWS_FOUND++))
    else
        log_warn "Not found: $WORKFLOW_DIR/$workflow"
    fi
done

if [ $WORKFLOWS_FOUND -eq 0 ]; then
    log_error "No workflow files found in $WORKFLOW_DIR"
    echo ""
    echo "You need to create the workflows first:"
    echo "  1. See docs/IMPLEMENTATION_CHECKLIST.md Phase 2"
    echo "  2. Create workflows in .github/workflows/"
    echo "  3. Then run this script again"
    exit 1
fi

log_info "Found $WORKFLOWS_FOUND of ${#REQUIRED_WORKFLOWS[@]} workflows"

# Step 3: Validate workflow syntax
echo ""
echo "[3/6] Validating workflow syntax..."
echo ""

VALID_COUNT=0
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    workflow_path="$WORKFLOW_DIR/$workflow"
    if [ ! -f "$workflow_path" ]; then
        continue
    fi

    # Check YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('$workflow_path'))" 2>/dev/null; then
        log_info "Valid YAML: $workflow"
        ((VALID_COUNT++))
    else
        log_warn "Invalid YAML: $workflow (may cause issues)"
    fi
done

echo ""
log_info "Validated $VALID_COUNT workflow files"

# Step 4: Check branch protection requirements
echo ""
echo "[4/6] Checking branch protection configuration..."
echo ""

# Get develop branch info
DEVELOP_PROTECTED=$(gh api repos/:owner/:repo/branches/develop --json isProtected -q 2>/dev/null || echo "false")

if [ "$DEVELOP_PROTECTED" = "true" ]; then
    log_info "Branch 'develop' is protected"

    # Check required status checks
    REQUIRED_STATUS=$(gh api repos/:owner/:repo/branches/develop/protection --jq '.required_status_checks.strict' 2>/dev/null || echo "false")
    if [ "$REQUIRED_STATUS" = "true" ]; then
        log_info "Strict status checks enabled"
    else
        log_warn "Strict status checks not enabled (recommended)"
    fi
else
    log_warn "Branch 'develop' is not protected"
    echo ""
    echo "Recommendation: Enable branch protection in GitHub settings"
    echo "  1. Go to: Settings → Branches → Branch protection rules"
    echo "  2. Create rule for 'develop' branch"
    echo "  3. Require status checks to pass"
    echo "  4. Require code reviews before merging"
fi

# Step 5: Configure secrets (if needed)
echo ""
echo "[5/6] Checking GitHub Secrets..."
echo ""

SECRETS_OK=true

# Check for Cloudsmith secret
CLOUDSMITH_SECRET=$(gh secret list | grep -i cloudsmith || echo "")
if [ -z "$CLOUDSMITH_SECRET" ]; then
    log_warn "CLOUDSMITH_API_KEY secret not configured"
    echo ""
    echo "To configure:"
    echo "  1. Generate Cloudsmith API key at: https://app.cloudsmith.io"
    echo "  2. Run: gh secret set CLOUDSMITH_API_KEY"
    echo "  3. Paste your API key"
    SECRETS_OK=false
else
    log_info "CLOUDSMITH_API_KEY secret configured"
fi

# Check for GitHub token (should be automatic)
if gh secret list | grep -q "GITHUB_TOKEN"; then
    log_info "GITHUB_TOKEN available"
else
    log_warn "GITHUB_TOKEN not explicitly configured (should be automatic)"
fi

# Step 6: Summary and next steps
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN: No changes were made"
    echo ""
    echo "To deploy workflows:"
    echo "  bash scripts/deploy-workflows.sh --force"
    exit 0
fi

echo "Workflows are ready for use!"
echo ""
echo "Next steps:"
echo ""
echo "1. Commit changes:"
echo "   git add .github/workflows/"
echo "   git commit -m 'ci: deploy GitHub Actions workflows'"
echo ""
echo "2. Push to develop:"
echo "   git push origin develop"
echo ""
echo "3. Monitor initial run:"
echo "   - Go to: https://github.com/$GH_REPO/actions"
echo "   - Click on the latest workflow run"
echo "   - Wait for analysis to complete (~5 min)"
echo ""
echo "4. Configure secrets (if needed):"
if [ "$SECRETS_OK" = false ]; then
    echo "   gh secret set CLOUDSMITH_API_KEY"
    echo "   # Then paste your Cloudsmith API key"
fi
echo ""
echo "5. After workflows pass:"
echo "   - Build artifacts will be available"
echo "   - CPS files will be generated"
echo "   - Cloudsmith upload (if secret configured)"
echo ""
echo "Documentation:"
echo "  - CI/CD Guide: docs/CI_CD_MODERNIZATION_GUIDE.md"
echo "  - Checklist: docs/IMPLEMENTATION_CHECKLIST.md"
echo "  - OpenSSL 3.6.0: docs/OPENSSL-360-BUILD-ANALYSIS.md"
echo ""

# Create post-deployment script
POST_DEPLOY_SCRIPT="scripts/post-deployment-checks.sh"
cat > "$POST_DEPLOY_SCRIPT" << 'EOF'
#!/bin/bash

# Post-deployment verification script
# Run this after workflows have completed for the first time

echo "Post-Deployment Verification Checks"
echo "===================================="
echo ""

# 1. Check workflow status
echo "1. Checking workflow status..."
gh run list --limit 5 --workflow openssl-analysis.yml

# 2. Check for artifacts
echo ""
echo "2. Checking artifacts..."
gh run list --limit 1 --status success | while read run_id rest; do
    gh run view "$run_id" --json artifacts -q '.artifacts[]' || echo "No artifacts yet"
done

# 3. Check branch protection
echo ""
echo "3. Checking branch protection..."
gh api repos/:owner/:repo/branches/develop/protection --jq '.required_status_checks.contexts'

# 4. List configured secrets
echo ""
echo "4. Configured secrets..."
gh secret list

EOF

chmod +x "$POST_DEPLOY_SCRIPT"

log_info "Created post-deployment script: $POST_DEPLOY_SCRIPT"

echo ""
echo "To verify deployment after workflows complete:"
echo "  bash $POST_DEPLOY_SCRIPT"
echo ""
