#!/bin/bash
# Setup Zero-Copy Symlinks for SpareTools Build Directory
#
# This script creates symlinks from _Build/packages/ to Conan cache
# packages, implementing the zero-copy deployment pattern.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR"
CONAN_CACHE="${CONAN_USER_HOME:-$HOME/.conan2}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SpareTools Zero-Copy Symlink Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Create packages directory if it doesn't exist
mkdir -p "$BUILD_DIR/packages"

# Create symlink to Conan cache root
echo -e "${BLUE}Setting up Conan cache symlink...${NC}"
if [ -L "$BUILD_DIR/conan-cache" ]; then
    rm "$BUILD_DIR/conan-cache"
fi
ln -sfn "$CONAN_CACHE" "$BUILD_DIR/conan-cache"
echo -e "${GREEN}✓${NC} conan-cache -> $CONAN_CACHE"
echo

# Package list
packages=(
    "sparetools-base"
    "sparetools-cpython"
    "sparetools-shared-dev-tools"
    "sparetools-bootstrap"
    "sparetools-openssl-tools"
    "sparetools-openssl"
)

echo -e "${BLUE}Setting up package symlinks...${NC}"
found_count=0
missing_count=0

for pkg in "${packages[@]}"; do
    # Find the latest package in Conan cache
    pkg_path=$(find "$CONAN_CACHE/p" -maxdepth 1 -type d -name "${pkg}*" 2>/dev/null | sort -V | tail -1)
    
    if [ -n "$pkg_path" ] && [ -d "$pkg_path/p" ]; then
        # Remove old symlink if exists
        if [ -L "$BUILD_DIR/packages/$pkg" ]; then
            rm "$BUILD_DIR/packages/$pkg"
        fi
        
        # Create new symlink
        ln -sfn "$pkg_path/p" "$BUILD_DIR/packages/$pkg"
        echo -e "${GREEN}✓${NC} $pkg -> $pkg_path/p"
        ((found_count++))
    else
        echo -e "${YELLOW}⚠${NC} $pkg not found in Conan cache"
        ((missing_count++))
    fi
done

echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "  Packages linked: ${found_count}/${#packages[@]}"
if [ $missing_count -gt 0 ]; then
    echo -e "  ${YELLOW}Missing packages: ${missing_count}${NC}"
    echo
    echo -e "${YELLOW}To build missing packages:${NC}"
    echo -e "  cd /home/sparrow/sparetools"
    echo -e "  ./scripts/build-and-upload.sh --skip-upload"
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Verify symlinks
echo -e "${BLUE}Verifying symlinks...${NC}"
ls -lh "$BUILD_DIR/packages/" 2>/dev/null | grep -E '^l' || echo "No symlinks created"
echo

# Show disk usage comparison
echo -e "${BLUE}Disk Usage Analysis:${NC}"
cache_usage=$(du -sh "$CONAN_CACHE" 2>/dev/null | awk '{print $1}' || echo "N/A")
build_usage=$(du -sh "$BUILD_DIR/packages" 2>/dev/null | awk '{print $1}' || echo "N/A")
echo -e "  Conan cache:      ${cache_usage}"
echo -e "  _Build/packages:  ${build_usage} ${GREEN}(symlinks only)${NC}"
echo

echo -e "${GREEN}✓ Zero-copy setup complete!${NC}"
