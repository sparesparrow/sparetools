#!/bin/bash
# Enable Service Discovery for Hotspot
# Ensures devices can see each other and services like KDE Connect work

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Enabling Service Discovery${NC}"
echo "============================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${YELLOW}Configuring mDNS reflection...${NC}"

# Install avahi-daemon if not present
if ! command -v avahi-daemon &> /dev/null; then
    echo -e "${YELLOW}Installing avahi-daemon...${NC}"
    apt-get update && apt-get install -y avahi-daemon
fi

# Configure avahi-daemon for mDNS reflection
cat > /etc/avahi/avahi-daemon.conf << EOF
[server]
host-name=studijko-hotspot
domain-name=local
browse-domains=local
use-ipv4=yes
use-ipv6=no
allow-interfaces=wlan0,eth0
deny-interfaces=lo
enable-dbus=yes
disallow-other-stacks=no
allow-point-to-point=no
cache-entries-max=4096
clients-max=4096
objects-per-client-max=1024
entries-per-entry-group-max=32
ratelimit-interval-usec=1000000
ratelimit-burst=1000

[wide-area]
enable-wide-area=yes

[publish]
disable-publishing=no
disable-user-service-publishing=no
add-service-cookie=yes
publish-addresses=yes
publish-hinfo=yes
publish-workstation=yes
publish-domain=yes
publish-dns-servers=192.168.200.1
publish-resolv-conf-dns-servers=yes
publish-aaaa-on-ipv4=yes
publish-a-on-ipv6=no

[reflector]
enable-reflector=yes
reflect-ipv=no

[rlimits]
rlimit-as=0
rlimit-fsize=0
rlimit-data=0
rlimit-stack=0
rlimit-core=0
rlimit-nofile=768
rlimit-rtprio=0
EOF

echo -e "${GREEN}✅ avahi-daemon configured${NC}"

# Start avahi-daemon
systemctl enable avahi-daemon
systemctl start avahi-daemon

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ avahi-daemon started${NC}"
else
    echo -e "${RED}❌ Failed to start avahi-daemon${NC}"
fi

echo ""
echo -e "${YELLOW}Configuring iptables for service discovery...${NC}"

# Add iptables rules for mDNS and service discovery
iptables -I INPUT -p udp --dport 5353 -j ACCEPT
iptables -I INPUT -p udp --sport 5353 -j ACCEPT
iptables -I INPUT -p tcp --dport 5353 -j ACCEPT
iptables -I INPUT -p tcp --sport 5353 -j ACCEPT

# Allow UPnP/SSDP traffic
iptables -I INPUT -p udp --dport 1900 -j ACCEPT
iptables -I INPUT -p udp --sport 1900 -j ACCEPT

# Allow common service discovery ports
iptables -I INPUT -p tcp --dport 8080 -j ACCEPT  # Common web services
iptables -I INPUT -p tcp --dport 8081 -j ACCEPT  # Alternative web services
iptables -I INPUT -p tcp --dport 9090 -j ACCEPT  # KDE Connect
iptables -I INPUT -p tcp --dport 1714:1764 -j ACCEPT  # KDE Connect range

echo -e "${GREEN}✅ iptables rules added${NC}"

echo ""
echo -e "${YELLOW}Testing service discovery...${NC}"

# Test mDNS
if avahi-browse -a -t | head -5; then
    echo -e "${GREEN}✅ mDNS service discovery working${NC}"
else
    echo -e "${YELLOW}⚠️  mDNS service discovery may need time to start${NC}"
fi

echo ""
echo -e "${GREEN}Service Discovery Configuration Complete!${NC}"
echo ""
echo "Services enabled:"
echo "• mDNS/Bonjour service discovery"
echo "• UPnP/SSDP device discovery"
echo "• KDE Connect support"
echo "• General service discovery"
echo ""
echo "Devices on the hotspot can now:"
echo "• See each other in network discovery"
echo "• Use KDE Connect and similar services"
echo "• Discover shared printers and services"
echo "• Access local network services"
echo ""
echo "To test:"
echo "• Connect a device to the hotspot"
echo "• Check if it can see other devices"
echo "• Try KDE Connect or similar apps"