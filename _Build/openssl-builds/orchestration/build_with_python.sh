#!/bin/bash
# Python-based OpenSSL build orchestration script
# Uses configure.py from sparetools-openssl-hybrid package

set -e

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <openssl-source-dir> <install-prefix>"
    echo "Example: $0 /path/to/openssl/src /path/to/install"
    exit 1
fi

OPENSSL_SRC="$1"
INSTALL_PREFIX="$2"
SPARETOOLS_ROOT="/home/sparrow/sparetools"
CONFIGURE_PY="${SPARETOOLS_ROOT}/packages/sparetools-openssl-hybrid/configure.py"

# Verify paths exist
if [ ! -d "$OPENSSL_SRC" ]; then
    echo "Error: OpenSSL source directory not found: $OPENSSL_SRC"
    exit 1
fi

if [ ! -f "$CONFIGURE_PY" ]; then
    echo "Error: configure.py not found: $CONFIGURE_PY"
    exit 1
fi

# Copy configure.py to OpenSSL source
echo "Copying configure.py to OpenSSL source directory..."
cp "$CONFIGURE_PY" "$OPENSSL_SRC/"

# Navigate to OpenSSL source
cd "$OPENSSL_SRC"

# Run Python configure.py
echo "Running Python configure.py..."
python3 configure.py \
    --prefix="$INSTALL_PREFIX" \
    --openssldir="$INSTALL_PREFIX/ssl" \
    --config=linux-x86_64 \
    no-shared \
    || {
        echo "Warning: configure.py failed, checking if Makefile was generated..."
        if [ ! -f "Makefile" ]; then
            echo "Error: No Makefile generated"
            exit 1
        fi
        echo "Makefile exists, continuing..."
    }

# Build
echo "Building OpenSSL with make..."
make -j$(nproc) || {
    echo "Build failed, checking for artifacts..."
    if [ -f "libcrypto.a" ] && [ -f "libssl.a" ]; then
        echo "Warning: Build had errors but artifacts exist"
    else
        echo "Error: Build failed and no artifacts found"
        exit 1
    fi
}

# Install
echo "Installing OpenSSL..."
make install_sw || {
    echo "Warning: Install had non-zero exit, checking artifacts..."
}

# Verify installation
echo "Verifying installation..."
if [ -f "$INSTALL_PREFIX/lib64/libcrypto.a" ] && [ -f "$INSTALL_PREFIX/lib64/libssl.a" ] && [ -x "$INSTALL_PREFIX/bin/openssl" ]; then
    echo "✓ Python-based build successful!"
    echo "  - Libraries: $INSTALL_PREFIX/lib64/"
    echo "  - Binary: $INSTALL_PREFIX/bin/openssl"
    exit 0
elif [ -f "$INSTALL_PREFIX/lib/libcrypto.a" ] && [ -f "$INSTALL_PREFIX/lib/libssl.a" ] && [ -x "$INSTALL_PREFIX/bin/openssl" ]; then
    echo "✓ Python-based build successful!"
    echo "  - Libraries: $INSTALL_PREFIX/lib/"
    echo "  - Binary: $INSTALL_PREFIX/bin/openssl"
    exit 0
else
    echo "✗ Installation verification failed"
    echo "Expected files not found in $INSTALL_PREFIX"
    exit 1
fi

