#!/bin/bash
# Upload all SpareTools packages to a remote repository

if [ $# -eq 0 ]; then
    echo "Usage: $0 <remote-name>"
    echo "Example: $0 cloudsmith"
    echo ""
    echo "Available remotes:"
    conan remote list
    exit 1
fi

REMOTE="$1"

echo "☁️  Uploading SpareTools packages to remote: $REMOTE"

# Upload foundation packages first
echo "📤 Uploading foundation packages..."

conan upload --name sparetools-recipe-base --version 1.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-base --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-cpython --version 3.12.7 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-test-harness --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-shared-dev-tools --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-bootstrap --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force

# Upload consumer packages
echo "📤 Uploading consumer packages..."

conan upload --name sparetools-obd-sim --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-cliphist-android --version 1.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-openssl --version 3.3.2 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-openssl-tools --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-mia --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-mcp-orchestrator --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-tinymcp --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-mcpserver-cpp --version 2.0.0 --user sparetools --channel stable -r "$REMOTE" --force
conan upload --name sparetools-nucleus --version 0.1.0 --user sparetools --channel stable -r "$REMOTE" --force

# Upload deprecated packages
echo "📤 Uploading deprecated packages..."

conan upload --name sparetools-openssl-autotools --version 3.3.2 --user sparetools --channel stable -r "$REMOTE" --force || echo "⚠️  Failed to upload deprecated package"
conan upload --name sparetools-openssl-cmake --version 3.3.2 --user sparetools --channel stable -r "$REMOTE" --force || echo "⚠️  Failed to upload deprecated package"
conan upload --name sparetools-openssl-hybrid --version 3.3.2 --user sparetools --channel stable -r "$REMOTE" --force || echo "⚠️  Failed to upload deprecated package"
conan upload --name sparetools-openssl-tools-mini --version 1.0.0 --user sparetools --channel stable -r "$REMOTE" --force || echo "⚠️  Failed to upload deprecated package"

echo "✅ All packages uploaded successfully!"
echo ""
echo "📋 To verify uploaded packages:"
echo "  conan list 'sparetools*' -r $REMOTE"