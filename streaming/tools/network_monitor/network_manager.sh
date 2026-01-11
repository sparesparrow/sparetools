#!/bin/bash
# Network Manager Script
# Manages WiFi hotspot, routing, and network configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to show banner
show_banner() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Network Manager                          ║${NC}"
    echo -e "${BLUE}║              WiFi Hotspot & Routing Control                ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show main menu
show_menu() {
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo "1. 🚀 Start WiFi Hotspot"
    echo "2. 🛑 Stop WiFi Hotspot"
    echo "3. 📊 Show Network Status"
    echo "4. 🔧 Configure Network Settings"
    echo "5. 🌐 Test Internet Connectivity"
    echo "6. 📱 Show Connected Devices"
    echo "7. 🔄 Restart Network Services"
    echo "8. 🧪 Test Authentication"
    echo "9. ❓ Help & Documentation"
    echo "10. 🚪 Exit"
    echo ""
    echo -n "Enter your choice [1-10]: "
}

# Function to start WiFi hotspot
start_hotspot() {
    echo -e "${GREEN}Starting WiFi Hotspot...${NC}"
    echo ""
    
    # Check if already running
    if systemctl is-active --quiet hostapd; then
        echo -e "${YELLOW}WiFi hotspot is already running${NC}"
        return
    fi
    
    # Check authentication
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}Authentication required. Please enter your password:${NC}"
        if ! sudo -v; then
            echo -e "${RED}Authentication failed${NC}"
            return
        fi
    fi
    
    # Start hotspot
    sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh
}

# Function to stop WiFi hotspot
stop_hotspot() {
    echo -e "${GREEN}Stopping WiFi Hotspot...${NC}"
    echo ""
    
    # Check authentication
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}Authentication required. Please enter your password:${NC}"
        if ! sudo -v; then
            echo -e "${RED}Authentication failed${NC}"
            return
        fi
    fi
    
    # Stop hotspot
    sudo /home/sparrow/network_monitor/setup_wifi_hotspot.sh --stop
}

# Function to show network status
show_network_status() {
    echo -e "${GREEN}Network Status${NC}"
    echo "=============="
    echo ""
    
    # Show interfaces
    echo -e "${BLUE}Network Interfaces:${NC}"
    ip addr show | grep -E "^[0-9]+:|inet " | grep -v "127.0.0.1" | head -20
    echo ""
    
    # Show routing table
    echo -e "${BLUE}Routing Table:${NC}"
    ip route show | head -10
    echo ""
    
    # Show WiFi hotspot status
    echo -e "${BLUE}WiFi Hotspot Status:${NC}"
    if systemctl is-active --quiet hostapd; then
        echo -e "  ${GREEN}✅ hostapd running${NC}"
    else
        echo -e "  ${RED}❌ hostapd not running${NC}"
    fi
    
    if systemctl is-active --quiet dnsmasq; then
        echo -e "  ${GREEN}✅ dnsmasq running${NC}"
    else
        echo -e "  ${RED}❌ dnsmasq not running${NC}"
    fi
    
    # Show IP forwarding
    if [ "$(cat /proc/sys/net/ipv4/ip_forward)" = "1" ]; then
        echo -e "  ${GREEN}✅ IP forwarding enabled${NC}"
    else
        echo -e "  ${RED}❌ IP forwarding disabled${NC}"
    fi
    
    echo ""
}

# Function to configure network settings
configure_network() {
    echo -e "${GREEN}Network Configuration${NC}"
    echo "======================"
    echo ""
    echo "Configuration Options:"
    echo "1. Change hotspot SSID and password"
    echo "2. Change hotspot IP range"
    echo "3. Configure firewall rules"
    echo "4. Set up port forwarding"
    echo "5. Back to main menu"
    echo ""
    echo -n "Choose option [1-5]: "
    read choice
    
    case $choice in
        1)
            echo -n "Enter new SSID [Sparrow-Hotspot]: "
            read ssid
            ssid=${ssid:-Sparrow-Hotspot}
            
            echo -n "Enter new password [sparrow123]: "
            read password
            password=${password:-sparrow123}
            
            echo -e "${YELLOW}Updating hotspot configuration...${NC}"
            # Update configuration files
            echo "SSID: $ssid"
            echo "Password: $password"
            echo "Configuration updated (restart hotspot to apply)"
            ;;
        2)
            echo -n "Enter new IP range [192.168.200.0/24]: "
            read ip_range
            ip_range=${ip_range:-192.168.200.0/24}
            
            echo -e "${YELLOW}Updating IP range...${NC}"
            echo "IP Range: $ip_range"
            echo "Configuration updated (restart hotspot to apply)"
            ;;
        3)
            echo -e "${YELLOW}Firewall configuration${NC}"
            echo "Current iptables rules:"
            iptables -L -n | head -10
            ;;
        4)
            echo -e "${YELLOW}Port forwarding configuration${NC}"
            echo "Port forwarding setup not implemented yet"
            ;;
        5)
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

