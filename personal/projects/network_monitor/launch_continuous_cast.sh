#!/bin/bash
# Continuous Screen Cast Launcher
# Easy interface for continuous screen casting system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show banner
show_banner() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                Continuous Screen Cast System                ║${NC}"
    echo -e "${BLUE}║              Segmented Video for DLNA Streaming             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show main menu
show_menu() {
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo "1. 🚀 Start Continuous Screen Casting"
    echo "2. 📊 Monitor Segments (Real-time)"
    echo "3. 🧪 Test System"
    echo "4. ⚙️  Configure Settings"
    echo "5. 📁 View Segments"
    echo "6. 🔧 System Status"
    echo "7. ❓ Help"
    echo "8. 🚪 Exit"
    echo ""
    echo -n "Enter your choice [1-8]: "
}

# Function to start continuous casting
start_casting() {
    echo -e "${GREEN}Starting Continuous Screen Casting...${NC}"
    echo ""
    echo "Options:"
    echo "1. Default settings (30s segments, 1280x720)"
    echo "2. Custom settings"
    echo "3. Back to main menu"
    echo ""
    echo -n "Choose option [1-3]: "
    read choice
    
    case $choice in
        1)
            echo -e "${GREEN}Starting with default settings...${NC}"
            ./continuous_screen_cast.sh
            ;;
        2)
            echo ""
            echo -n "Segment duration in seconds [30]: "
            read duration
            duration=${duration:-30}
            
            echo -n "Max segments to keep [3]: "
            read segments
            segments=${segments:-3}
            
            echo -n "Resolution [1280x720]: "
            read resolution
            resolution=${resolution:-1280x720}
            
            echo -e "${GREEN}Starting with custom settings...${NC}"
            ./continuous_screen_cast.sh -d $duration -s $segments -r $resolution
            ;;
        3)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Function to monitor segments
monitor_segments() {
    echo -e "${GREEN}Starting Segment Monitor...${NC}"
    echo ""
    echo "Press Ctrl+C to return to main menu"
    echo ""
    sleep 2
    ./monitor_screen_cast.sh
}

# Function to test system
test_system() {
    echo -e "${GREEN}Running System Test...${NC}"
    echo ""
    echo "Test options:"
    echo "1. Quick test (prerequisites only)"
    echo "2. Full test (2 minutes)"
    echo "3. Custom duration test"
    echo "4. Back to main menu"
    echo ""
    echo -n "Choose option [1-4]: "
    read choice
    
    case $choice in
        1)
            ./test_continuous_screen_cast.sh -q
            ;;
        2)
            ./test_continuous_screen_cast.sh
            ;;
        3)
            echo -n "Test duration in seconds [120]: "
            read duration
            duration=${duration:-120}
            ./test_continuous_screen_cast.sh -d $duration
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

# Function to configure settings
configure_settings() {
    echo -e "${GREEN}Configuration Settings${NC}"
    echo ""
    echo "Current configuration file: continuous_screen_cast.conf"
    echo ""
    echo "Options:"
    echo "1. Edit configuration file"
    echo "2. View current settings"
    echo "3. Reset to defaults"
    echo "4. Back to main menu"
    echo ""
    echo -n "Choose option [1-4]: "
    read choice
    
    case $choice in
        1)
            if command -v nano &> /dev/null; then
                nano continuous_screen_cast.conf
            elif command -v vim &> /dev/null; then
                vim continuous_screen_cast.conf
            else
                echo -e "${YELLOW}No text editor found. Please edit continuous_screen_cast.conf manually.${NC}"
            fi
            ;;
        2)
            echo -e "${BLUE}Current Settings:${NC}"
            cat continuous_screen_cast.conf
            echo ""
            echo -n "Press Enter to continue..."
            read
            ;;
        3)
            echo -e "${YELLOW}Resetting to defaults...${NC}"
            # This would reset the config file to defaults
            echo "Configuration reset (not implemented yet)"
            ;;
        4)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Function to view segments
