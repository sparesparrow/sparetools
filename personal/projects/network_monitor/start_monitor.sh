#!/bin/bash

# Enhanced Network Monitor - Quick Start Script
# "We can't stop here. This is bat country!" - Hunter S. Thompson

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/enhanced_network_monitor.sh"

# Check if monitor script exists
if [[ ! -f "$MONITOR_SCRIPT" ]]; then
    echo "Error: Enhanced network monitor script not found at $MONITOR_SCRIPT"
    exit 1
fi

# Check permissions
if [[ ! -x "$MONITOR_SCRIPT" ]]; then
    echo "Making monitor script executable..."
    chmod +x "$MONITOR_SCRIPT"
fi

# Check for required tools
echo "Checking for required tools..."
missing_tools=()

for tool in tcpdump tshark nft nmap; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        missing_tools+=("$tool")
    fi
done

if [[ ${#missing_tools[@]} -gt 0 ]]; then
    echo "Warning: Missing tools: ${missing_tools[*]}"
    echo "Install with: sudo apt install ${missing_tools[*]}"
fi

# Optional tools
echo "Checking for optional tools..."
optional_missing=()

for tool in spd-say docker rtl_433; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        optional_missing+=("$tool")
    fi
done

if [[ ${#optional_missing[@]} -gt 0 ]]; then
    echo "Optional tools not found: ${optional_missing[*]}"
    echo "Enhanced features will be disabled."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                 ENHANCED NETWORK MONITOR - GONZO EDITION                   ║"
echo "║                \"The wires never stop talking...\"                           ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting surveillance... Press Ctrl+C to exit"
echo ""

# Start the monitor
exec "$MONITOR_SCRIPT"