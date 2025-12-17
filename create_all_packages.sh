#!/bin/bash
# Simple script to create all SpareTools packages in dependency order

set -e  # Exit on any error

echo "🚀 Creating all SpareTools packages..."

# Foundation packages (in dependency order)
echo "📦 Building foundation packages..."

cd packages/foundation/sparetools-recipe-base
echo "  - sparetools-recipe-base/1.0.0"
conan create . --name sparetools-recipe-base --version 1.0.0 --user sparetools --channel stable

cd ../sparetools-base
echo "  - sparetools-base/2.0.0"
conan create . --name sparetools-base --version 2.0.0 --user sparetools --channel stable

cd ../sparetools-cpython
echo "  - sparetools-cpython/3.12.7"
conan create . --name sparetools-cpython --version 3.12.7 --user sparetools --channel stable

cd ../sparetools-test-harness
echo "  - sparetools-test-harness/2.0.0"
conan create . --name sparetools-test-harness --version 2.0.0 --user sparetools --channel stable

cd ../sparetools-shared-dev-tools
echo "  - sparetools-shared-dev-tools/2.0.0"
conan create . --name sparetools-shared-dev-tools --version 2.0.0 --user sparetools --channel stable

cd ../sparetools-bootstrap
echo "  - sparetools-bootstrap/2.0.0"
conan create . --name sparetools-bootstrap --version 2.0.0 --user sparetools --channel stable

# Consumer packages
echo "📦 Building consumer packages..."

cd ../../consumers/sparetools-obd-sim
echo "  - sparetools-obd-sim/2.0.0"
conan create . --name sparetools-obd-sim --version 2.0.0 --user sparetools --channel stable

cd ../android/sparetools-cliphist-android
echo "  - sparetools-cliphist-android/1.0.0"
conan create . --name sparetools-cliphist-android --version 1.0.0 --user sparetools --channel stable

cd ../../openssl/sparetools-openssl
echo "  - sparetools-openssl/3.3.2"
conan create . --name sparetools-openssl --version 3.3.2 --user sparetools --channel stable

cd ../sparetools-openssl-tools
echo "  - sparetools-openssl-tools/2.0.0"
conan create . --name sparetools-openssl-tools --version 2.0.0 --user sparetools --channel stable

cd ../../mia/sparetools-mia
echo "  - sparetools-mia/2.0.0"
conan create . --name sparetools-mia --version 2.0.0 --user sparetools --channel stable

cd ../../mcp/sparetools-mcp-orchestrator
echo "  - sparetools-mcp-orchestrator/2.0.0"
conan create . --name sparetools-mcp-orchestrator --version 2.0.0 --user sparetools --channel stable

cd ../sparetools-tinymcp
echo "  - sparetools-tinymcp/2.0.0"
conan create . --name sparetools-tinymcp --version 2.0.0 --user sparetools --channel stable

cd ../sparetools-mcpserver-cpp
echo "  - sparetools-mcpserver-cpp/2.0.0"
conan create . --name sparetools-mcpserver-cpp --version 2.0.0 --user sparetools --channel stable

cd ../../esp32/sparetools-nucleus
echo "  - sparetools-nucleus/0.1.0"
conan create . --name sparetools-nucleus --version 0.1.0 --user sparetools --channel stable

# Deprecated packages (optional)
echo "📦 Building deprecated packages..."

cd ../../../deprecated/sparetools-openssl-autotools
echo "  - sparetools-openssl-autotools/3.3.2"
conan create . --name sparetools-openssl-autotools --version 3.3.2 --user sparetools --channel stable || echo "  ⚠️  Failed (expected for deprecated)"

cd ../sparetools-openssl-cmake
echo "  - sparetools-openssl-cmake/3.3.2"
conan create . --name sparetools-openssl-cmake --version 3.3.2 --user sparetools --channel stable || echo "  ⚠️  Failed (expected for deprecated)"

cd ../sparetools-openssl-hybrid
echo "  - sparetools-openssl-hybrid/3.3.2"
conan create . --name sparetools-openssl-hybrid --version 3.3.2 --user sparetools --channel stable || echo "  ⚠️  Failed (expected for deprecated)"

cd ../sparetools-openssl-tools-mini
echo "  - sparetools-openssl-tools-mini/1.0.0"
conan create . --name sparetools-openssl-tools-mini --version 1.0.0 --user sparetools --channel stable || echo "  ⚠️  Failed (expected for deprecated)"

cd ../../../../..

echo "✅ All packages created successfully!"
echo ""
echo "📋 To list created packages:"
echo "  conan list 'sparetools*'"
echo ""
echo "📋 To upload to remote repository:"
echo "  ./upload_packages.sh <remote-name>"