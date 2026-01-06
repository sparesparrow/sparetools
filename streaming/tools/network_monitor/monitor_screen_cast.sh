#!/bin/bash
# Monitor Continuous Screen Casting Segments
# Shows real-time status of screen cast segments

SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
REFRESH_INTERVAL=5

# Function to show segment status
show_segment_status() {
    clear
    echo "🎬 Continuous Screen Cast Monitor"
    echo "=================================="
    echo "📁 Directory: $SCREEN_CAST_DIR"
    echo "🕐 $(date)"
    echo ""
    
    # Check if directory exists
    if [ ! -d "$SCREEN_CAST_DIR" ]; then
        echo "❌ Screen cast directory not found: $SCREEN_CAST_DIR"
        return 1
    fi
    
    # Show segment information
    echo "📹 Available Segments:"
    echo "----------------------"
    
    local segment_count=0
    for i in $(seq 1 10); do
        local segment_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
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
            
            local status=""
            if [ $i -eq 1 ]; then
                status="🟢 CURRENT"
            elif [ $i -eq 2 ]; then
                status="🟡 PREVIOUS"
            elif [ $i -eq 3 ]; then
                status="🔴 OLDEST"
            else
                status="⚪ OLD"
            fi
            
            echo "   live_screen_$i.mp4 - $size - $age_formatted - $status"
        fi
    done
    
    if [ $segment_count -eq 0 ]; then
        echo "   No segments found"
    fi
    
    echo ""
    echo "🌐 DLNA URLs:"
    echo "-------------"
    local local_ip=$(hostname -I | awk '{print $1}')
    for i in $(seq 1 3); do
        local segment_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
        if [ -f "$segment_file" ]; then
            echo "   http://$local_ip:8200/live_screen_$i.mp4"
        fi
    done
    
    echo ""
    echo "📊 System Status:"
    echo "-----------------"
    
    # Check MiniDLNA status
    if systemctl is-active --quiet minidlna; then
        echo "   MiniDLNA: 🟢 Running"
    else
        echo "   MiniDLNA: 🔴 Stopped"
    fi
    
    # Check disk usage
    local disk_usage=$(df -h "$SCREEN_CAST_DIR" | tail -1 | awk '{print $5}')
    echo "   Disk Usage: $disk_usage"
    
    # Check total segment size
    local total_size=$(du -sh "$SCREEN_CAST_DIR" 2>/dev/null | awk '{print $1}')
    echo "   Total Size: $total_size"
    
    echo ""
    echo "Press Ctrl+C to exit monitor"
}

# Function to show help
show_help() {
    echo "Continuous Screen Cast Monitor"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -i, --interval Set refresh interval in seconds (default: 5)"
    echo "  -d, --dir      Set screen cast directory (default: $SCREEN_CAST_DIR)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Monitor with default settings"
    echo "  $0 -i 2               # Refresh every 2 seconds"
    echo "  $0 -d /custom/path    # Monitor custom directory"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--interval)
            REFRESH_INTERVAL="$2"
            shift 2
            ;;
        -d|--dir)
            SCREEN_CAST_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set up signal handler for graceful shutdown
trap 'echo ""; echo "🛑 Stopping monitor..."; exit 0' INT

# Main monitoring loop
while true; do
    show_segment_status
    sleep $REFRESH_INTERVAL
done