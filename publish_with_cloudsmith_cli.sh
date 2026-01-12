#!/bin/bash

echo "=== Publishing SpareTools Packages using Cloudsmith CLI ==="
echo "Repository: sparesparrow-conan/sparetools"
echo ""

# Check if CLOUDSMITH_API_KEY is set
if [ -z "$CLOUDSMITH_API_KEY" ]; then
    echo "❌ Error: CLOUDSMITH_API_KEY environment variable not set"
    echo "Please set it with: export CLOUDSMITH_API_KEY=your_api_key_here"
    echo ""
    echo "Get your API key from: https://cloudsmith.io/user/settings/api-key/"
    exit 1
fi

echo "🔑 Using Cloudsmith API Key: ${CLOUDSMITH_API_KEY:0:8}..."
echo ""

# Authenticate with cloudsmith-cli using environment variable
echo "🔐 Authenticating with Cloudsmith..."
CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" cloudsmith whoami >/dev/null 2>&1 || {
    echo "❌ Authentication failed"
    exit 1
}

echo ""
echo "📦 Publishing new consolidated packages..."

# Function to publish a package using Conan + Cloudsmith CLI
publish_conan_package() {
    local package_path=$1
    local package_name=$2
    local version=${3:-"1.0.0"}
    
    echo ""
    echo "🚀 Publishing: $package_name v$version"
    echo "   Path: $package_path"
    
    if [ ! -f "$package_path/conanfile.py" ]; then
        echo "❌ No conanfile.py found at: $package_path"
        return 1
    fi
    
    echo "   Creating package with Conan..."
    
    # Create the package
    if conan create "$package_path" --version="$version" --build=missing; then
        echo "   ✅ Package created successfully"
        
        # Export to find the package files
        conan export "$package_path" --version="$version"
        
        # Find the package files for Conan 2.x
        PACKAGE_FILE=$(find ~/.conan2/p -name "*${package_name}-${version}*.tgz" 2>/dev/null | head -1)
        
        if [ -n "$PACKAGE_FILE" ]; then
            echo "   📤 Uploading to Cloudsmith..."
            if CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" cloudsmith push conan sparesparrow-conan/sparetools "$PACKAGE_FILE"; then
                echo "   ✅ Successfully uploaded $package_name v$version"
            else
                echo "   ❌ Failed to upload $package_name v$version"
            fi
        else
            echo "   ❌ Could not find package file to upload"
        fi
        
    else
        echo "   ❌ Failed to create package $package_name"
    fi
}

# Publish the working foundation packages
publish_conan_package "packages/foundation/sparetools-base" "sparetools-base" "2.0.3"
publish_conan_package "packages/foundation/sparetools-bootstrap" "sparetools-bootstrap" "2.0.3"
publish_conan_package "packages/foundation/sparetools-cpython" "sparetools-cpython" "3.12.7"
publish_conan_package "packages/foundation/sparetools-shared-dev-tools" "sparetools-shared-dev-tools" "2.0.3"
publish_conan_package "packages/foundation/sparetools-test-harness" "sparetools-test-harness" "2.0.3"
publish_conan_package "packages/schemas" "sparetools-protocols" "1.0.0"
publish_conan_package "packages/python/sparetools-py" "sparetools-py" "1.0.0"

# Publish the fixed embedded packages
publish_conan_package "packages/embedded/sparetools-lvgl" "sparetools-lvgl" "8.3.11"

# Publish MCP packages
publish_conan_package "packages/mcp/sparetools-mcp-prompts" "sparetools-mcp-prompts" "3.13.0"
publish_conan_package "packages/mcp/sparetools-mcp-servers" "sparetools-mcp-servers" "1.0.0"
publish_conan_package "packages/mcp/sparetools-mcp-ecosystem" "sparetools-mcp-ecosystem" "1.0.0"
publish_conan_package "packages/mcp/sparetools-mcp-project-orchestrator" "sparetools-mcp-project-orchestrator" "0.1.0"

echo ""
echo "🎉 Package publishing process complete!"
echo ""
echo "🔍 Verify uploads:"
echo "cloudsmith list packages sparesparrow-conan/sparetools --query='sparetools-base OR sparetools-bootstrap OR sparetools-cpython OR sparetools-shared-dev-tools OR sparetools-test-harness OR sparetools-protocols OR sparetools-py OR sparetools-lvgl OR sparetools-mcp-prompts OR sparetools-mcp-servers OR sparetools-mcp-ecosystem OR sparetools-mcp-project-orchestrator'"
echo ""
echo "🌐 View packages at: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/"
echo ""
echo "📚 For manual upload if needed:"
echo "CLOUDSMITH_API_KEY=\$CLOUDSMITH_API_KEY cloudsmith push conan sparesparrow-conan/sparetools /path/to/package.tgz"
