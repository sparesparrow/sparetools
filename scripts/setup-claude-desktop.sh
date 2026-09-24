#!/bin/bash
#
# SpareTools Claude Desktop Integration Setup
# Installs MCP server configurations for Claude Desktop
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_CONFIG="$PROJECT_ROOT/packages/mcp/sparetools-mcp-ecosystem/claude_desktop_config.json"

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect Claude Desktop config path by OS
detect_config_path() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "$HOME/.config/Claude/claude_desktop_config.json"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "$APPDATA/Claude/claude_desktop_config.json"
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Merge new servers into existing config without overwriting user's custom entries
merge_configs() {
    local dest="$1"
    local src="$2"

    if command -v python3 &>/dev/null; then
        python3 - <<PYEOF
import json, sys

with open("$src") as f:
    new_cfg = json.load(f)

dest_path = "$dest"
try:
    with open(dest_path) as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = {"mcpServers": {}}

existing.setdefault("mcpServers", {})
new_servers = new_cfg.get("mcpServers", {})
added = []
for name, cfg in new_servers.items():
    if name not in existing["mcpServers"]:
        existing["mcpServers"][name] = cfg
        added.append(name)

with open(dest_path, "w") as f:
    json.dump(existing, f, indent=2)

if added:
    print(f"Added servers: {', '.join(added)}")
else:
    print("All SpareTools servers already present — no changes needed")
PYEOF
    else
        cp "$src" "$dest"
        log_warning "python3 not found — overwrote existing config with SpareTools defaults"
    fi
}

main() {
    echo ""
    echo "========================================="
    echo "  SpareTools Claude Desktop Setup"
    echo "========================================="
    echo ""

    DEST_CONFIG="$(detect_config_path)"
    DEST_DIR="$(dirname "$DEST_CONFIG")"

    log_info "Config target: $DEST_CONFIG"

    # Ensure destination directory exists
    mkdir -p "$DEST_DIR"

    # Back up existing config
    if [ -f "$DEST_CONFIG" ]; then
        BACKUP="$DEST_CONFIG.bak.$(date +%Y%m%d%H%M%S)"
        cp "$DEST_CONFIG" "$BACKUP"
        log_info "Backed up existing config to: $BACKUP"
    fi

    # Merge SpareTools servers into config
    merge_configs "$DEST_CONFIG" "$SOURCE_CONFIG"
    log_success "Claude Desktop config updated: $DEST_CONFIG"

    echo ""
    echo "----------------------------------------"
    echo "SpareTools MCP servers registered:"
    echo "  - sparetools-static-analysis"
    echo "  - sparetools-esp32"
    echo "  - sparetools-android"
    echo "  - sparetools-conan"
    echo "  - sparetools-repo"
    echo "  - sparetools-orchestrator"
    echo ""
    echo "Required environment variables:"
    echo "  CLOUDSMITH_API_KEY   — Cloudsmith package registry"
    echo "  GITHUB_TOKEN         — GitHub API access"
    echo "  ANTHROPIC_API_KEY    — Claude AI (orchestrator server)"
    echo ""
    echo "Restart Claude Desktop to activate the MCP servers."
    echo "========================================="
    echo ""
}

main "$@"
