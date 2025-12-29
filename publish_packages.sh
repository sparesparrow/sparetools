#!/bin/bash

echo "=== Publishing SpareTools Packages to Cloudsmith ==="
echo "Repository: sparesparrow-conan/sparetools"
echo ""

# Check if CLOUDSMITH_API_KEY is set
if [ -z "$CLOUDSMITH_API_KEY" ]; then
    echo "❌ Error: CLOUDSMITH_API_KEY environment variable not set"
    echo "Please set it with: export CLOUDSMITH_API_KEY=your_api_key_here"
    exit 1
fi

echo "🔑 Authenticating with Cloudsmith..."
cloudsmith login --api-key "$CLOUDSMITH_API_KEY" || {
    echo "❌ Authentication failed"
    exit 1
}

echo ""
echo "📦 Publishing packages..."

# Function to publish a package
publish_package() {
    local package_path=$1
    local package_name=$2
    
    echo ""
    echo "Publishing: $package_name"
    
    if [ -f "$package_path/conanfile.py" ]; then
        echo "Found conanfile.py at: $package_path"
        
        # Try to create and upload the package
        if conan create "$package_path" --build=missing; then
            echo "✅ Package created successfully"
            
            # Upload to Cloudsmith
            if conan upload "$package_name/*" -r sparesparrow-conan --confirm; then
                echo "✅ Package uploaded to Cloudsmith"
            else
                echo "❌ Failed to upload package"
            fi
        else
            echo "❌ Failed to create package"
        fi
    else
        echo "❌ No conanfile.py found at: $package_path"
    fi
}

# Publish the main new packages
echo "🚀 Publishing new consolidated packages..."

publish_package "packages/pentest/sparetools-pentest-toolkit" "sparetools-pentest-toolkit"
publish_package "packages/prompt/sparetools-prompt-system" "sparetools-prompt-system"  
publish_package "packages/sdr/sparetools-sdr-tools" "sparetools-sdr-tools"
publish_package "packages/streaming/sparetools-streaming-solutions" "sparetools-streaming-solutions"
publish_package "packages/wifi/sparetools-wifi-sensing" "sparetools-wifi-sensing"

echo ""
echo "🎉 Package publishing complete!"
echo "Check your packages at: https://cloudsmith.io/~sparesparrow-conan/packages/"