view_segments() {
    echo -e "${GREEN}Current Segments${NC}"
    echo ""
    
    local screen_cast_dir="/var/lib/minidlna/screen_cast"
    
    if [ ! -d "$screen_cast_dir" ]; then
        echo -e "${RED}Screen cast directory not found: $screen_cast_dir${NC}"
        return
    fi
    
    echo "Directory: $screen_cast_dir"
    echo ""
    
    local segment_count=0
    for i in $(seq 1 10); do
        local segment_file="$screen_cast_dir/live_screen_$i.mp4"
        if [ -f "$segment_file" ]; then
            segment_count=$((segment_count + 1))
            local size=$(ls -lh "$segment_file" | awk '{print $5}')
            local age=$(stat -c %Y "$segment_file")
            local now=$(date +%s)
            local age_seconds=$((now - age))
            local age_formatted=""
            
            if [ $age_seconds -lt 60 ]; then
                age_formatted="${age_seconds}s ago"
            elif [ $age_seconds -lt 3600 ]; then
                local minutes=$((age_seconds / 60))
                age_formatted="${minutes}m ago"
            else
                local hours=$((age_seconds / 3600))
                age_formatted="${hours}h ago"
            fi
            
            echo "  live_screen_$i.mp4 - $size - $age_formatted"
        fi
    done
    
    if [ $segment_count -eq 0 ]; then
        echo -e "${YELLOW}No segments found${NC}"
    else
        echo ""
        echo -e "${BLUE}DLNA URLs:${NC}"
        local local_ip=$(hostname -I | awk '{print $1}')
        for i in $(seq 1 3); do
            local segment_file="$screen_cast_dir/live_screen_$i.mp4"
            if [ -f "$segment_file" ]; then
                echo "  http://$local_ip:8200/live_screen_$i.mp4"
            fi
        done
    fi
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to show system status
show_system_status() {
    echo -e "${GREEN}System Status${NC}"
    echo ""
    
    # Check X11 display
    if [ -z "$DISPLAY" ]; then
        echo -e "X11 Display: ${RED}Not available${NC}"
    else
        echo -e "X11 Display: ${GREEN}$DISPLAY${NC}"
    fi
    
    # Check ffmpeg
    if command -v ffmpeg &> /dev/null; then
        echo -e "FFmpeg: ${GREEN}Available${NC}"
    else
        echo -e "FFmpeg: ${RED}Not found${NC}"
    fi
    
    # Check MiniDLNA
    if systemctl is-active --quiet minidlna; then
        echo -e "MiniDLNA: ${GREEN}Running${NC}"
    else
        echo -e "MiniDLNA: ${RED}Stopped${NC}"
    fi
    
    # Check screen cast directory
    local screen_cast_dir="/var/lib/minidlna/screen_cast"
    if [ -d "$screen_cast_dir" ]; then
        echo -e "Screen Cast Dir: ${GREEN}Exists${NC}"
        local total_size=$(du -sh "$screen_cast_dir" 2>/dev/null | awk '{print $1}')
        echo "  Total Size: $total_size"
    else
        echo -e "Screen Cast Dir: ${RED}Not found${NC}"
    fi
    
    # Check network
    local local_ip=$(hostname -I | awk '{print $1}')
    echo "Local IP: $local_ip"
    
    echo ""
    echo -n "Press Enter to continue..."
    read
}

# Function to show help
show_help() {
    echo -e "${GREEN}Continuous Screen Cast Help${NC}"
    echo ""
    echo "This system captures your desktop screen in short segments and makes"
    echo "them available through DLNA for near real-time screen sharing."
    echo ""
    echo "Key Features:"
    echo "• 30-second segments for near real-time experience"
    echo "• Automatic segment rotation (keeps last 3 segments)"
    echo "• TV-compatible encoding (H.264 baseline profile)"
    echo "• DLNA integration with automatic rescan"
    echo "• Real-time monitoring of segment status"
    echo ""
    echo "Files:"
    echo "• continuous_screen_cast.sh - Main casting script"
    echo "• monitor_screen_cast.sh - Real-time monitoring"
    echo "• test_continuous_screen_cast.sh - System testing"
    echo "• continuous_screen_cast.conf - Configuration"
    echo ""
    echo "For detailed documentation, see README_continuous_screen_cast.md"
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
                start_casting
                ;;
            2)
                monitor_segments
                ;;
            3)
                test_system
                ;;
            4)
                configure_settings
                ;;
            5)
                view_segments
                ;;
            6)
                show_system_status
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