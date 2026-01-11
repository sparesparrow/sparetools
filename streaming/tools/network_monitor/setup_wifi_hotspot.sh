#!/bin/bash
# WiFi Hotspot Setup Script
# Creates a WiFi hotspot on wlan0 with internet sharing from eth0

# Configuration
HOTSPOT_SSID="STUDIJKO"
HOTSPOT_PASSWORD="pppppppp"
HOTSPOT_IP="192.168.200.1"
HOTSPOT_NETWORK="192.168.200.0/24"
HOTSPOT_INTERFACE="wlan0"
INTERNET_INTERFACE="eth0"
INTERNET_NETWORK="192.168.200.0/24"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}WiFi Hotspot Setup${NC}"
echo "=================="
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    local errors=0
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
        echo "Please run: sudo $0"
        exit 1
    fi
    
    # Check if required tools are installed
    for tool in hostapd dnsmasq iptables; do
        if ! command -v $tool &> /dev/null; then
            echo -e "${RED}❌ $tool not found${NC}"
            errors=$((errors + 1))
        else
            echo -e "${GREEN}✅ $tool available${NC}"
        fi
    done
    
    # Check if wlan0 exists
    if ! ip link show wlan0 &> /dev/null; then
        echo -e "${RED}❌ wlan0 interface not found${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✅ wlan0 interface available${NC}"
    fi
    
    # Check if eth0 exists and has internet
    if ! ip link show eth0 &> /dev/null; then
        echo -e "${RED}❌ eth0 interface not found${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✅ eth0 interface available${NC}"
    fi
    
    if [ $errors -gt 0 ]; then
        echo -e "${RED}❌ $errors prerequisite(s) failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Function to stop existing services
stop_existing_services() {
    echo -e "${YELLOW}Stopping existing services...${NC}"
    
    # Stop hostapd
    systemctl stop hostapd 2>/dev/null || true
    pkill hostapd 2>/dev/null || true
    
    # Stop dnsmasq
    systemctl stop dnsmasq 2>/dev/null || true
    pkill dnsmasq 2>/dev/null || true
    
    # Stop NetworkManager on wlan0
    nmcli device set wlan0 managed no 2>/dev/null || true
    
    echo -e "${GREEN}✅ Existing services stopped${NC}"
}

# Function to configure hostapd
configure_hostapd() {
    echo -e "${YELLOW}Configuring hostapd...${NC}"
    
    cat > /etc/hostapd/hostapd.conf << EOF
# WiFi Hotspot Configuration
interface=$HOTSPOT_INTERFACE
driver=nl80211
ssid=$HOTSPOT_SSID
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$HOTSPOT_PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    
    echo -e "${GREEN}✅ hostapd configured${NC}"
}

# Function to configure dnsmasq
configure_dnsmasq() {
    echo -e "${YELLOW}Configuring dnsmasq...${NC}"
    
    cat > /etc/dnsmasq.conf << EOF
# DNS and DHCP configuration for WiFi hotspot
interface=$HOTSPOT_INTERFACE
dhcp-range=192.168.200.10,192.168.200.50,255.255.255.0,24h
dhcp-option=3,$HOTSPOT_IP
dhcp-option=6,$HOTSPOT_IP
server=8.8.8.8
server=8.8.4.4
log-queries
log-dhcp
listen-address=$HOTSPOT_IP
# Enable mDNS reflection for service discovery
enable-dbus
domain-needed
bogus-priv
expand-hosts
bind-interfaces
EOF
    
    echo -e "${GREEN}✅ dnsmasq configured${NC}"
}

# Function to configure network interfaces
configure_network() {
    echo -e "${YELLOW}Configuring network interfaces...${NC}"
    
    # Bring down wlan0
    ip link set wlan0 down
    
    # Configure wlan0 with static IP
    ip addr add $HOTSPOT_IP/24 dev wlan0
    
    # Bring up wlan0
    ip link set wlan0 up
    
    echo -e "${GREEN}✅ Network interfaces configured${NC}"
}

# Function to configure iptables rules
configure_iptables() {
    echo -e "${YELLOW}Configuring iptables rules...${NC}"
    
    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward
    
    # Flush existing rules
    iptables -F
    iptables -t nat -F
    iptables -X
    iptables -t nat -X
    
    # Set default policies
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT
    
    # Allow forwarding between interfaces
    iptables -A FORWARD -i $HOTSPOT_INTERFACE -o $INTERNET_INTERFACE -j ACCEPT
    iptables -A FORWARD -i $INTERNET_INTERFACE -o $HOTSPOT_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
    
    # NAT for internet sharing
    iptables -t nat -A POSTROUTING -o $INTERNET_INTERFACE -j MASQUERADE
    
    # Allow access to local network
    iptables -A FORWARD -i $HOTSPOT_INTERFACE -d $INTERNET_NETWORK -j ACCEPT
    iptables -A FORWARD -i $INTERNET_INTERFACE -s $INTERNET_NETWORK -o $HOTSPOT_INTERFACE -j ACCEPT
    
    # Allow communication between hotspot clients (for KDE Connect, etc.)
    iptables -A FORWARD -i $HOTSPOT_INTERFACE -o $HOTSPOT_INTERFACE -j ACCEPT
    
    # Allow mDNS/Bonjour traffic (for service discovery)
    iptables -A INPUT -p udp --dport 5353 -j ACCEPT
    iptables -A INPUT -p udp --sport 5353 -j ACCEPT
    
    echo -e "${GREEN}✅ iptables rules configured${NC}"
}

