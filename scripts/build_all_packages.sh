#!/bin/bash
# SpareTools Package Build Script

set -e  # Exit on any error

echo "=== SpareTools Package Build Script ==="
echo "Building packages in dependency order..."
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to build a package
build_package() {
    local package_name=$1
    local category=$2

    echo -e "${YELLOW}Building ${package_name} (${category})...${NC}"

    # Find the conanfile.py for this package
    local conanfile_path
    conanfile_path=$(find packages -name "conanfile.py" -exec grep -l "name = \"$package_name\"" {} \; | head -1)

    if [ -z "$conanfile_path" ]; then
        echo -e "${RED}❌ Cannot find conanfile.py for $package_name${NC}"
        return 1
    fi

    local package_dir
    package_dir=$(dirname "$conanfile_path")

    echo "  Package directory: $package_dir"

    # Extract version from conanfile.py
    local version
    version=$(grep -oP "version = \"\K[^\"]+" "$conanfile_path" | head -1)

    if [ -z "$version" ]; then
        echo -e "${RED}❌ Cannot determine version for $package_name${NC}"
        return 1
    fi

    echo "  Version: $version"

    # Build the package
    if cd "$package_dir" && conan create . --version="$version" --build=missing; then
        echo -e "${GREEN}✅ Successfully built $package_name v$version${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to build $package_name${NC}"
        return 1
    fi
}

# Build foundation packages in dependency order
echo "=== Building Foundation Packages ==="

# These are the foundation packages in roughly correct order
foundation_packages=(
    "sparetools-recipe-base:foundation"
    "sparetools-base:foundation"
    "sparetools-cpython:foundation"
    "sparetools-bootstrap:foundation"
    "sparetools-shared-dev-tools:foundation"
    "sparetools-test-harness:foundation"
    "sparetools-test-framework:foundation"
    "sparetools-flatbuffers:foundation"
    "sparetools-protocols:foundation"
    "sparesparrow-protocols:foundation"
    "sparetools-icd:foundation"
    "sparetools-schema-tests:foundation"
    "sparetools-voice-fsm:foundation"
)

built_count=0
failed_count=0

for package_info in "${foundation_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Build embedded packages
echo "=== Building Embedded Packages ==="

embedded_packages=(
    "sparetools-embedded:embedded"
    "sparetools-hal-sunton:embedded"
    "sparetools-lvgl:embedded"
)

for package_info in "${embedded_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Build schema packages
echo "=== Building Schema Packages ==="

schema_packages=(
    "sparetools-bpm-schemas:schemas"
)

for package_info in "${schema_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Build MCP packages
echo "=== Building MCP Packages ==="

mcp_packages=(
    "sparetools-mcp-core:mcp"
    "sparetools-mcp-ecosystem:mcp"
    "sparetools-mcp-prompts:mcp"
    "sparetools-mcp-servers:mcp"
)

for package_info in "${mcp_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Build consumer packages
echo "=== Building Consumer Packages ==="

consumer_packages=(
    "sparetools-mia:consumers"
    "sparetools-bpm-detector:consumers"
    "sparetools-nucleus:consumers"
    "sparetools-openssl:consumers"
    "sparetools-openssl-tools:consumers"
    "sparetools-obd-sim:consumers"
    "sparetools-cliphist-android:consumers"
    "sparetools-mcp-orchestrator:consumers"
    "sparetools-tinymcp:consumers"
    "sparetools-mcpserver-cpp:consumers"
)

for package_info in "${consumer_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Build other packages
echo "=== Building Other Packages ==="

other_packages=(
    "sparetools-py:python_tools"
    "sparetools-fs-tools:python_tools"
    "sparetools-proc-tools:python_tools"
    "sparetools-streaming-solutions:streaming"
    "sparetools-wifi-sensing:wifi"
    "sparetools-sdr-tools:sdr"
    "sparetools-crypto-suite:security"
    "sparetools-gamepad-core:input"
    "sparetools-input-backends:input"
    "sparetools-gamepad-mapper:input"
    "sparetools-prompt-system:prompt"
    "sparetools-ci-templates:devops"
    "sparetools-pentest-toolkit:pentest"
    "esp32-bus-pirate:firmware"
)

for package_info in "${other_packages[@]}"; do
    IFS=':' read -r package_name category <<< "$package_info"

    if build_package "$package_name" "$category"; then
        ((built_count++))
    else
        ((failed_count++))
        echo "Continuing with next package..."
    fi
    echo
done

# Summary
echo "=== Build Summary ==="
echo "Successfully built: $built_count packages"
echo "Failed to build: $failed_count packages"

if [ $failed_count -eq 0 ]; then
    echo -e "${GREEN}🎉 All packages built successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages failed to build. Check logs above.${NC}"
fi

echo
echo "To upload packages to Cloudsmith, run:"
echo "  ./scripts/upload_all_packages.sh"
