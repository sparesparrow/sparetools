#!/bin/bash
# Upload reusable artifacts to Cloudsmith
# Usage: ./scripts/upload_artifacts_to_cloudsmith.sh [firmware|tools|mcp-servers|dependencies|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARTIFACT_TYPE="${1:-all}"
VERSION="${2:-$(git describe --tags --always 2>/dev/null || echo 'latest')}"

# Cloudsmith configuration
CLOUDSMITH_ORG="sparesparrow-conan"
CLOUDSMITH_REPO="sparetools"

echo "=== Uploading Artifacts to Cloudsmith ==="
echo "Repository: $CLOUDSMITH_ORG/$CLOUDSMITH_REPO"
echo "Version: $VERSION"
echo "Artifact Type: $ARTIFACT_TYPE"
echo ""

# Check for Cloudsmith CLI
if ! command -v cloudsmith &> /dev/null; then
    echo "Installing Cloudsmith CLI..."
    pip install cloudsmith-cli
fi

# Check for API key
if [ -z "${CLOUDSMITH_API_KEY:-}" ]; then
    echo "❌ Error: CLOUDSMITH_API_KEY environment variable not set"
    echo "Please set it with: export CLOUDSMITH_API_KEY=your_api_key_here"
    exit 1
fi

# Authenticate
echo "🔐 Authenticating with Cloudsmith..."
cloudsmith whoami || {
    echo "❌ Authentication failed"
    exit 1
}