# Function to start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    
    # Start dnsmasq
    systemctl start dnsmasq
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ dnsmasq started${NC}"
    else
        echo -e "${RED}❌ Failed to start dnsmasq${NC}"
        return 1
    fi
    
    # Start hostapd
    systemctl start hostapd
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ hostapd started${NC}"
    else
        echo -e "${RED}❌ Failed to start hostapd${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ All services started${NC}"
}

# Function to show status
show_status() {
    echo ""
    echo -e "${BLUE}WiFi Hotspot Status${NC}"
    echo "==================="
    echo "SSID: $HOTSPOT_SSID"
    echo "Password: $HOTSPOT_PASSWORD"
    echo "Hotspot IP: $HOTSPOT_IP"
    echo "Network: $HOTSPOT_NETWORK"
    echo "Interface: $HOTSPOT_INTERFACE"
    echo "Internet Interface: $INTERNET_INTERFACE"
    echo ""
    
    # Show connected devices
    echo -e "${YELLOW}Connected devices:${NC}"
    dnsmasq --test 2>/dev/null && echo "DHCP server running" || echo "DHCP server not running"
    
    # Show iptables rules
    echo ""
    echo -e "${YELLOW}Firewall rules:${NC}"
    iptables -L -n | grep -E "(FORWARD|POSTROUTING)" | head -5
    
    echo ""
    echo -e "${GREEN}Hotspot is running!${NC}"
    echo "Devices can now connect to: $HOTSPOT_SSID"
    echo "Password: $HOTSPOT_PASSWORD"
}

# Function to stop hotspot
stop_hotspot() {
    echo -e "${YELLOW}Stopping WiFi hotspot...${NC}"
    
    # Stop services
    systemctl stop hostapd
    systemctl stop dnsmasq
    
    # Reset network configuration
    ip link set wlan0 down
    ip addr del $HOTSPOT_IP/24 dev wlan0 2>/dev/null || true
    
    # Reset iptables
    iptables -F
    iptables -t nat -F
    iptables -X
    iptables -t nat -X
    
    # Disable IP forwarding
    echo 0 > /proc/sys/net/ipv4/ip_forward
    
    echo -e "${GREEN}✅ WiFi hotspot stopped${NC}"
}

# Function to show help
show_help() {
    echo "WiFi Hotspot Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -s, --ssid        Set hotspot SSID (default: $HOTSPOT_SSID)"
    echo "  -p, --password    Set hotspot password (default: $HOTSPOT_PASSWORD)"
    echo "  -i, --ip          Set hotspot IP (default: $HOTSPOT_IP)"
    echo "  -w, --wifi        Set WiFi interface (default: $HOTSPOT_INTERFACE)"
    echo "  -e, --ethernet    Set ethernet interface (default: $INTERNET_INTERFACE)"
    echo "  --stop            Stop the hotspot"
    echo "  --status          Show hotspot status"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start with default settings"
    echo "  $0 -s MyHotspot -p mypassword123     # Custom SSID and password"
    echo "  $0 --stop                             # Stop the hotspot"
    echo "  $0 --status                           # Show status"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--ssid)
            HOTSPOT_SSID="$2"
            shift 2
            ;;
        -p|--password)
            HOTSPOT_PASSWORD="$2"
            shift 2
            ;;
        -i|--ip)
            HOTSPOT_IP="$2"
            shift 2
            ;;
        -w|--wifi)
            HOTSPOT_INTERFACE="$2"
            shift 2
            ;;
        -e|--ethernet)
            INTERNET_INTERFACE="$2"
            shift 2
            ;;
        --stop)
            stop_hotspot
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
echo "Starting WiFi hotspot setup..."

# Check prerequisites
check_prerequisites

# Stop existing services
stop_existing_services

# Configure services
configure_hostapd
configure_dnsmasq
configure_network
configure_iptables

# Start services
if start_services; then
    show_status
    echo ""
    echo -e "${GREEN}WiFi hotspot setup complete!${NC}"
    echo ""
    echo "To stop the hotspot: sudo $0 --stop"
    echo "To check status: sudo $0 --status"
else
    echo -e "${RED}Failed to start WiFi hotspot${NC}"
    exit 1
fi