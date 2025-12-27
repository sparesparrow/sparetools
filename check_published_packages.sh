#!/bin/bash

echo "=== Checking Published SpareTools Packages ==="
echo "Repository: https://cloudsmith.io/~sparesparrow-conan/packages/"
echo ""

echo "🔍 Querying Cloudsmith for sparetools packages..."

# Get all sparetools packages
cloudsmith list packages sparesparrow-conan/openssl-conan --query="sparetools" | head -20

echo ""
echo "📊 Package Summary:"

# Count packages by category
echo "Foundation packages:" 
cloudsmith list packages sparesparrow-conan/openssl-conan --query="sparetools-base OR sparetools-bootstrap OR sparetools-shared-dev-tools" 2>/dev/null | grep -c "sparetools" || echo "Query failed"

echo ""
echo "Consumer packages:"
cloudsmith list packages sparesparrow-conan/openssl-conan --query="sparetools-mia OR sparetools-nucleus" 2>/dev/null | grep -c "sparetools" || echo "Query failed"

echo ""
echo "New consolidated packages (check these):"
PACKAGES_TO_CHECK=("sparetools-pentest-toolkit" "sparetools-prompt-system" "sparetools-sdr-tools" "sparetools-streaming-solutions" "sparetools-wifi-sensing")

for package in "${PACKAGES_TO_CHECK[@]}"; do
    echo -n "$package: "
    cloudsmith list packages sparesparrow-conan/openssl-conan --query="$package" 2>/dev/null | grep -c "$package" || echo "Not found"
done

echo ""
echo "🌐 View all packages at: https://cloudsmith.io/~sparesparrow-conan/packages/"
echo "📖 Documentation: https://help.cloudsmith.io/docs/conan"
