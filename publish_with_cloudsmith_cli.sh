#!/bin/bash

echo "=== Publishing SpareTools Packages using Cloudsmith CLI ==="
echo "Repository: sparesparrow-conan/openssl-conan"
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

# Authenticate with cloudsmith-cli
echo "🔐 Authenticating with Cloudsmith..."
cloudsmith login --api-key "$CLOUDSMITH_API_KEY" || {
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
        
        # Find the package files (this is a simplified approach)
        PACKAGE_FILE=$(find ~/.conan/data -name "*${package_name}-${version}*" -type f | head -1)
        
        if [ -n "$PACKAGE_FILE" ]; then
            echo "   📤 Uploading to Cloudsmith..."
            if cloudsmith push conan sparesparrow-conan/openssl-conan "$PACKAGE_FILE"; then
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

# Publish the main new consolidated packages
publish_conan_package "packages/pentest/sparetools-pentest-toolkit" "sparetools-pentest-toolkit" "1.0.0"
publish_conan_package "packages/prompt/sparetools-prompt-system" "sparetools-prompt-system" "1.0.0"
publish_conan_package "packages/sdr/sparetools-sdr-tools" "sparetools-sdr-tools" "1.0.0"
publish_conan_package "packages/streaming/sparetools-streaming-solutions" "sparetools-streaming-solutions" "1.0.0"
publish_conan_package "packages/wifi/sparetools-wifi-sensing" "sparetools-wifi-sensing" "1.0.0"

echo ""
echo "🎉 Package publishing process complete!"
echo ""
echo "🔍 Verify uploads:"
echo "cloudsmith list packages sparesparrow-conan/openssl-conan --query='sparetools-pentest-toolkit OR sparetools-prompt-system OR sparetools-sdr-tools OR sparetools-streaming-solutions OR sparetools-wifi-sensing'"
echo ""
echo "🌐 View packages at: https://cloudsmith.io/~sparesparrow-conan/packages/"
echo ""
echo "📚 For manual upload if needed:"
echo "cloudsmith push conan sparesparrow-conan/openssl-conan /path/to/package.tgz"
