#!/bin/bash
set -euo pipefail

echo "=== Conan Environment Validation ==="

# Check Conan version (must be 2.x)
CONAN_VERSION=$(conan --version | grep -oP '\d+\.\d+\.\d+')
if [[ ! "$CONAN_VERSION" =~ ^2\. ]]; then
  echo "❌ Conan 2.x required (found: $CONAN_VERSION)"
  exit 1
fi

echo "✅ Conan version: $CONAN_VERSION"

# Check Cloudsmith remote exists
if ! conan remote list | grep -q "sparetools"; then
  echo "⚠️  Adding Cloudsmith remote..."
  conan remote add sparetools \
    https://conan.cloudsmith.io/sparesparrow-conan/sparetools/
fi

echo "✅ Cloudsmith remote configured"

# Test authentication (skip in local development if packages are cached)
if ! conan remote list-users sparetools 2>/dev/null; then
  echo "⚠️  Cloudsmith authentication not configured"
  echo "For production use: conan remote login sparetools spare-sparrow -p \$CLOUDSMITH_API_KEY"
  echo "For local development: checking if packages exist in local cache..."
  AUTH_CONFIGURED=false
else
  echo "✅ Cloudsmith authentication verified"
  AUTH_CONFIGURED=true
fi

# Check critical packages exist (remote or local cache)
for pkg in "sparetools-base/2.0.3" "sparetools-cpython/3.12.7" "sparetools-protocols/1.0.1" "sparetools-embedded/1.0.0"; do
  echo -n "Checking $pkg... "
  if $AUTH_CONFIGURED && conan search "$pkg" -r=sparetools &>/dev/null; then
    echo "✅ (remote)"
  elif conan search "$pkg" &>/dev/null; then
    echo "✅ (local cache)"
  else
    echo "❌ NOT FOUND"
    if $AUTH_CONFIGURED; then
      echo "Package $pkg not found on Cloudsmith or in local cache"
      echo "Upload command: conan upload \"$pkg\" -r=sparetools --confirm"
    else
      echo "Package $pkg not found in local cache"
      echo "Build locally: cd packages/foundation/sparetools-base && conan create ."
    fi
    exit 1
  fi
done

echo "✅ Environment validated - all critical packages available"
echo ""
echo "Next steps:"
echo "1. Run this script in each project directory before integration"
echo "2. All SpareTools packages are available for consumption"
echo "3. Proceed with project integration following the plan"