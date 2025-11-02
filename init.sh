#!/bin/bash
# SpareTools Zero-Copy Bootstrap Script
# Creates zero-copy environment using OS symlinks to Conan cache

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVENV_ROOT="${HOME}/.openssl-devenv"

echo "?? SpareTools Zero-Copy Bootstrap"
echo "=================================="

# 1. Detect environment
detect_environment() {
    echo "?? Detecting environment..."
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    echo "   OS: $OS"
    echo "   Architecture: $ARCH"
}

# 2. Setup Conan
setup_conan() {
    echo "?? Setting up Conan..."
    
    # Ensure Conan 2.x
    if ! command -v conan &> /dev/null; then
        echo "? Conan 2.x required. Install: pip install conan"
        exit 1
    fi
    
    if ! conan --version | grep -q "Conan version 2"; then
        echo "? Conan 2.x required. Found: $(conan --version)"
        echo "   Install: pip install --upgrade conan"
        exit 1
    fi
    
    # Add remote
    conan remote add sparesparrow-conan \
        https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
        --force 2>/dev/null || echo "   ??  Remote already configured"
    
    echo "   ? Conan remote configured"
}

# 3. Install dependencies (to Conan cache)
install_dependencies() {
    echo "?? Installing dependencies to Conan cache..."
    
    # Install base utilities
    echo "   Installing sparetools-base/2.0.0..."
    conan install --requires=sparetools-base/2.0.0@ \
        --build=missing \
        -s build_type=Release 2>/dev/null || {
        # If not available remotely, build locally
        echo "   Building sparetools-base locally..."
        cd "${SCRIPT_DIR}/packages/sparetools-base"
        conan create . --version=2.0.0 --build=missing
        cd "${SCRIPT_DIR}"
    }
    
    # Install CPython (builds or downloads to cache)
    echo "   Installing sparetools-cpython/3.12.7..."
    conan install --tool-requires=sparetools-cpython/3.12.7@ \
        --build=missing \
        -s build_type=Release 2>/dev/null || {
        # If not available remotely, build locally
        echo "   Building sparetools-cpython locally..."
        cd "${SCRIPT_DIR}/packages/sparetools-cpython"
        conan create . --version=3.12.7 --build=missing
        cd "${SCRIPT_DIR}"
    }
    
    # Install OpenSSL
    echo "   Installing sparetools-openssl/3.3.2..."
    conan install --requires=sparetools-openssl/3.3.2@ \
        -o sparetools-openssl/*:shared=True \
        -o sparetools-openssl/*:fips=False \
        --build=missing \
        -s build_type=Release 2>/dev/null || {
        # If not available remotely, build locally
        echo "   Building sparetools-openssl locally..."
        cd "${SCRIPT_DIR}/packages/sparetools-openssl"
        conan create . --version=3.3.2 \
            -o shared=True \
            -o fips=False \
            --build=missing
        cd "${SCRIPT_DIR}"
    }
    
    echo "   ? Dependencies in Conan cache"
}

# 4. Create zero-copy environment (symlinks)
create_zero_copy_env() {
    echo "?? Creating zero-copy environment..."
    
    # Clean existing
    rm -rf "${DEVENV_ROOT}"
    mkdir -p "${DEVENV_ROOT}"/{bin,lib,include,ssl}
    
    # Find packages in Conan cache
    CONAN_CACHE="${HOME}/.conan2/p"
    
    if [ ! -d "${CONAN_CACHE}" ]; then
        echo "   ? Conan cache not found: ${CONAN_CACHE}"
        return 1
    fi
    
    # Symlink CPython
    CPYTHON_PKG=$(find "${CONAN_CACHE}" -type d -path "*/sparetools-cpython*/package/*/bin" 2>/dev/null | head -1)
    if [ -n "$CPYTHON_PKG" ]; then
        CPYTHON_ROOT=$(dirname "$CPYTHON_PKG")
        echo "   Found CPython at: ${CPYTHON_ROOT}"
        
        # Symlink binaries
        for bin_file in "${CPYTHON_ROOT}"/bin/*; do
            if [ -f "$bin_file" ] || [ -x "$bin_file" ]; then
                ln -sf "$bin_file" "${DEVENV_ROOT}/bin/$(basename "$bin_file")"
            fi
        done
        
        # Symlink libs
        if [ -d "${CPYTHON_ROOT}/lib" ]; then
            for lib_file in "${CPYTHON_ROOT}"/lib/*; do
                if [ -f "$lib_file" ] || [ -L "$lib_file" ]; then
                    ln -sf "$lib_file" "${DEVENV_ROOT}/lib/$(basename "$lib_file")"
                fi
            done
        fi
        
        echo "   ? CPython symlinked from cache"
    else
        echo "   ??  CPython package not found in cache"
    fi
    
    # Symlink OpenSSL
    OPENSSL_PKG=$(find "${CONAN_CACHE}" -type d -path "*/sparetools-openssl*/package/*/bin" 2>/dev/null | head -1)
    if [ -n "$OPENSSL_PKG" ]; then
        OPENSSL_ROOT=$(dirname "$OPENSSL_PKG")
        echo "   Found OpenSSL at: ${OPENSSL_ROOT}"
        
        # Symlink binaries
        for bin_file in "${OPENSSL_ROOT}"/bin/*; do
            if [ -f "$bin_file" ] || [ -x "$bin_file" ]; then
                ln -sf "$bin_file" "${DEVENV_ROOT}/bin/$(basename "$bin_file")"
            fi
        done
        
        # Symlink libs
        if [ -d "${OPENSSL_ROOT}/lib" ] || [ -d "${OPENSSL_ROOT}/lib64" ]; then
            LIB_DIR="${OPENSSL_ROOT}/lib64"
            [ -d "${OPENSSL_ROOT}/lib" ] && LIB_DIR="${OPENSSL_ROOT}/lib"
            for lib_file in "${LIB_DIR}"/*; do
                if [ -f "$lib_file" ] || [ -L "$lib_file" ]; then
                    ln -sf "$lib_file" "${DEVENV_ROOT}/lib/$(basename "$lib_file")"
                fi
            done
        fi
        
        # Symlink includes
        if [ -d "${OPENSSL_ROOT}/include" ]; then
            ln -sf "${OPENSSL_ROOT}/include" "${DEVENV_ROOT}/include/openssl" 2>/dev/null || true
        fi
        
        # Symlink SSL config
        if [ -d "${OPENSSL_ROOT}/ssl" ]; then
            ln -sf "${OPENSSL_ROOT}/ssl" "${DEVENV_ROOT}/ssl" 2>/dev/null || true
        fi
        
        echo "   ? OpenSSL symlinked from cache"
    else
        echo "   ??  OpenSSL package not found in cache"
    fi
}

# 5. Generate activation script
generate_activation_script() {
    echo "?? Generating activation script..."
    
    cat > "${DEVENV_ROOT}/activate.sh" <<'EOF'
#!/bin/bash
# SpareTools Zero-Copy Environment Activation

export OPENSSL_DEVENV_ROOT="$HOME/.openssl-devenv"
export PATH="$OPENSSL_DEVENV_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$OPENSSL_DEVENV_ROOT/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$OPENSSL_DEVENV_ROOT/lib/pkgconfig:$PKG_CONFIG_PATH"
export PYTHONHOME="$OPENSSL_DEVENV_ROOT"

# FIPS mode (if available)
if [ -f "$OPENSSL_DEVENV_ROOT/ssl/fipsmodule.cnf" ]; then
    export OPENSSL_CONF="$OPENSSL_DEVENV_ROOT/ssl/openssl.cnf"
    export OPENSSL_FIPS=1
    echo "? FIPS mode enabled"
fi

echo "? SpareTools environment activated"
echo "   Python: $(which python3 2>/dev/null || which python 2>/dev/null || echo 'not found')"
echo "   OpenSSL: $(which openssl 2>/dev/null || echo 'not found')"
if command -v openssl &> /dev/null; then
    echo "   Version: $(openssl version 2>/dev/null)"
fi
EOF

    chmod +x "${DEVENV_ROOT}/activate.sh"
    echo "   ? Activation script: ${DEVENV_ROOT}/activate.sh"
}

# 6. Verify installation
verify_installation() {
    echo "?? Verifying installation..."
    
    source "${DEVENV_ROOT}/activate.sh"
    
    # Check Python
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 || echo "unknown")
        echo "   ? Python: $PYTHON_VERSION"
    else
        echo "   ? Python not found"
        return 1
    fi
    
    # Check OpenSSL
    if command -v openssl &> /dev/null; then
        OPENSSL_VERSION=$(openssl version 2>&1 || echo "unknown")
        echo "   ? OpenSSL: $OPENSSL_VERSION"
    else
        echo "   ??  OpenSSL not found (may not be built yet)"
    fi
    
    # Check symlinks (no actual copies)
    SYMLINK_COUNT=$(find "${DEVENV_ROOT}" -type l 2>/dev/null | wc -l)
    FILE_COUNT=$(find "${DEVENV_ROOT}" -type f 2>/dev/null | wc -l)
    echo "   ? Zero-copy verified: $SYMLINK_COUNT symlinks, $FILE_COUNT files"
    
    # Warn if too many files (should be mostly symlinks)
    if [ "$FILE_COUNT" -gt 10 ] && [ "$SYMLINK_COUNT" -lt "$FILE_COUNT" ]; then
        echo "   ??  Warning: Many files found (expected mostly symlinks)"
    fi
}

# Main execution
main() {
    detect_environment
    setup_conan
    install_dependencies
    create_zero_copy_env
    generate_activation_script
    verify_installation
    
    echo ""
    echo "? Bootstrap complete!"
    echo ""
    echo "To activate:"
    echo "  source ${DEVENV_ROOT}/activate.sh"
    echo ""
    echo "To verify:"
    echo "  python3 --version"
    echo "  openssl version"
    echo ""
    echo "Zero-copy environment located at: ${DEVENV_ROOT}"
}

main "$@"
