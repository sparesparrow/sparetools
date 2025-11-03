#!/bin/bash
# Documentation Consolidation Script for SpareTools
# Phase 1 & 2: Archive old files, rename/move files to docs/

set -e

echo "===== SpareTools Documentation Consolidation ====="
echo

# Create archive directory
echo "Creating docs/archive/..."
mkdir -p docs/archive

# Phase 1: Archive root files
echo "Archiving root documentation files..."
git mv BASELINE.md docs/archive/ 2>/dev/null || echo "  BASELINE.md already moved or missing"
git mv ZERO-COPY-IMPLEMENTATION.md docs/archive/ 2>/dev/null || echo "  ZERO-COPY-IMPLEMENTATION.md already moved or missing"
git mv RELEASE-NOTES-v2.0.0.md docs/archive/ 2>/dev/null || echo "  RELEASE-NOTES-v2.0.0.md already moved or missing"
git mv PACKAGE-ECOSYSTEM-INDEX.md docs/archive/ 2>/dev/null || echo "  PACKAGE-ECOSYSTEM-INDEX.md already moved or missing"

# Phase 1: Delete root files
echo "Deleting consolidated root files..."
git rm QUICKSTART.md 2>/dev/null || echo "  QUICKSTART.md already deleted or missing"

# Phase 2: Rename PACKAGE-*.md files to docs/
echo "Renaming and moving PACKAGE-*.md files to docs/..."
git mv PACKAGE-QUICK-REFERENCE.md docs/QUICK-REFERENCE.md 2>/dev/null || echo "  PACKAGE-QUICK-REFERENCE.md already moved or missing"
git mv PACKAGE-ECOSYSTEM-SUMMARY.md docs/PACKAGES.md 2>/dev/null || echo "  PACKAGE-ECOSYSTEM-SUMMARY.md already moved or missing"

# Phase 2: Delete duplicate CI/CD docs
echo "Deleting duplicate CI/CD documentation..."
git rm docs/README_CI_CD_QUICKSTART.md 2>/dev/null || echo "  README_CI_CD_QUICKSTART.md already deleted or missing"
git rm docs/CI-CD-DOCUMENTATION-INDEX.md 2>/dev/null || echo "  CI-CD-DOCUMENTATION-INDEX.md already deleted or missing"

echo
echo "===== Consolidation Complete ====="
echo
echo "Summary:"
echo "  - Archived: BASELINE.md, ZERO-COPY-IMPLEMENTATION.md, RELEASE-NOTES-v2.0.0.md, PACKAGE-ECOSYSTEM-INDEX.md"
echo "  - Deleted: QUICKSTART.md, README_CI_CD_QUICKSTART.md, CI-CD-DOCUMENTATION-INDEX.md"
echo "  - Renamed: PACKAGE-QUICK-REFERENCE.md → docs/QUICK-REFERENCE.md"
echo "  - Renamed: PACKAGE-ECOSYSTEM-SUMMARY.md → docs/PACKAGES.md"
echo
echo "Next steps:"
echo "  1. Review changes with: git status"
echo "  2. Consolidate CI/CD docs (manual step)"
echo "  3. Commit with: git commit -m 'docs: consolidate documentation structure'"
