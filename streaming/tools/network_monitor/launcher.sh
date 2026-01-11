#!/bin/bash
# Network Monitor Launcher
# Main entry point for all network monitoring and hotspot functionality

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to show banner
show_banner() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                Network Monitor & Hotspot                    ║${NC}"
    echo -e "${BLUE}║              Complete Network Management Suite              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show main menu
show_menu() {
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo "1. 🚀 Quick Start (WiFi Hotspot)"
    echo "2. 🔧 Network Manager (Full Control)"
    echo "3. 📺 Screen Casting (DLNA/RTSP)"
    echo "4. 🔍 Enable Service Discovery"
    echo "5. 🧪 Test & Diagnostics"
    echo "6. ⚙️  Service Management"
    echo "7. 📊 System Status"
    echo "8. ❓ Help & Documentation"
    echo "9. 🚪 Exit"
    echo ""
    echo -n "Enter your choice [1-9]: "
}

# Function to quick start
quick_start() {
    echo -e "${GREEN}Quick Start - WiFi Hotspot${NC}"
    echo "=========================="
    echo ""
    $SCRIPT_DIR/quick_setup.sh
}

# Function to network manager
network_manager() {
    echo -e "${GREEN}Network Manager${NC}"
    echo "==============="
    echo ""
    $SCRIPT_DIR/network_manager.sh
}

# Function to screen casting
screen_casting() {
    echo -e "${GREEN}Screen Casting Options${NC}"
    echo "======================="
    echo ""
    echo "1. Real-Time RTSP Streaming"
    echo "2. Continuous DLNA Casting"
    echo "3. Test Screen Capture"
    echo "4. Back to main menu"
    echo ""
    echo -n "Choose option [1-4]: "
    read choice
    
    case $choice in
        1)
            echo -e "${GREEN}Starting RTSP Launcher...${NC}"
            $SCRIPT_DIR/rtsp_launcher.sh
            ;;
        2)
            echo -e "${GREEN}Starting Continuous Cast Launcher...${NC}"
            $SCRIPT_DIR/launch_continuous_cast.sh
            ;;
        3)
            echo -e "${GREEN}Testing Screen Capture...${NC}"
            $SCRIPT_DIR/test_continuous_screen_cast.sh
            ;;
        4)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to enable service discovery
enable_service_discovery() {
    echo -e "${GREEN}Enable Service Discovery${NC}"
    echo "========================"
    echo ""
    echo "This will enable mDNS/Bonjour service discovery so devices"
    echo "on the hotspot can see each other and use services like KDE Connect."
    echo ""
    echo -n "Continue? [y/N]: "
    read choice
    
    if [[ $choice =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Enabling service discovery...${NC}"
        $SCRIPT_DIR/enable_service_discovery.sh
    else
        echo "Cancelled"
    fi
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to test and diagnostics
test_diagnostics() {
    echo -e "${GREEN}Test & Diagnostics${NC}"
    echo "==================="
    echo ""
    echo "1. Test Authentication"
    echo "2. Test Network Connectivity"
    echo "3. Test RTSP Services"
    echo "4. Test DLNA Services"
    echo "5. System Health Check"
    echo "6. Back to main menu"
    echo ""
    echo -n "Choose option [1-6]: "
    read choice
    
    case $choice in
        1)
            $SCRIPT_DIR/fix_authentication.sh
            ;;
        2)
            echo -e "${YELLOW}Testing network connectivity...${NC}"
            ping -c 3 8.8.8.8
            ping -c 3 google.com
            ;;
        3)
            echo -e "${YELLOW}Testing RTSP services...${NC}"
            $SCRIPT_DIR/rtsp_client_test.sh
            ;;
        4)
            echo -e "${YELLOW}Testing DLNA services...${NC}"
            python3 $SCRIPT_DIR/upnp_discovery.py
            ;;
        5)
            echo -e "${YELLOW}System health check...${NC}"
            systemctl status hostapd dnsmasq minidlna
            df -h
            free -h
            ;;
        6)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to service management
