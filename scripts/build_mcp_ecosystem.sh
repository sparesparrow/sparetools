#!/bin/bash
# Build SpareTools MCP Ecosystem packages

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPARETOOLS_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Building SpareTools MCP Ecosystem..."
echo "   Base directory: $SPARETOOLS_DIR"

# Build order: dependencies first
PACKAGES=(
    "packages/mcp/sparetools-mcp-core"      # NEW: Shared core library
    "packages/mcp/sparetools-mcp-servers"   # Updated: Uses core
    "packages/mcp/sparetools-mcp-ecosystem" # Updated: Includes all
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

build_package() {
    local pkg="$1"
    local pkg_path="$SPARETOOLS_DIR/$pkg"
    
    if [ ! -d "$pkg_path" ]; then
        echo -e "${YELLOW}⚠️  Package directory not found: $pkg${NC}"
        return 0
    fi
    
    echo ""
    echo -e "${GREEN}📦 Building $pkg...${NC}"
    
    if [ -f "$pkg_path/conanfile.py" ]; then
        (cd "$pkg_path" && conan create . --build=missing)
    else
        echo -e "${YELLOW}   No conanfile.py found, skipping Conan build${NC}"
    fi
}

# Build each package in order
for pkg in "${PACKAGES[@]}"; do
    build_package "$pkg"
done

echo ""
echo -e "${GREEN}✅ All MCP packages built successfully${NC}"

# Upload to Cloudsmith if API key is configured
if [ -n "${CLOUDSMITH_API_KEY:-}" ]; then
    echo ""
    echo "☁️ Uploading to Cloudsmith..."
    conan upload "sparetools-mcp-*" -r cloudsmith --all --confirm
    echo -e "${GREEN}✅ Uploaded to Cloudsmith${NC}"
else
    echo ""
    echo -e "${YELLOW}ℹ️  CLOUDSMITH_API_KEY not set, skipping upload${NC}"
    echo "   Set CLOUDSMITH_API_KEY environment variable to enable upload"
fi

# List built packages
echo ""
echo "📋 Built packages:"
conan list "sparetools-mcp-*:*" 2>/dev/null || echo "   (Use 'conan list' to see packages)"
