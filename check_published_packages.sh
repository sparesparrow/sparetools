#!/bin/bash

echo "=== Checking Published SpareTools Packages ==="
echo "Repository: https://cloudsmith.io/~sparesparrow-conan/packages/"
echo ""

echo "🔍 Querying Cloudsmith for sparetools packages..."

# Get all sparetools packages
cloudsmith list packages sparesparrow-conan/sparetools --query="sparetools" | head -20

echo ""
echo "📊 Package Summary:"

# Count packages by category
echo "Foundation packages:"
cloudsmith list packages sparesparrow-conan/sparetools --query="sparetools-base OR sparetools-bootstrap OR sparetools-cpython OR sparetools-shared-dev-tools OR sparetools-test-harness OR sparetools-protocols OR sparetools-py" 2>/dev/null | grep -c "sparetools\|sparesparrow" || echo "Query failed"

echo ""
echo "Consumer packages:"
cloudsmith list packages sparesparrow-conan/sparetools --query="sparetools-mia OR sparetools-nucleus OR sparetools-bpm-detector" 2>/dev/null | grep -c "sparetools" || echo "Query failed"

echo ""
echo "Foundation packages status:"
PACKAGES_TO_CHECK=("sparetools-base" "sparetools-bootstrap" "sparetools-cpython" "sparetools-shared-dev-tools" "sparetools-test-harness" "sparetools-protocols" "sparetools-py")

for package in "${PACKAGES_TO_CHECK[@]}"; do
    echo -n "$package: "
    cloudsmith list packages sparesparrow-conan/sparetools --query="$package" 2>/dev/null | grep -c "$package" || echo "Not found"
done

echo ""
echo "🌐 View all packages at: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/"
echo "📖 Documentation: https://help.cloudsmith.io/docs/conan"