service_management() {
    echo -e "${GREEN}Service Management${NC}"
    echo "==================="
    echo ""
    echo "1. Start WiFi Hotspot Service"
    echo "2. Stop WiFi Hotspot Service"
    echo "3. Restart All Services"
    echo "4. Check Service Status"
    echo "5. Enable/Disable Services"
    echo "6. Back to main menu"
    echo ""
    echo -n "Choose option [1-6]: "
    read choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Starting WiFi hotspot service...${NC}"
            sudo systemctl start wifi-hotspot.service
            ;;
        2)
            echo -e "${YELLOW}Stopping WiFi hotspot service...${NC}"
            sudo systemctl stop wifi-hotspot.service
            ;;
        3)
            echo -e "${YELLOW}Restarting all services...${NC}"
            sudo systemctl restart hostapd dnsmasq minidlna
            ;;
        4)
            echo -e "${YELLOW}Service status:${NC}"
            systemctl status hostapd dnsmasq minidlna wifi-hotspot.service
            ;;
        5)
            echo -e "${YELLOW}Enable/Disable services:${NC}"
            echo "1. Enable WiFi hotspot service"
            echo "2. Disable WiFi hotspot service"
            echo "3. Enable hostapd"
            echo "4. Disable hostapd"
            echo -n "Choose option [1-4]: "
            read sub_choice
            case $sub_choice in
                1) sudo systemctl enable wifi-hotspot.service ;;
                2) sudo systemctl disable wifi-hotspot.service ;;
                3) sudo systemctl enable hostapd ;;
                4) sudo systemctl disable hostapd ;;
                *) echo -e "${RED}Invalid option${NC}" ;;
            esac
            ;;
        6)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to system status
system_status() {
    echo -e "${GREEN}System Status${NC}"
    echo "============="
    echo ""
    
    # Network interfaces
    echo -e "${BLUE}Network Interfaces:${NC}"
    ip addr show | grep -E "^[0-9]+:|inet " | grep -v "127.0.0.1"
    echo ""
    
    # Services status
    echo -e "${BLUE}Services Status:${NC}"
    systemctl is-active hostapd dnsmasq minidlna wifi-hotspot.service
    echo ""
    
    # Disk usage
    echo -e "${BLUE}Disk Usage:${NC}"
    df -h | head -5
    echo ""
    
    # Memory usage
    echo -e "${BLUE}Memory Usage:${NC}"
    free -h
    echo ""
    
    # Network connections
    echo -e "${BLUE}Active Connections:${NC}"
    netstat -tuln | grep -E ":80|:443|:22|:53|:8200|:8554" | head -10
    echo ""
    
    echo -n "Press Enter to continue..."
    read
}

# Function to show help
show_help() {
    echo -e "${GREEN}Network Monitor & Hotspot Help${NC}"
    echo "==============================="
    echo ""
    echo "This suite provides comprehensive network management including:"
    echo ""
    echo "🌐 WiFi Hotspot:"
    echo "• Create WiFi hotspot on wlan0"
    echo "• Internet sharing from eth0"
    echo "• Local network access (192.168.200.0/24)"
    echo "• DHCP and DNS services"
    echo ""
    echo "📺 Screen Casting:"
    echo "• Real-time RTSP streaming"
    echo "• Continuous DLNA casting"
    echo "• TV-compatible encoding"
    echo ""
    echo "🔧 Management:"
    echo "• Service control"
    echo "• Network diagnostics"
    echo "• Authentication testing"
    echo "• System monitoring"
    echo ""
    echo "Files Location: $SCRIPT_DIR"
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Main program loop
main() {
    while true; do
        show_banner
        show_menu
        read choice
        
        case $choice in
            1)
                quick_start
                ;;
            2)
                network_manager
                ;;
            3)
                screen_casting
                ;;
            4)
                enable_service_discovery
                ;;
            5)
                test_diagnostics
                ;;
            6)
                service_management
                ;;
            7)
                system_status
                ;;
            8)
                show_help
                ;;
            9)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please choose 1-9.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Run main program
main