# Upload firmware
if [[ "$ARTIFACT_TYPE" == "all" || "$ARTIFACT_TYPE" == "firmware" ]]; then
    echo ""
    echo "📦 Uploading Firmware Binaries..."
    
    ESP32_BPM_DIR="$REPO_ROOT/../embedded-systems/esp32-bpm-detector"
    
    if [ -d "$ESP32_BPM_DIR/.pio/build" ]; then
        mkdir -p /tmp/firmware-artifacts
        
        # ESP32-S3
        if [ -f "$ESP32_BPM_DIR/.pio/build/esp32-s3-release/firmware.bin" ]; then
            cp "$ESP32_BPM_DIR/.pio/build/esp32-s3-release/firmware.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32s3-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32-s3-release/bootloader.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32s3-bootloader-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32-s3-release/partitions.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32s3-partitions-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32-s3-release/firmware.elf" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32s3-$VERSION.elf"
        fi
        
        # ESP32
        if [ -f "$ESP32_BPM_DIR/.pio/build/esp32dev-release/firmware.bin" ]; then
            cp "$ESP32_BPM_DIR/.pio/build/esp32dev-release/firmware.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32dev-release/bootloader.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32-bootloader-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32dev-release/partitions.bin" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32-partitions-$VERSION.bin"
            cp "$ESP32_BPM_DIR/.pio/build/esp32dev-release/firmware.elf" "/tmp/firmware-artifacts/esp32-bpm-detector-esp32-$VERSION.elf"
        fi
        
        # Upload
        for file in /tmp/firmware-artifacts/*.bin /tmp/firmware-artifacts/*.elf; do
            if [ -f "$file" ]; then
                echo "  Uploading $(basename $file)..."
                cloudsmith upload raw "$CLOUDSMITH_ORG/$CLOUDSMITH_REPO" "$file" \
                    --name "$(basename $file)" \
                    --version "$VERSION" \
                    --summary "ESP32 BPM Detector firmware binary" \
                    --description "Firmware binary for ESP32 BPM detector project"
            fi
        done
        
        echo "✅ Firmware uploaded"
    else
        echo "⚠️  No firmware build directory found. Run 'pio run' first."
    fi
fi

# Upload tools
if [[ "$ARTIFACT_TYPE" == "all" || "$ARTIFACT_TYPE" == "tools" ]]; then
    echo ""
    echo "🔧 Uploading Development Tools..."
    
    mkdir -p /tmp/tools-artifacts
    
    # FlatBuffers compiler
    if command -v flatc &> /dev/null; then
        FLATC_PATH=$(which flatc)
        echo "  Uploading flatc from $FLATC_PATH..."
        cloudsmith upload raw "$CLOUDSMITH_ORG/$CLOUDSMITH_REPO" "$FLATC_PATH" \
            --name "flatc" \
            --version "24.3.25" \
            --summary "FlatBuffers compiler (flatc)" \
            --description "Standalone FlatBuffers compiler executable"
    else
        echo "⚠️  flatc not found in PATH"
    fi
    
    # Conan standalone
    if command -v conan &> /dev/null; then
        CONAN_VERSION=$(conan --version | awk '{print $2}')
        echo "  Packaging Conan $CONAN_VERSION..."
        
        # Create standalone package
        mkdir -p /tmp/tools-artifacts/conan-standalone
        python3 -m pip install --target /tmp/tools-artifacts/conan-standalone "conan==$CONAN_VERSION"
        
        # Create wrapper
        cat > /tmp/tools-artifacts/conan-standalone/conan-wrapper.sh <<'EOF'
#!/bin/bash
export PYTHONPATH="$(dirname $0):$PYTHONPATH"
python3 -m conans.conan "$@"
EOF
        chmod +x /tmp/tools-artifacts/conan-standalone/conan-wrapper.sh
        
        # Archive
        tar -czf /tmp/tools-artifacts/conan-${CONAN_VERSION}-standalone.tar.gz -C /tmp/tools-artifacts/conan-standalone .
        
        # Upload
        cloudsmith upload raw "$CLOUDSMITH_ORG/$CLOUDSMITH_REPO" "/tmp/tools-artifacts/conan-${CONAN_VERSION}-standalone.tar.gz" \
            --name "conan-standalone" \
            --version "$CONAN_VERSION" \
            --summary "Conan package manager (standalone)" \
            --description "Standalone Conan package manager distribution"
        
        echo "✅ Tools uploaded"
    else
        echo "⚠️  conan not found in PATH"
    fi
fi

# Upload MCP servers
if [[ "$ARTIFACT_TYPE" == "all" || "$ARTIFACT_TYPE" == "mcp-servers" ]]; then
    echo ""
    echo "🚀 Uploading MCP Servers..."
    
    mkdir -p /tmp/mcp-servers-artifacts
    
    # MCP Prompts Server
    MCP_PROMPTS_DIR="$REPO_ROOT/../ai-mcp-monorepo/packages/mcp-prompts"
    if [ -d "$MCP_PROMPTS_DIR/dist" ]; then
        echo "  Packaging MCP Prompts Server..."
        cd "$MCP_PROMPTS_DIR"
        
        mkdir -p /tmp/mcp-servers-artifacts/mcp-prompts-standalone
        cp -r dist/* /tmp/mcp-servers-artifacts/mcp-prompts-standalone/
        cp package.json /tmp/mcp-servers-artifacts/mcp-prompts-standalone/
        
        # Create launcher
        cat > /tmp/mcp-servers-artifacts/mcp-prompts-standalone/mcp-prompts-server.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
node dist/mcp-server-standalone.js "$@"
EOF
        chmod +x /tmp/mcp-servers-artifacts/mcp-prompts-standalone/mcp-prompts-server.sh
        
        tar -czf /tmp/mcp-servers-artifacts/mcp-prompts-server-standalone.tar.gz -C /tmp/mcp-servers-artifacts/mcp-prompts-standalone .
        
        cloudsmith upload raw "$CLOUDSMITH_ORG/$CLOUDSMITH_REPO" /tmp/mcp-servers-artifacts/mcp-prompts-server-standalone.tar.gz \
            --name "mcp-prompts-server" \
            --version "$VERSION" \
            --summary "MCP Prompts Server (standalone)" \
            --description "Standalone MCP Prompts server executable"
    fi
    
    # Python MCP Servers
    MCP_SERVERS_DIR="$REPO_ROOT/packages/mcp/sparetools-mcp-servers/src/sparetools/mcp_servers"
    if [ -d "$MCP_SERVERS_DIR" ]; then
        for server_dir in "$MCP_SERVERS_DIR"/*; do
            if [ -d "$server_dir" ]; then
                server_name=$(basename "$server_dir")
                echo "  Packaging $server_name..."
                cd "$server_dir"
                tar -czf "/tmp/mcp-servers-artifacts/${server_name}-mcp-server.tar.gz" .
                
                cloudsmith upload raw "$CLOUDSMITH_ORG/$CLOUDSMITH_REPO" "/tmp/mcp-servers-artifacts/${server_name}-mcp-server.tar.gz" \
                    --name "$server_name-mcp-server" \
                    --version "$VERSION" \
                    --summary "MCP Server: $server_name" \
                    --description "MCP server executable package"
            fi
        done
    fi
    
    echo "✅ MCP Servers uploaded"
fi

# Upload dependencies
if [[ "$ARTIFACT_TYPE" == "all" || "$ARTIFACT_TYPE" == "dependencies" ]]; then
    echo ""
    echo "📚 Uploading Built Dependencies..."
    
    if ! command -v conan &> /dev/null; then
        echo "⚠️  conan not found. Skipping dependency upload."
    else
        # Configure remote
        conan remote add "$CLOUDSMITH_ORG" \
            "https://dl.cloudsmith.io/public/$CLOUDSMITH_ORG/$CLOUDSMITH_REPO/conan/" \
            --force || true
        
        # Authenticate
        conan remote login "$CLOUDSMITH_ORG" spare-sparrow --password "$CLOUDSMITH_API_KEY"
        
        # Upload key dependencies
        echo "  Uploading sparetools-flatbuffers..."
        conan upload "sparetools-flatbuffers/24.3.26" -r "$CLOUDSMITH_ORG" --confirm --retry 3 || echo "  ⚠️  Package may already exist"
        
        echo "  Uploading sparetools-cpython..."
        conan upload "sparetools-cpython/3.12.8" -r "$CLOUDSMITH_ORG" --confirm --retry 3 || echo "  ⚠️  Package may already exist"
        
        echo "✅ Dependencies uploaded"
    fi
fi

echo ""
echo "🎉 Artifact upload complete!"
echo ""
echo "🌐 View artifacts at: https://cloudsmith.io/~$CLOUDSMITH_ORG/repos/$CLOUDSMITH_REPO/packages/"