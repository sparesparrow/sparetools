#!/bin/bash
# Rebuild SpareTools CPython with cloudsmith-cli integration

set -e

echo "=== Rebuilding SpareTools CPython with cloudsmith-cli ==="
echo

# Change to the CPython package directory
cd packages/foundation/sparetools-cpython

echo "🔧 Building sparetools-cpython/3.12.7 with cloudsmith-cli..."
conan build . --build=missing

echo
echo "📦 Creating package..."
conan export-pkg . --force

echo
echo "✅ Build complete!"
echo
echo "To test cloudsmith-cli integration:"
echo "conan install sparetools-cpython/3.12.7@ --build=missing"
echo "source conanbuild.sh  # or conanrun.sh"
echo "cloudsmith --help"