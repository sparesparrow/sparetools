#!/bin/bash
# KDE Connect Helper Script
# Helps troubleshoot and configure KDE Connect discovery

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}KDE Connect Helper${NC}"
echo "=================="
echo ""

# Function to check KDE Connect status
check_kdeconnect() {
    echo -e "${YELLOW}Checking KDE Connect status...${NC}"
    
    # Check if KDE Connect is installed
    if command -v kdeconnect-cli &> /dev/null; then
        echo -e "${GREEN}✅ KDE Connect CLI available${NC}"
        
        # List devices
        echo -e "${YELLOW}Available devices:${NC}"
        kdeconnect-cli --list-devices
        echo ""
        
        # Check if daemon is running
        if pgrep -f kdeconnectd > /dev/null; then
            echo -e "${GREEN}✅ KDE Connect daemon is running${NC}"
        else
            echo -e "${RED}❌ KDE Connect daemon is not running${NC}"
            echo "Starting KDE Connect daemon..."
            kdeconnectd &
            sleep 2
        fi
    else
        echo -e "${RED}❌ KDE Connect not installed${NC}"
        echo "Install with: sudo apt install kdeconnect"
        return 1
    fi
}

# Function to check network connectivity
check_network() {
    echo -e "${YELLOW}Checking network connectivity...${NC}"
    
    # Check if we're on the right network
    local current_ip=$(ip route get 8.8.8.8 | grep -oP 'src \K\S+')
    echo "Current IP: $current_ip"
    
    if [[ $current_ip == 192.168.200.* ]]; then
        echo -e "${GREEN}✅ On correct network (192.168.200.x)${NC}"
    else
        echo -e "${YELLOW}⚠️  Not on expected network${NC}"
    fi
    
    # Check mDNS
    echo -e "${YELLOW}Checking mDNS services...${NC}"
    if command -v avahi-browse &> /dev/null; then
        echo "mDNS services:"
        avahi-browse -a -t | head -5
    else
        echo -e "${RED}❌ avahi-browse not available${NC}"
    fi
}

# Function to check firewall
check_firewall() {
    echo -e "${YELLOW}Checking firewall rules...${NC}"
    
    # Check KDE Connect ports
    local ports=(1714 1715 1716 1717 1718 1719 1720 1721 1722 1723 1724 9090 5353)
    
    for port in "${ports[@]}"; do
        if sudo iptables -L -n | grep -q "dpt:$port"; then
            echo -e "${GREEN}✅ Port $port is open${NC}"
        else
            echo -e "${RED}❌ Port $port is not open${NC}"
        fi
    done
}

# Function to restart services
restart_services() {
    echo -e "${YELLOW}Restarting services...${NC}"
    
    # Restart avahi
    sudo systemctl restart avahi-daemon
    echo -e "${GREEN}✅ avahi-daemon restarted${NC}"
    
    # Restart KDE Connect
    pkill -f kdeconnectd
    sleep 1
    kdeconnectd &
    echo -e "${GREEN}✅ KDE Connect daemon restarted${NC}"
    
    sleep 3
}

# Function to show troubleshooting tips
show_tips() {
    echo -e "${YELLOW}Troubleshooting Tips:${NC}"
    echo ""
    echo "1. Make sure both devices are on the same network (192.168.200.x)"
    echo "2. Check that KDE Connect is installed on both devices"
    echo "3. Ensure both devices have KDE Connect running"
    echo "4. Try restarting KDE Connect on both devices"
    echo "5. Check firewall settings on both devices"
    echo "6. Make sure mDNS/Bonjour is working"
    echo ""
    echo "On the client device:"
    echo "• Install KDE Connect: sudo apt install kdeconnect"
    echo "• Start KDE Connect daemon: kdeconnectd &"
    echo "• Open KDE Connect app and refresh"
    echo ""
    echo "On this server:"
    echo "• Check status: kdeconnect-cli --list-devices"
    echo "• Restart daemon: pkill kdeconnectd && kdeconnectd &"
}

# Function to test connectivity
test_connectivity() {
    echo -e "${YELLOW}Testing connectivity...${NC}"
    
    # Get connected devices
    local devices=$(ip neigh show | grep "192.168.200" | awk '{print $1}')
    
    if [ -z "$devices" ]; then
        echo -e "${RED}❌ No devices found on network${NC}"
        return 1
    fi
    
    echo "Found devices:"
    for device in $devices; do
        echo "• $device"
        
        # Try to ping
        if ping -c 1 -W 1 $device > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Reachable${NC}"
        else
            echo -e "  ${RED}❌ Not reachable${NC}"
        fi
    done
}

# Main menu
show_menu() {
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo "1. Check KDE Connect status"
    echo "2. Check network connectivity"
    echo "3. Check firewall rules"
    echo "4. Restart services"
    echo "5. Test device connectivity"
    echo "6. Show troubleshooting tips"
    echo "7. Exit"
    echo ""
    echo -n "Enter your choice [1-7]: "
}

# Main program
main() {
    while true; do
        show_menu
        read choice
        
        case $choice in
            1)
                check_kdeconnect
                ;;
            2)
                check_network
                ;;
            3)
                check_firewall
                ;;
            4)
                restart_services
                ;;
            5)
                test_connectivity
                ;;
            6)
                show_tips
                ;;
            7)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please choose 1-7.${NC}"
                ;;
        esac
        
        echo ""
        echo -n "Press Enter to continue..."
        read
        clear
        echo -e "${BLUE}KDE Connect Helper${NC}"
        echo "=================="
        echo ""
    done
}

# Run main program
main