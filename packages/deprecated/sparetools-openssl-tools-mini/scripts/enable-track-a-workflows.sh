#!/bin/bash

# Enable Track A Security & Compliance Pipeline Workflows
# This script triggers the initial runs of Track A workflows

set -e

echo "🚀 Enabling Track A Security & Compliance Pipeline Workflows"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -f "openssl-test.code-workspace" ]; then
    print_error "Please run this script from the openssl-test root directory"
    exit 1
fi

print_status "Checking Track A workflow files..."

# Verify Track A workflow files exist
TRACK_A_FILES=(
    "openssl-conan-base/.github/workflows/reusable-sbom-generation.yml"
    "openssl-conan-base/.github/workflows/example-sbom-usage.yml"
    "openssl-fips-policy/.github/workflows/fips-validation.yml"
    "openssl/.github/workflows/codeql-analysis.yml"
    "openssl/.github/codeql/codeql-config.yml"
    "openssl/.github/codeql/custom-queries/openssl-security.ql"
    "openssl-fips-policy/fips/expected_module_hash.txt"
)

for file in "${TRACK_A_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file exists"
    else
        print_error "✗ $file missing"
        exit 1
    fi
done

print_status "All Track A workflow files verified!"

# Create a trigger commit to enable workflows
print_status "Creating trigger commit to enable workflows..."

# Add all Track A files to git
git add openssl-conan-base/.github/workflows/
git add openssl-fips-policy/.github/workflows/
git add openssl/.github/workflows/codeql-analysis.yml
git add openssl/.github/codeql/
git add openssl-fips-policy/fips/expected_module_hash.txt
git add openssl-tools/.github/workflows/conan-ci-enhanced.yml
git add openssl/.github/workflows/ci.yml

# Create commit message
COMMIT_MSG="feat: Enable Track A Security & Compliance Pipeline

- Integrate SBOM generation into existing CI/CD workflows
- Add security scanning using reusable Track A workflows
- Enable CodeQL analysis for OpenSSL repository
- Add FIPS 140-3 validation workflows
- Update CI workflows to include SBOM generation steps

Track A Components:
✅ Reusable SBOM Generation Workflow
✅ FIPS 140-3 Validation Workflow
✅ CodeQL Security Analysis Workflow
✅ SBOM Integration in CI/CD Pipelines
✅ Security Scanning with Trivy
✅ GitHub Security Tab Integration

This commit triggers the initial runs of all Track A workflows."

# Commit the changes
if git commit -m "$COMMIT_MSG"; then
    print_success "✓ Trigger commit created successfully"
else
    print_warning "No changes to commit (workflows may already be enabled)"
fi

# Push to trigger workflows
print_status "Pushing changes to trigger workflow runs..."

if git push origin main; then
    print_success "✓ Changes pushed successfully"
    print_status "Workflows should now be triggered automatically"
else
    print_error "Failed to push changes"
    exit 1
fi

# Display next steps
echo ""
echo "🎯 Track A Security & Compliance Pipeline Enabled!"
echo "=================================================="
echo ""
echo "Next Steps:"
echo "1. 📊 Monitor GitHub Actions:"
echo "   - Go to each repository's Actions tab"
echo "   - Look for workflow runs triggered by this commit"
echo ""
echo "2. 🔍 Check Security Tab:"
echo "   - Navigate to Security > Code scanning alerts"
echo "   - Review any findings from CodeQL analysis"
echo "   - Check Security > Dependabot alerts for vulnerability scans"
echo ""
echo "3. 📋 Review Workflow Results:"
echo "   - openssl-conan-base: SBOM generation and vulnerability scanning"
echo "   - openssl-fips-policy: FIPS 140-3 validation"
echo "   - openssl: CodeQL security analysis"
echo "   - openssl-tools: Integrated security scanning"
echo ""
echo "4. 🔧 Configure Secrets (if needed):"
echo "   - DEPENDENCY_TRACK_API_KEY (optional)"
echo "   - DEPENDENCY_TRACK_URL (optional)"
echo "   - CLOUDSMITH_API_KEY (for package uploads)"
echo ""
echo "5. 📈 Monitor Results:"
echo "   - Check workflow artifacts for SBOM files"
echo "   - Review security scan results"
echo "   - Address any critical/high severity findings"
echo ""
echo "Track A is now active and will run on:"
echo "- Push to main branches"
echo "- Pull requests"
echo "- Scheduled runs (weekly for CodeQL, daily for SBOM)"
echo "- Manual workflow dispatch"
echo ""
print_success "🚀 Track A Security & Compliance Pipeline is now enabled!"
