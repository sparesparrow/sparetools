#!/bin/bash
# SpareTools Package Upload Script

set -e  # Exit on any error

echo "=== SpareTools Package Upload Script ==="
echo

# Check if authenticated
echo "Checking authentication status..."
if ! conan remote list-users | grep -q "sparetools.*authenticated"; then
    echo "❌ Not authenticated with sparetools remote"
    echo "Please run: conan remote login sparetools <your-cloudsmith-username>"
    exit 1
fi

echo "✅ Authenticated with sparetools remote"
echo

# Function to upload package
upload_package() {
    local package=$1
    echo "📦 Uploading $package..."

    if conan upload "$package" -r sparetools -c --force; then
        echo "✅ Successfully uploaded $package"
    else
        echo "❌ Failed to upload $package"
        return 1
    fi
}

echo "=== Uploading Foundation Packages ==="

# Core foundation packages
upload_package "sparetools-cpython/3.12.7"
upload_package "sparetools-base/2.0.3"
upload_package "sparetools-bootstrap/2.0.0"

echo
echo "=== Uploading Consumer Packages ==="

# MIA and other consumers
upload_package "sparetools-mia/2.0.0"

echo
echo "=== Uploading Python Tool Packages ==="

# Python tools (if built)
# upload_package "sparetools-fs-tools/*"
# upload_package "sparetools-proc-tools/*"
# upload_package "sparetools-net-tools/*"

echo
echo "=== Upload Complete ==="
echo
echo "To verify uploads, run:"
echo "conan search '*' -r sparetools"
echo
echo "To use packages in new projects:"
echo 'conan install sparetools-mia/2.0.0@ -r sparetools'