#!/bin/bash

# SpareTools CI/CD Documentation Setup Script
# This script automates deployment of CLAUDE.md files to local repository clones
#
# Usage: bash scripts/setup-documentation.sh
#
# Prerequisites:
# - Local clones must exist in _local-clones/cpy-local, etc.
# - docs/_Build/ must contain CLAUDE_*.md files

set -e

echo "=========================================="
echo "SpareTools CI/CD Documentation Setup"
echo "=========================================="
echo ""

# Configuration
CLONE_BASE="_local-clones"
DOCS_BASE="docs/_Build"
SPARETOOLS_ROOT="$(pwd)"

# Repositories to configure
declare -A REPOS=(
    [cpy-local]="CLAUDE_cpy.md"
    [openssl-tools-local]="CLAUDE_openssl_tools.md"
    [openssl-local]="CLAUDE_openssl.md"
)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Step 1: Validate prerequisites
echo "[1/5] Validating prerequisites..."
echo ""

if [ ! -d "$CLONE_BASE" ]; then
    log_error "Clone base directory not found: $CLONE_BASE"
    echo "Create it with: mkdir -p $CLONE_BASE"
    echo "Then clone repositories:"
    echo "  git clone https://github.com/sparesparrow/cpy.git $CLONE_BASE/cpy-local"
    echo "  git clone https://github.com/sparesparrow/openssl-tools.git $CLONE_BASE/openssl-tools-local"
    echo "  git clone https://github.com/sparesparrow/openssl.git $CLONE_BASE/openssl-local"
    exit 1
fi
log_info "Clone base directory found: $CLONE_BASE"

if [ ! -d "$DOCS_BASE" ]; then
    log_error "Documentation source directory not found: $DOCS_BASE"
    echo "Expected CLAUDE.md files in: $DOCS_BASE/"
    exit 1
fi
log_info "Documentation source directory found: $DOCS_BASE"

# Step 2: Deploy CLAUDE.md files
echo ""
echo "[2/5] Deploying CLAUDE.md files..."
echo ""

DEPLOY_COUNT=0
for repo_dir in "${!REPOS[@]}"; do
    claude_file="${REPOS[$repo_dir]}"
    src_file="$DOCS_BASE/$claude_file"
    dst_dir="$CLONE_BASE/$repo_dir"
    dst_file="$dst_dir/CLAUDE.md"

    if [ ! -d "$dst_dir" ]; then
        log_warn "Repository directory not found: $dst_dir (skipping)"
        continue
    fi

    if [ ! -f "$src_file" ]; then
        log_warn "Source file not found: $src_file (skipping)"
        continue
    fi

    # Copy file
    cp "$src_file" "$dst_file"
    LINES=$(wc -l < "$dst_file")
    log_info "Deployed $repo_dir/CLAUDE.md ($LINES lines)"
    ((DEPLOY_COUNT++))
done

if [ $DEPLOY_COUNT -eq 0 ]; then
    log_error "No CLAUDE.md files were deployed"
    exit 1
fi

echo ""
log_info "Successfully deployed $DEPLOY_COUNT CLAUDE.md files"

# Step 3: Update .gitignore
echo ""
echo "[3/5] Updating .gitignore..."
echo ""

GITIGNORE_FILE=".gitignore"
GITIGNORE_ENTRIES=(
    "# Local repository clones with CLAUDE.md documentation"
    "_local-clones/*/CLAUDE.md"
    "_local-clones/cpy-local/"
    "_local-clones/openssl-tools-local/"
    "_local-clones/openssl-local/"
)

# Check if entries already exist
NEEDS_UPDATE=false
for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -q "$(echo "$entry" | sed 's/[[\.*^$/]/\\&/g')" "$GITIGNORE_FILE" 2>/dev/null; then
        NEEDS_UPDATE=true
        break
    fi
done

if [ "$NEEDS_UPDATE" = true ]; then
    # Append entries
    echo "" >> "$GITIGNORE_FILE"
    for entry in "${GITIGNORE_ENTRIES[@]}"; do
        echo "$entry" >> "$GITIGNORE_FILE"
    done
    log_info "Updated .gitignore with _local-clones entries"
else
    log_info ".gitignore already contains _local-clones entries"
fi

# Step 4: Validate deployed files
echo ""
echo "[4/5] Validating deployed files..."
echo ""

