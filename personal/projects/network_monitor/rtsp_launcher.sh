#!/bin/bash
# RTSP Real-Time Streaming Launcher
# Easy interface for real-time RTSP streaming system

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
    echo -e "${BLUE}║                Real-Time RTSP Streaming System              ║${NC}"
    echo -e "${BLUE}║              Ultra-Low Latency Screen Casting               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show main menu
show_menu() {
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo "1. 🚀 Start RTSP Server (Real-Time Streaming)"
    echo "2. 🧪 Test RTSP Client Connectivity"
    echo "3. 🔍 Discover RTSP Services on Network"
    echo "4. 📊 Monitor RTSP Stream Performance"
    echo "5. ⚙️  Configure RTSP Settings"
    echo "6. 📺 Quick Start (Default Settings)"
    echo "7. ❓ Help & Documentation"
    echo "8. 🚪 Exit"
    echo ""
    echo -n "Enter your choice [1-8]: "
}

# Function to start RTSP server
start_rtsp_server() {
    echo -e "${GREEN}Starting RTSP Server...${NC}"
    echo ""
    echo "RTSP Server Options:"
    echo "1. Default settings (1280x720, 30fps, 3000k bitrate)"
    echo "2. High quality (1920x1080, 30fps, 5000k bitrate)"
    echo "3. Ultra high quality (1920x1080, 60fps, 8000k bitrate)"
    echo "4. Custom settings"
    echo "5. Back to main menu"
    echo ""
    echo -n "Choose option [1-5]: "
    read choice
    
    case $choice in
        1)
            echo -e "${GREEN}Starting with default settings...${NC}"
            ./rtsp_screen_stream.sh
            ;;
        2)
            echo -e "${GREEN}Starting with high quality settings...${NC}"
            ./rtsp_screen_stream.sh -r 1920x1080 -b 5000k
            ;;
        3)
            echo -e "${GREEN}Starting with ultra high quality settings...${NC}"
            ./rtsp_screen_stream.sh -r 1920x1080 -b 8000k -f 60
            ;;
        4)
            echo ""
            echo -n "Resolution [1280x720]: "
            read resolution
            resolution=${resolution:-1280x720}
            
            echo -n "Bitrate [3000k]: "
            read bitrate
            bitrate=${bitrate:-3000k}
            
            echo -n "Framerate [30]: "
            read framerate
            framerate=${framerate:-30}
            
            echo -n "Port [8554]: "
            read port
            port=${port:-8554}
            
            echo -e "${GREEN}Starting with custom settings...${NC}"
            ./rtsp_screen_stream.sh -r $resolution -b $bitrate -f $framerate -p $port
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Function to test RTSP client
test_rtsp_client() {
    echo -e "${GREEN}RTSP Client Testing${NC}"
    echo ""
    echo "Test Options:"
    echo "1. Test default RTSP URL (192.168.200.44:8554)"
    echo "2. Test custom RTSP URL"
    echo "3. Test with VLC"
    echo "4. Test with FFplay"
    echo "5. Test with GStreamer"
    echo "6. Back to main menu"
    echo ""
    echo -n "Choose option [1-6]: "
    read choice
    
    case $choice in
        1)
            echo -e "${GREEN}Testing default RTSP URL...${NC}"
            ./rtsp_client_test.sh
            ;;
        2)
            echo -n "Enter RTSP URL: "
            read rtsp_url
            if [ -n "$rtsp_url" ]; then
                echo -e "${GREEN}Testing custom RTSP URL...${NC}"
                ./rtsp_client_test.sh "$rtsp_url"
            fi
            ;;
        3)
            echo -n "Enter RTSP URL [rtsp://192.168.200.44:8554/screen]: "
            read rtsp_url
            rtsp_url=${rtsp_url:-rtsp://192.168.200.44:8554/screen}
            echo -e "${GREEN}Testing with VLC...${NC}"
            ./rtsp_client_test.sh -v "$rtsp_url"
            ;;
        4)
            echo -n "Enter RTSP URL [rtsp://192.168.200.44:8554/screen]: "
            read rtsp_url
            rtsp_url=${rtsp_url:-rtsp://192.168.200.44:8554/screen}
            echo -e "${GREEN}Testing with FFplay...${NC}"
            ./rtsp_client_test.sh -v "$rtsp_url"
            ;;
        5)
            echo -n "Enter RTSP URL [rtsp://192.168.200.44:8554/screen]: "
            read rtsp_url
            rtsp_url=${rtsp_url:-rtsp://192.168.200.44:8554/screen}
            echo -e "${GREEN}Testing with GStreamer...${NC}"
            ./rtsp_client_test.sh -v "$rtsp_url"
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

# Function to discover RTSP services
discover_rtsp_services() {
    echo -e "${GREEN}RTSP Service Discovery${NC}"
    echo ""
    echo "Discovery Options:"
    echo "1. Discover services on local network"
    echo "2. Test specific RTSP URL"
    echo "3. Back to main menu"
    echo ""
    echo -n "Choose option [1-3]: "
    read choice
    
    case $choice in
        1)
            echo -e "${GREEN}Discovering RTSP services...${NC}"
            python3 rtsp_discovery.py
            ;;
        2)
            echo -n "Enter RTSP URL: "
            read rtsp_url
            if [ -n "$rtsp_url" ]; then
                echo -e "${GREEN}Testing RTSP URL...${NC}"
                python3 rtsp_discovery.py
            fi
            ;;
        3)
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

