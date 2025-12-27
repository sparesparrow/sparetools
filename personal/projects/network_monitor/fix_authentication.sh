#!/bin/bash
# Authentication Fix Script
# Helps resolve sudo authentication issues

echo "Authentication Fix Script"
echo "========================"
echo ""

# Function to check sudo configuration
check_sudo_config() {
    echo "Checking sudo configuration..."
    
    if [ -f /etc/sudoers ]; then
        echo "✅ /etc/sudoers exists"
    else
        echo "❌ /etc/sudoers not found"
        return 1
    fi
    
    # Check if user is in sudo group
    if groups | grep -q sudo; then
        echo "✅ User is in sudo group"
    else
        echo "❌ User is not in sudo group"
        echo "Run: sudo usermod -aG sudo $USER"
        return 1
    fi
    
    # Check sudo timeout
    if sudo -v 2>/dev/null; then
        echo "✅ sudo authentication works"
        return 0
    else
        echo "❌ sudo authentication failed"
        return 1
    fi
}

# Function to show authentication options
show_auth_options() {
    echo ""
    echo "Authentication Options:"
    echo "======================"
    echo ""
    echo "1. Password Authentication (default)"
    echo "   - Enter your user password when prompted"
    echo "   - Password is required for each sudo command"
    echo ""
    echo "2. Passwordless sudo (temporary)"
    echo "   - Run: sudo visudo"
    echo "   - Add: $USER ALL=(ALL) NOPASSWD:ALL"
    echo "   - Save and exit"
    echo ""
    echo "3. Extended sudo timeout"
    echo "   - Run: sudo visudo"
    echo "   - Add: Defaults timestamp_timeout=60"
    echo "   - Save and exit"
    echo ""
    echo "4. Use pkexec instead of sudo"
    echo "   - Some commands can use pkexec instead"
    echo "   - Example: pkexec systemctl start hostapd"
    echo ""
}

# Function to test authentication methods
test_auth_methods() {
    echo "Testing authentication methods..."
    echo ""
    
    # Test sudo with password
    echo "1. Testing sudo with password:"
    if sudo -v 2>/dev/null; then
        echo "   ✅ sudo works (password cached)"
    else
        echo "   ❌ sudo requires password"
    fi
    
    # Test pkexec
    echo "2. Testing pkexec:"
    if pkexec --version 2>/dev/null; then
        echo "   ✅ pkexec available"
    else
        echo "   ❌ pkexec not available"
    fi
    
    # Test su
    echo "3. Testing su:"
    if su -c "whoami" 2>/dev/null; then
        echo "   ✅ su works"
    else
        echo "   ❌ su requires password"
    fi
    
    echo ""
}

# Function to provide solutions
provide_solutions() {
    echo "Solutions for Authentication Issues:"
    echo "==================================="
    echo ""
    echo "If sudo is not working:"
    echo "1. Make sure you know your user password"
    echo "2. Try: sudo -k (clear cached credentials)"
    echo "3. Try: sudo -v (verify password)"
    echo ""
    echo "If you forgot your password:"
    echo "1. Boot into recovery mode"
    echo "2. Mount root filesystem: mount -o remount,rw /"
    echo "3. Change password: passwd $USER"
    echo "4. Reboot: reboot"
    echo ""
    echo "For WiFi hotspot setup:"
    echo "1. Run: sudo ./setup_wifi_hotspot.sh"
    echo "2. Enter your password when prompted"
    echo "3. Or use: pkexec ./setup_wifi_hotspot.sh"
    echo ""
}

# Main execution
echo "Checking authentication status..."

if check_sudo_config; then
    echo "✅ Authentication is working correctly"
    echo ""
    echo "You can now run:"
    echo "  sudo ./setup_wifi_hotspot.sh"
    echo ""
else
    echo "❌ Authentication issues detected"
    show_auth_options
    test_auth_methods
    provide_solutions
fi

echo ""
echo "For immediate WiFi hotspot setup:"
echo "1. Run: sudo ./setup_wifi_hotspot.sh"
echo "2. Enter your password when prompted"
echo "3. The hotspot will be created with SSID: Sparrow-Hotspot"
echo "4. Password: sparrow123"
echo ""