VALID_COUNT=0
for repo_dir in "${!REPOS[@]}"; do
    dst_dir="$CLONE_BASE/$repo_dir"
    dst_file="$dst_dir/CLAUDE.md"

    if [ ! -f "$dst_file" ]; then
        log_warn "Validation failed: $dst_file not found"
        continue
    fi

    # Check file size (should be substantial)
    SIZE=$(stat -f%z "$dst_file" 2>/dev/null || stat -c%s "$dst_file" 2>/dev/null || echo "0")
    SIZE_KB=$((SIZE / 1024))

    if [ $SIZE -lt 10000 ]; then
        log_warn "File appears small: $dst_file ($SIZE_KB KB)"
        continue
    fi

    # Check for section headers
    if grep -q "## Overview" "$dst_file"; then
        log_info "Validated $repo_dir/CLAUDE.md ($SIZE_KB KB, proper structure)"
        ((VALID_COUNT++))
    else
        log_warn "File structure issue: $dst_file (missing ## Overview)"
    fi
done

echo ""
if [ $VALID_COUNT -eq $DEPLOY_COUNT ]; then
    log_info "All deployed files validated successfully"
else
    log_warn "$VALID_COUNT of $DEPLOY_COUNT files validated"
fi

# Step 5: Generate verification report
echo ""
echo "[5/5] Generating verification report..."
echo ""

REPORT_FILE="docs/documentation-deployment-report.txt"
cat > "$REPORT_FILE" << EOF
SpareTools CI/CD Documentation Deployment Report
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
========================================

DEPLOYMENT SUMMARY
------------------
Total Files Deployed: $DEPLOY_COUNT

DEPLOYED FILES
--------------
EOF

for repo_dir in "${!REPOS[@]}"; do
    dst_dir="$CLONE_BASE/$repo_dir"
    dst_file="$dst_dir/CLAUDE.md"

    if [ -f "$dst_file" ]; then
        LINES=$(wc -l < "$dst_file")
        SIZE=$(stat -f%z "$dst_file" 2>/dev/null || stat -c%s "$dst_file" 2>/dev/null || echo "0")
        SIZE_KB=$((SIZE / 1024))
        MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$dst_file" 2>/dev/null || stat -c "%y" "$dst_file" 2>/dev/null)

        echo "" >> "$REPORT_FILE"
        echo "Repository: $repo_dir" >> "$REPORT_FILE"
        echo "  File: $dst_file" >> "$REPORT_FILE"
        echo "  Lines: $LINES" >> "$REPORT_FILE"
        echo "  Size: $SIZE_KB KB" >> "$REPORT_FILE"
        echo "  Modified: $MODIFIED" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << 'EOF'

GITIGNORE STATUS
----------------
EOF

if grep -q "_local-clones" "$GITIGNORE_FILE"; then
    echo "✓ _local-clones entries added to .gitignore" >> "$REPORT_FILE"
else
    echo "⚠ _local-clones not in .gitignore" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << 'EOF'

NEXT STEPS
----------
1. Review deployed CLAUDE.md files in each cloned repository
2. Verify content matches expectations
3. Commit changes: git add . && git commit -m "docs: deploy CLAUDE.md documentation"
4. Push to develop: git push origin develop
5. Run validation: bash scripts/validate-ci-setup.sh

DOCUMENTATION LOCATIONS
-----------------------
Main Documentation:
  - docs/CI_CD_MODERNIZATION_GUIDE.md
  - docs/IMPLEMENTATION_CHECKLIST.md (THIS FILE)
  - docs/OPENSSL-360-BUILD-ANALYSIS.md

Deployed to Local Clones:
  - _local-clones/cpy-local/CLAUDE.md
  - _local-clones/openssl-tools-local/CLAUDE.md
  - _local-clones/openssl-local/CLAUDE.md

NOTES
-----
- These files are excluded from git via .gitignore
- They serve as local documentation for developers
- When cloning into dedicated locations, copy files from _Build/ to repository root
EOF

log_info "Verification report generated: $REPORT_FILE"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Documentation deployment summary:"
echo "  • Deployed files: $DEPLOY_COUNT"
echo "  • Validated files: $VALID_COUNT"
echo ""
echo "Next steps:"
echo "  1. Review deployed files: ls -lh $_local-clones/*/CLAUDE.md"
echo "  2. Commit and push: git add . && git commit -m 'docs: deploy CLAUDE.md files'"
echo "  3. Validate setup: bash scripts/validate-ci-setup.sh"
echo "  4. Read checklist: docs/IMPLEMENTATION_CHECKLIST.md"
echo ""
echo "Report: $REPORT_FILE"
echo ""
