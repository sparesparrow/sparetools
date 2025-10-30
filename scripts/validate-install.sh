#!/bin/bash
# Validate SpareTools installation

echo "🔍 Validating SpareTools installation..."
echo ""

# Check Conan
echo "1. Checking Conan..."
if ! command -v conan &> /dev/null; then
    echo "   ❌ Conan not installed"
    exit 1
fi
CONAN_VERSION=$(conan --version 2>&1 | head -1)
echo "   ✅ Conan: $CONAN_VERSION"

# Check Conan version (should be 2.x)
if echo "$CONAN_VERSION" | grep -q "Conan version 2"; then
    echo "   ✅ Conan 2.x detected"
else
    echo "   ⚠️  Warning: SpareTools requires Conan 2.x"
fi

# Check remote
echo ""
echo "2. Checking Cloudsmith remote..."
if conan remote list | grep -q "sparesparrow-conan"; then
    echo "   ✅ Remote configured (sparesparrow-conan)"
elif conan remote list | grep -q "cloudsmith"; then
    echo "   ✅ Remote configured (cloudsmith - legacy name)"
else
    echo "   ⚠️  Remote not found. Add with:"
    echo "      conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/"
    exit 1
fi

# Check packages in cache
echo ""
echo "3. Checking cached packages..."
echo ""
if conan list 'sparetools-*:*' 2>/dev/null | grep -q "sparetools"; then
    conan list 'sparetools-*:*' | head -20
else
    echo "   ⚠️  No SpareTools packages found in local cache"
    echo "   Run: conan install --requires=sparetools-cpython/3.12.7 -r sparesparrow-conan"
fi

# Check remote packages
echo ""
echo "4. Checking remote packages..."
echo ""
if conan search 'sparetools-base*' -r sparesparrow-conan 2>/dev/null | grep -q "sparetools-base"; then
    echo "   ✅ sparetools-base found on remote"
else
    echo "   ⚠️  sparetools-base not found on remote"
fi

if conan search 'sparetools-cpython*' -r sparesparrow-conan 2>/dev/null | grep -q "sparetools-cpython"; then
    echo "   ✅ sparetools-cpython found on remote"
else
    echo "   ⚠️  sparetools-cpython not found on remote"
fi

echo ""
echo "✅ Validation complete!"
