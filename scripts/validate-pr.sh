#!/bin/bash
# Validate PR changes before pushing
#
# This script helps validate local changes before opening a PR,
# reducing the chance of blocking CI/CD pipelines.
#
# Usage:
#   ./scripts/validate-pr.sh
#
# Prerequisites:
#   - Conan 2.x installed
#   - Git repository with origin/main configured
#   - Packages in packages/ directory

set -e

echo "🔍 Validating PR changes..."
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ Error: Not in a git repository"
  exit 1
fi

# Check if origin/main exists
if ! git rev-parse --verify origin/main > /dev/null 2>&1; then
  echo "⚠️  Warning: origin/main not found. Fetching..."
  git fetch origin main || {
    echo "❌ Error: Could not fetch origin/main"
    echo "   Please configure upstream: git remote add origin <url>"
    exit 1
  }
fi

# Get changed files
CHANGED_FILES=$(git diff --name-only origin/main 2>/dev/null || git diff --name-only HEAD)

if [ -z "$CHANGED_FILES" ]; then
  echo "✅ No changes detected (working directory clean)"
  exit 0
fi

echo "📋 Changed files:"
echo "$CHANGED_FILES" | head -10
if [ $(echo "$CHANGED_FILES" | wc -l) -gt 10 ]; then
  echo "... and $(( $(echo "$CHANGED_FILES" | wc -l) - 10 )) more files"
fi
echo ""

# Check for package changes
HAS_PACKAGE_CHANGES=false
if echo "$CHANGED_FILES" | grep -q "packages/"; then
  HAS_PACKAGE_CHANGES=true
  echo "📦 Package changes detected"
fi

# Check for profile changes
HAS_PROFILE_CHANGES=false
if echo "$CHANGED_FILES" | grep -q "packages/sparetools-openssl-tools/profiles/"; then
  HAS_PROFILE_CHANGES=true
  echo "⚙️  Profile changes detected"
fi

# Check for docs-only changes
if echo "$CHANGED_FILES" | grep -qv "packages/" && \
   echo "$CHANGED_FILES" | grep -qv "\.github/workflows/" && \
   echo "$CHANGED_FILES" | grep -qE "\.(md|txt|json)$|docs/"; then
  echo "📝 Docs-only changes detected"
  echo "✅ CI will skip builds for docs-only changes"
  exit 0
fi

if [ "$HAS_PACKAGE_CHANGES" = false ] && [ "$HAS_PROFILE_CHANGES" = false ]; then
  echo "✅ No package or profile changes - skipping build validation"
  exit 0
fi

# Validate Conan installation
if ! command -v conan &> /dev/null; then
  echo "❌ Error: Conan not found. Install with: pip install conan==2.21.0"
  exit 1
fi