# Function to monitor RTSP stream
monitor_rtsp_stream() {
    echo -e "${GREEN}RTSP Stream Monitoring${NC}"
    echo ""
    echo -n "Enter RTSP URL to monitor: "
    read rtsp_url
    
    if [ -z "$rtsp_url" ]; then
        echo -e "${RED}No RTSP URL provided${NC}"
        return
    fi
    
    echo -n "Monitor interval in seconds [5]: "
    read interval
    interval=${interval:-5}
    
    echo -e "${GREEN}Starting stream monitoring...${NC}"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    python3 rtsp_monitor.py "$rtsp_url" "$interval"
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to configure RTSP settings
configure_rtsp_settings() {
    echo -e "${GREEN}RTSP Configuration${NC}"
    echo ""
    echo "Configuration Options:"
    echo "1. View current settings"
    echo "2. Edit RTSP server settings"
    echo "3. Test configuration"
    echo "4. Back to main menu"
    echo ""
    echo -n "Choose option [1-4]: "
    read choice
    
    case $choice in
        1)
            echo -e "${BLUE}Current RTSP Settings:${NC}"
            echo "Default Port: 8554"
            echo "Default Resolution: 1280x720"
            echo "Default Bitrate: 3000k"
            echo "Default Framerate: 30fps"
            echo "Default GOP Size: 30"
            echo ""
            echo -n "Press Enter to continue..."
            read
            ;;
        2)
            echo -e "${YELLOW}RTSP settings are configured via command line options${NC}"
            echo "Use the 'Start RTSP Server' option with custom settings"
            echo ""
            echo -n "Press Enter to continue..."
            read
            ;;
        3)
            echo -e "${GREEN}Testing RTSP configuration...${NC}"
            ./rtsp_client_test.sh
            ;;
        4)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Function to quick start
quick_start() {
    echo -e "${GREEN}Quick Start - Real-Time RTSP Streaming${NC}"
    echo ""
    echo "This will start RTSP streaming with default settings:"
    echo "• Resolution: 1280x720"
    echo "• Bitrate: 3000k"
    echo "• Framerate: 30fps"
    echo "• Port: 8554"
    echo ""
    echo -n "Start streaming? [y/N]: "
    read choice
    
    if [[ $choice =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Starting RTSP streaming...${NC}"
        ./rtsp_screen_stream.sh
    else
        echo -e "${YELLOW}Cancelled${NC}"
    fi
}

# Function to show help
show_help() {
    echo -e "${GREEN}Real-Time RTSP Streaming Help${NC}"
    echo ""
    echo "This system provides true real-time screen streaming using RTSP"
    echo "with ultra-low latency (<2 seconds)."
    echo ""
    echo "Key Features:"
    echo "• Real-time streaming (not pseudo-real-time)"
    echo "• Ultra-low latency (<2 seconds)"
    echo "• H.264 encoding with zerolatency tuning"
    echo "• TCP transport for reliability"
    echo "• Compatible with VLC, FFplay, GStreamer"
    echo ""
    echo "Files:"
    echo "• rtsp_screen_stream.sh - Main RTSP server"
    echo "• rtsp_client_test.sh - Client testing"
    echo "• rtsp_discovery.py - Service discovery"
    echo "• rtsp_monitor.py - Stream monitoring"
    echo ""
    echo "Usage:"
    echo "1. Start RTSP server on your machine"
    echo "2. Connect from TV or other device using RTSP URL"
    echo "3. Monitor stream performance if needed"
    echo ""
    echo "RTSP URL format: rtsp://[your-ip]:8554/screen"
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    local errors=0
    
    # Check if X11 display is available
    if [ -z "$DISPLAY" ]; then
        echo -e "❌ X11 display not available"
        errors=$((errors + 1))
    else
        echo -e "✅ X11 display available: $DISPLAY"
    fi
    
    # Check if ffmpeg is installed
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "❌ ffmpeg not found"
        errors=$((errors + 1))
    else
        echo -e "✅ ffmpeg available"
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "❌ python3 not found"
        errors=$((errors + 1))
    else
        echo -e "✅ python3 available"
    fi
    
    if [ $errors -gt 0 ]; then
        echo ""
        echo -e "${RED}$errors prerequisite(s) failed. Please fix them before using RTSP streaming.${NC}"
        echo ""
        echo -n "Press Enter to continue..."
        read
        return 1
    fi
    
    echo -e "✅ All prerequisites met"
    return 0
}

# Main program loop
main() {
    while true; do
        show_banner
        show_menu
        read choice
        
        case $choice in
            1)
                if check_prerequisites; then
                    start_rtsp_server
                fi
                ;;
            2)
                test_rtsp_client
                ;;
            3)
                discover_rtsp_services
                ;;
            4)
                monitor_rtsp_stream
                ;;
            5)
                configure_rtsp_settings
                ;;
            6)
                if check_prerequisites; then
                    quick_start
                fi
                ;;
            7)
                show_help
                ;;
            8)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please choose 1-8.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Run main program
main