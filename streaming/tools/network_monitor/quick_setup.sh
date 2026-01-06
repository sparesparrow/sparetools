#!/bin/bash
# Quick Setup Script
# Handles authentication and starts WiFi hotspot

echo "Quick Setup - WiFi Hotspot"
echo "========================="
echo ""

# Function to check if we can run with sudo
check_sudo() {
    if sudo -n true 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to start hotspot with authentication
start_hotspot_with_auth() {
    echo "Starting WiFi hotspot setup..."
    echo ""
    
    # Try different authentication methods
    if check_sudo; then
        echo "✅ Using cached sudo credentials"
        sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh
    else
        echo "🔐 Authentication required"
        echo "Please enter your password when prompted:"
        echo ""
        
        # Try sudo with password prompt
        if sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh; then
            echo "✅ Hotspot started successfully"
        else
            echo "❌ Failed to start hotspot"
            echo ""
            echo "Alternative methods:"
            echo "1. Run: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh"
            echo "2. Run: pkexec /home/sparrow/network_monitor/setup_wifi_hotspot.sh"
            echo "3. Run: /home/sparrow/network_monitor/fix_authentication.sh"
            return 1
        fi
    fi
}

# Function to show current status
show_status() {
    echo ""
    echo "Current Network Status:"
    echo "======================"
    
    # Show interfaces
    echo "Network Interfaces:"
    ip addr show | grep -E "^[0-9]+:|inet " | grep -v "127.0.0.1"
    echo ""
    
    # Show routing
    echo "Routing Table:"
    ip route show | head -5
    echo ""
    
    # Show services
    echo "Services:"
    if systemctl is-active --quiet hostapd; then
        echo "  ✅ hostapd running"
    else
        echo "  ❌ hostapd not running"
    fi
    
    if systemctl is-active --quiet dnsmasq; then
        echo "  ✅ dnsmasq running"
    else
        echo "  ❌ dnsmasq not running"
    fi
    echo ""
}

# Function to show help
show_help() {
    echo "Quick Setup Help"
    echo "================"
    echo ""
    echo "This script will:"
    echo "1. Check authentication status"
    echo "2. Start WiFi hotspot if possible"
    echo "3. Show network status"
    echo ""
    echo "WiFi Hotspot Details:"
    echo "• SSID: STUDIJKO"
    echo "• Password: pppppppp"
    echo "• IP Range: 192.168.200.0/24"
    echo "• Internet sharing from eth0 to wlan0"
    echo ""
    echo "If authentication fails:"
    echo "• Run: ./fix_authentication.sh"
    echo "• Run: sudo ./setup_wifi_hotspot.sh"
    echo "• Run: pkexec ./setup_wifi_hotspot.sh"
    echo ""
}

# Main execution
echo "Checking system status..."

# Show current status
show_status

# Check if hotspot is already running
if systemctl is-active --quiet hostapd && systemctl is-active --quiet dnsmasq; then
    echo "✅ WiFi hotspot is already running!"
    echo ""
    echo "Hotspot Details:"
    echo "• SSID: STUDIJKO"
    echo "• Password: pppppppp"
    echo "• IP Range: 192.168.200.0/24"
    echo ""
    echo "To stop: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh --stop"
    echo "To restart: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh"
    exit 0
fi

# Try to start hotspot
echo "Attempting to start WiFi hotspot..."
echo ""

if start_hotspot_with_auth; then
    echo ""
    echo "🎉 WiFi hotspot started successfully!"
    echo ""
    echo "Hotspot Details:"
    echo "• SSID: STUDIJKO"
    echo "• Password: pppppppp"
    echo "• IP Range: 192.168.200.0/24"
    echo "• Internet sharing: eth0 → wlan0"
    echo ""
    echo "Connected devices can now:"
    echo "• Access the internet"
    echo "• Access local network (192.168.200.0/24)"
    echo "• Connect to other devices on the hotspot"
    echo ""
    echo "To manage the hotspot:"
    echo "• Status: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh --status"
    echo "• Stop: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh --stop"
    echo "• Restart: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh"
    echo "• Full management: /home/sparrow/network_monitor/network_manager.sh"
else
    echo ""
    echo "❌ Failed to start WiFi hotspot"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check authentication: /home/sparrow/network_monitor/fix_authentication.sh"
    echo "2. Try manual start: sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh"
    echo "3. Check prerequisites: hostapd, dnsmasq, iptables"
    echo "4. Check interfaces: ip addr show"
    echo ""
    echo "For help: /home/sparrow/network_monitor/network_manager.sh"
fi