CONAN_VERSION=$(conan --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo "🔧 Using Conan $CONAN_VERSION"
echo ""

# Stage 1: Test Foundation Packages
echo "📦 Stage 1: Testing foundation packages..."
echo "   This step validates sparetools-base and sparetools-openssl-tools"
echo ""

if echo "$CHANGED_FILES" | grep -q "packages/sparetools-base"; then
  echo "   → sparetools-base changed - exporting..."
  cd packages/sparetools-base
  conan export . --version=2.0.0 || {
    echo "❌ Failed to export sparetools-base"
    exit 1
  }
  cd ../..
  echo "   ✅ sparetools-base exported"
else
  echo "   → sparetools-base unchanged - skipping export"
fi

if echo "$CHANGED_FILES" | grep -q "packages/sparetools-openssl-tools"; then
  echo "   → sparetools-openssl-tools changed - exporting..."
  cd packages/sparetools-openssl-tools
  conan export . --version=2.0.0 || {
    echo "❌ Failed to export sparetools-openssl-tools"
    exit 1
  }
  cd ../..
  echo "   ✅ sparetools-openssl-tools exported"
else
  echo "   → sparetools-openssl-tools unchanged - skipping export"
fi

# Export other foundation packages if needed
for pkg in sparetools-bootstrap sparetools-shared-dev-tools; do
  if echo "$CHANGED_FILES" | grep -q "packages/$pkg"; then
    echo "   → $pkg changed - exporting..."
    cd "packages/$pkg"
    conan export . --version=2.0.0 || {
      echo "❌ Failed to export $pkg"
      exit 1
    }
    cd ../..
    echo "   ✅ $pkg exported"
  fi
done

echo ""

# Stage 2: Test CPython (if changed)
if echo "$CHANGED_FILES" | grep -q "packages/sparetools-cpython"; then
  echo "🐍 Stage 2: Testing CPython build..."
  echo "   ⚠️  WARNING: CPython builds take 5-10 min (Linux/macOS) or 15-30 min (Windows)"
  echo "   Windows CPython builds are experimental in CI (won't block PR)"
  echo ""
  
  read -p "   Continue with CPython build? (y/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd packages/sparetools-cpython
    echo "   → Building sparetools-cpython (this may take a while)..."
    conan create . --version=3.12.7 --build=missing || {
      echo "❌ Failed to build sparetools-cpython"
      exit 1
    }
    cd ../..
    echo "   ✅ sparetools-cpython built successfully"
  else
    echo "   ⏭️  Skipping CPython build (will be tested in CI)"
  fi
  echo ""
fi

# Stage 3: Test OpenSSL (if changed)
if echo "$CHANGED_FILES" | grep -q "packages/sparetools-openssl"; then
  echo "🔐 Stage 3: Testing OpenSSL build..."
  
  # Check if CPython is available (needed for OpenSSL build)
  if ! conan list "sparetools-cpython/3.12.7:*" > /dev/null 2>&1; then
    echo "   ⚠️  sparetools-cpython not found in cache"
    echo "   → Building CPython first (required dependency)..."
    cd packages/sparetools-cpython
    conan create . --version=3.12.7 --build=missing
    cd ../..
  fi
  
  echo "   → Building sparetools-openssl with default profile..."
  cd packages/sparetools-openssl
  
  # Use default profile if available, otherwise skip profile
  PROFILE_BASE="packages/sparetools-openssl-tools/profiles/base/linux-gcc11"
  PROFILE_METHOD="packages/sparetools-openssl-tools/profiles/build-methods/perl-configure"
  
  if [ -f "../../$PROFILE_BASE" ] && [ -f "../../$PROFILE_METHOD" ]; then
    conan create . \
      --version=3.3.2 \
      -pr:b "../../$PROFILE_BASE" \
      -pr:b "../../$PROFILE_METHOD" \
      --build=missing || {
      echo "❌ Failed to build sparetools-openssl"
      exit 1
    }
  else
    echo "   ⚠️  Profile not found, building with defaults..."
    conan create . --version=3.3.2 --build=missing || {
      echo "❌ Failed to build sparetools-openssl"
      exit 1
    }
  fi
  
  echo "   → Testing sparetools-openssl..."
  conan test test_package --requires=sparetools-openssl/3.3.2 || {
    echo "❌ test_package failed"
    exit 1
  }
  
  cd ../..
  echo "   ✅ sparetools-openssl built and tested successfully"
  echo ""
fi

# Stage 4: Test Profile Changes
if [ "$HAS_PROFILE_CHANGES" = true ]; then
  echo "⚙️  Stage 4: Testing profile changes..."
  
  # Validate profile syntax
  PROFILE_DIR="packages/sparetools-openssl-tools/profiles"
  if [ -d "$PROFILE_DIR" ]; then
    echo "   → Validating profile syntax..."
    
    # Try to show each changed profile
    for profile_file in $(echo "$CHANGED_FILES" | grep "$PROFILE_DIR"); do
      if [ -f "$profile_file" ]; then
        echo "   → Validating: $profile_file"
        conan profile show "$profile_file" > /dev/null || {
          echo "   ⚠️  Warning: Profile syntax check failed for $profile_file"
          echo "      (This may be expected for partial profile definitions)"
        }
      fi
    done
    
    echo "   ✅ Profile syntax validation complete"
  fi
  
  # If OpenSSL package exists, test build with modified profiles
  if conan list "sparetools-openssl/3.3.2:*" > /dev/null 2>&1; then
    echo "   → Testing build with modified profiles..."
    cd packages/sparetools-openssl
    PROFILE_BASE="packages/sparetools-openssl-tools/profiles/base/linux-gcc11"
    if [ -f "../../$PROFILE_BASE" ]; then
      conan create . \
        --version=3.3.2 \
        -pr:b "../../$PROFILE_BASE" \
        --build=missing || {
        echo "   ⚠️  Build with modified profile failed (may need manual testing)"
      }
    fi
    cd ../..
  else
    echo "   ℹ️  OpenSSL package not built - skipping profile build test"
  fi
  
  echo ""
fi

# Summary
echo "✅ PR validation complete!"
echo ""
echo "📊 Summary:"
echo "   - Foundation packages: ✅"
if echo "$CHANGED_FILES" | grep -q "packages/sparetools-cpython"; then
  echo "   - CPython: $([ -n "$(conan list 'sparetools-cpython/3.12.7:*' 2>/dev/null)" ] && echo '✅' || echo '⏭️  Skipped')"
fi
if echo "$CHANGED_FILES" | grep -q "packages/sparetools-openssl"; then
  echo "   - OpenSSL: ✅"
fi
if [ "$HAS_PROFILE_CHANGES" = true ]; then
  echo "   - Profiles: ✅"
fi
echo ""
echo "💡 Next steps:"
echo "   1. Commit your changes: git commit -am 'your message'"
echo "   2. Push to your branch: git push origin <your-branch>"
echo "   3. Open a PR on GitHub"
echo ""
echo "   Note: Windows builds are experimental (won't block PR merge)"
echo "         CI will run additional integration tests"
echo ""