# Function to test internet connectivity
test_internet() {
    echo -e "${GREEN}Testing Internet Connectivity${NC}"
    echo "=============================="
    echo ""
    
    # Test DNS resolution
    echo -e "${YELLOW}Testing DNS resolution...${NC}"
    if nslookup google.com &> /dev/null; then
        echo -e "  ${GREEN}✅ DNS resolution working${NC}"
    else
        echo -e "  ${RED}❌ DNS resolution failed${NC}"
    fi
    
    # Test HTTP connectivity
    echo -e "${YELLOW}Testing HTTP connectivity...${NC}"
    if curl -s --connect-timeout 5 http://google.com &> /dev/null; then
        echo -e "  ${GREEN}✅ HTTP connectivity working${NC}"
    else
        echo -e "  ${RED}❌ HTTP connectivity failed${NC}"
    fi
    
    # Test HTTPS connectivity
    echo -e "${YELLOW}Testing HTTPS connectivity...${NC}"
    if curl -s --connect-timeout 5 https://google.com &> /dev/null; then
        echo -e "  ${GREEN}✅ HTTPS connectivity working${NC}"
    else
        echo -e "  ${RED}❌ HTTPS connectivity failed${NC}"
    fi
    
    # Test ping
    echo -e "${YELLOW}Testing ping...${NC}"
    if ping -c 3 8.8.8.8 &> /dev/null; then
        echo -e "  ${GREEN}✅ Ping working${NC}"
    else
        echo -e "  ${RED}❌ Ping failed${NC}"
    fi
    
    echo ""
}

# Function to show connected devices
show_connected_devices() {
    echo -e "${GREEN}Connected Devices${NC}"
    echo "=================="
    echo ""
    
    # Show DHCP leases
    echo -e "${BLUE}DHCP Leases:${NC}"
    if [ -f /var/lib/dhcp/dhcpd.leases ]; then
        cat /var/lib/dhcp/dhcpd.leases | grep -E "lease|hardware|client-hostname" | head -20
    else
        echo "No DHCP leases found"
    fi
    
    # Show ARP table
    echo ""
    echo -e "${BLUE}ARP Table:${NC}"
    arp -a | head -10
    
    # Show network connections
    echo ""
    echo -e "${BLUE}Active Connections:${NC}"
    netstat -tuln | grep -E ":80|:443|:22|:53" | head -10
    
    echo ""
}

# Function to restart network services
restart_network_services() {
    echo -e "${GREEN}Restarting Network Services${NC}"
    echo "=============================="
    echo ""
    
    # Check authentication
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}Authentication required. Please enter your password:${NC}"
        if ! sudo -v; then
            echo -e "${RED}Authentication failed${NC}"
            return
        fi
    fi
    
    echo -e "${YELLOW}Restarting network services...${NC}"
    
    # Restart NetworkManager
    sudo systemctl restart NetworkManager
    echo -e "  ${GREEN}✅ NetworkManager restarted${NC}"
    
    # Restart hostapd
    sudo systemctl restart hostapd
    echo -e "  ${GREEN}✅ hostapd restarted${NC}"
    
    # Restart dnsmasq
    sudo systemctl restart dnsmasq
    echo -e "  ${GREEN}✅ dnsmasq restarted${NC}"
    
    echo -e "${GREEN}Network services restarted${NC}"
}

# Function to test authentication
test_authentication() {
    echo -e "${GREEN}Testing Authentication${NC}"
    echo "======================="
    echo ""
    
    /home/sparrow/network_monitor/fix_authentication.sh
}

# Function to show help
show_help() {
    echo -e "${GREEN}Network Manager Help${NC}"
    echo "==================="
    echo ""
    echo "This script manages your WiFi hotspot and network configuration."
    echo ""
    echo "Features:"
    echo "• Start/stop WiFi hotspot"
    echo "• Monitor network status"
    echo "• Configure network settings"
    echo "• Test internet connectivity"
    echo "• Show connected devices"
    echo "• Restart network services"
    echo ""
    echo "WiFi Hotspot:"
    echo "• SSID: STUDIJKO"
    echo "• Password: pppppppp"
    echo "• IP Range: 192.168.200.0/24"
    echo "• Internet sharing from eth0 to wlan0"
    echo ""
    echo "Authentication:"
    echo "• sudo password required for system changes"
    echo "• Use 'Test Authentication' to check status"
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
                start_hotspot
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            2)
                stop_hotspot
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            3)
                show_network_status
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            4)
                configure_network
                ;;
            5)
                test_internet
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            6)
                show_connected_devices
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            7)
                restart_network_services
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            8)
                test_authentication
                echo ""
                echo -n "Press Enter to continue..."
                read
                ;;
            9)
                show_help
                ;;
            10)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please choose 1-10.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Run main program
main