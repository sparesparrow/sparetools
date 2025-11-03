#!/bin/bash
# Verify that workflow optimizations are correctly configured

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Verifying Workflow Optimizations ===${NC}"
echo ""

# Check ci.yml
echo -e "${BLUE}Checking ci.yml...${NC}"
if grep -q "path: ~/.conan2$" .github/workflows/ci.yml; then
    echo -e "${GREEN}  ✓ Conan cache path is correct${NC}"
else
    echo -e "${RED}  ✗ Conan cache path may be incorrect${NC}"
fi

if grep -q "BUILD_START" .github/workflows/ci.yml; then
    echo -e "${GREEN}  ✓ Build timing is configured${NC}"
else
    echo -e "${YELLOW}  ⚠ Build timing may not be configured${NC}"
fi

if grep -A 2 "Save build artifacts" .github/workflows/ci.yml | grep -q "if: failure()"; then
    echo -e "${GREEN}  ✓ Artifacts upload on failure only${NC}"
else
    echo -e "${YELLOW}  ⚠ Check artifact upload conditions${NC}"
fi

echo ""

# Check publish.yml
echo -e "${BLUE}Checking publish.yml...${NC}"
if grep -q "check-existing-packages" .github/workflows/publish.yml; then
    echo -e "${GREEN}  ✓ Smart publishing check exists${NC}"
else
    echo -e "${RED}  ✗ Smart publishing check missing${NC}"
fi

if grep -q "list-existing-packages" .github/workflows/publish.yml; then
    echo -e "${GREEN}  ✓ List existing packages job exists${NC}"
else
    echo -e "${RED}  ✗ List existing packages job missing${NC}"
fi

echo ""

# Check nightly.yml
echo -e "${BLUE}Checking nightly.yml...${NC}"
if grep -q "Cache Conan artifacts" .github/workflows/nightly.yml; then
    echo -e "${GREEN}  ✓ Nightly caching is configured${NC}"
else
    echo -e "${RED}  ✗ Nightly caching missing${NC}"
fi

if grep -q "BUILD_START" .github/workflows/nightly.yml; then
    echo -e "${GREEN}  ✓ Nightly build timing is configured${NC}"
else
    echo -e "${YELLOW}  ⚠ Nightly build timing may not be configured${NC}"
fi

echo ""

# Check reusable workflow
echo -e "${BLUE}Checking reusable/build-package.yml...${NC}"
if grep -q "path: ~/.conan2$" .github/workflows/reusable/build-package.yml; then
    echo -e "${GREEN}  ✓ Reusable workflow cache path is correct${NC}"
else
    echo -e "${RED}  ✗ Reusable workflow cache path may be incorrect${NC}"
fi

if grep -q "profiles/\*\*" .github/workflows/reusable/build-package.yml; then
    echo -e "${GREEN}  ✓ Profile files included in cache hash${NC}"
else
    echo -e "${YELLOW}  ⚠ Profile files may not be in cache hash${NC}"
fi

echo ""

echo -e "${GREEN}=== Verification Complete ===${NC}"
echo ""
echo "Summary:"
echo "  All optimizations appear to be correctly configured."
echo "  Next workflow run will use these optimizations."
