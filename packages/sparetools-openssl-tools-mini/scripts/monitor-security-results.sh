#!/bin/bash

# Monitor Track A Security & Compliance Pipeline Results
# This script checks GitHub Security tab and workflow results

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first:"
    echo "  https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI. Please run: gh auth login"
    exit 1
fi

print_header "Track A Security & Compliance Pipeline Monitor"
echo ""

# Repository configurations
REPOS=(
    "sparesparrow/openssl-conan-base:Foundation"
    "sparesparrow/openssl-fips-policy:FIPS Policy"
    "sparesparrow/openssl:Domain"
    "sparesparrow/openssl-tools:Tooling"
)

print_status "Checking workflow runs for all repositories..."

for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo name <<< "$repo_info"
    
    print_header "$name Repository ($repo)"
    
    # Check recent workflow runs
    print_status "Recent workflow runs:"
    gh run list --repo "$repo" --limit 5 --json status,conclusion,name,createdAt,url | \
        jq -r '.[] | "\(.name) - \(.status)/\(.conclusion) - \(.createdAt)"' || \
        print_warning "Could not fetch workflow runs for $repo"
    
    echo ""
    
    # Check for security alerts (if accessible)
    print_status "Security alerts:"
    if gh api "repos/$repo/security-advisories" --jq 'length' 2>/dev/null; then
        ALERT_COUNT=$(gh api "repos/$repo/security-advisories" --jq 'length' 2>/dev/null || echo "0")
        if [ "$ALERT_COUNT" -gt 0 ]; then
            print_warning "Found $ALERT_COUNT security advisories"
            gh api "repos/$repo/security-advisories" --jq '.[] | "\(.summary) - \(.state)"' 2>/dev/null || true
        else
            print_success "No security advisories found"
        fi
    else
        print_warning "Could not access security advisories (may require admin permissions)"
    fi
    
    echo ""
done

print_header "Track A Workflow Status Summary"
echo ""

# Check specific Track A workflows
TRACK_A_WORKFLOWS=(
    "sparesparrow/openssl-conan-base:reusable-sbom-generation"
    "sparesparrow/openssl-conan-base:example-sbom-usage"
    "sparesparrow/openssl-fips-policy:fips-validation"
    "sparesparrow/openssl:codeql-analysis"
    "sparesparrow/openssl-tools:conan-ci-enhanced"
)

for workflow_info in "${TRACK_A_WORKFLOWS[@]}"; do
    IFS=':' read -r repo workflow <<< "$workflow_info"
    
    print_status "Checking $workflow in $repo..."
    
    # Get latest run for this workflow
    LATEST_RUN=$(gh run list --repo "$repo" --workflow "$workflow" --limit 1 --json status,conclusion,createdAt,url 2>/dev/null || echo "[]")
    
    if [ "$LATEST_RUN" != "[]" ]; then
        STATUS=$(echo "$LATEST_RUN" | jq -r '.[0].status')
        CONCLUSION=$(echo "$LATEST_RUN" | jq -r '.[0].conclusion')
        CREATED=$(echo "$LATEST_RUN" | jq -r '.[0].createdAt')
        URL=$(echo "$LATEST_RUN" | jq -r '.[0].url')
        
        if [ "$STATUS" = "completed" ] && [ "$CONCLUSION" = "success" ]; then
            print_success "✓ $workflow completed successfully ($CREATED)"
        elif [ "$STATUS" = "completed" ] && [ "$CONCLUSION" = "failure" ]; then
            print_error "✗ $workflow failed ($CREATED)"
            echo "  URL: $URL"
        elif [ "$STATUS" = "in_progress" ]; then
            print_warning "⏳ $workflow is running ($CREATED)"
        else
            print_warning "⚠ $workflow status: $STATUS/$CONCLUSION ($CREATED)"
        fi
    else
        print_warning "No recent runs found for $workflow"
    fi
    
    echo ""
done

print_header "Security Findings Summary"
echo ""

# Check for CodeQL findings
print_status "CodeQL Security Analysis Results:"
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo name <<< "$repo_info"
    
    # Get CodeQL alerts
    ALERTS=$(gh api "repos/$repo/code-scanning/alerts" --jq '.[] | select(.state == "open") | "\(.rule.name) - \(.severity)"' 2>/dev/null || echo "")
    
    if [ -n "$ALERTS" ]; then
        echo "$name ($repo):"
        echo "$ALERTS" | while read -r alert; do
            echo "  - $alert"
        done
    else
        print_success "$name: No open CodeQL alerts"
    fi
done

echo ""

# Check for Dependabot alerts
print_status "Dependabot Security Alerts:"
for repo_info in "${REPOS[@]}"; do
    IFS=':' read -r repo name <<< "$repo_info"
    
    # Get Dependabot alerts
    ALERTS=$(gh api "repos/$repo/dependabot/alerts" --jq '.[] | select(.state == "open") | "\(.security_advisory.summary) - \(.severity)"' 2>/dev/null || echo "")
    
    if [ -n "$ALERTS" ]; then
        echo "$name ($repo):"
        echo "$ALERTS" | while read -r alert; do
            echo "  - $alert"
        done
    else
        print_success "$name: No open Dependabot alerts"
    fi
done

echo ""

print_header "Next Steps"
echo ""
echo "1. 📊 Review Workflow Results:"
echo "   - Check the Actions tab in each repository"
echo "   - Look for any failed workflows and address issues"
echo ""
echo "2. 🔍 Investigate Security Findings:"
echo "   - Review CodeQL alerts in the Security tab"
echo "   - Check Dependabot alerts for dependency vulnerabilities"
echo "   - Address critical and high severity findings first"
echo ""
echo "3. 📋 Download SBOM Artifacts:"
echo "   - Go to workflow runs and download SBOM artifacts"
echo "   - Review the generated Software Bill of Materials"
echo "   - Use SBOMs for compliance and security auditing"
echo ""
echo "4. 🔧 Configure Additional Security:"
echo "   - Set up Dependency Track integration (optional)"
echo "   - Configure additional security scanning tools"
echo "   - Set up notifications for security findings"
echo ""
echo "5. 📈 Monitor Ongoing Security:"
echo "   - Run this script regularly to monitor results"
echo "   - Set up alerts for new security findings"
echo "   - Review and update security policies as needed"
echo ""

print_success "🎯 Track A Security & Compliance Pipeline monitoring complete!"
echo ""
echo "For more detailed information, visit:"
echo "- GitHub Actions: https://github.com/sparesparrow/openssl-conan-base/actions"
echo "- Security Tab: https://github.com/sparesparrow/openssl-conan-base/security"
echo "- Track A Documentation: ./TRACK-A-SECURITY-PIPELINE.md"





