#!/bin/bash
# Continuous Screen Casting with Segmented Video
# Captures screen in 30-second segments and makes them available through DLNA

# Configuration
SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
SEGMENT_DURATION=30
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_BITRATE=2000k
AUDIO_BITRATE=128k
MAX_SEGMENTS=3

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "🎬 Starting Continuous Screen Casting..."
echo "📁 Screen Cast Directory: $SCREEN_CAST_DIR"
echo "⏱️  Segment Duration: $SEGMENT_DURATION seconds"
echo "📺 Resolution: ${VIDEO_WIDTH}x${VIDEO_HEIGHT}"
echo "🌐 DLNA URL: http://$LOCAL_IP:8200/"

# Check if X11 display is available
if [ -z "$DISPLAY" ]; then
    echo "❌ Error: No X11 display available"
    exit 1
fi

# Check if ffmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ Error: ffmpeg not found. Please install it first."
    exit 1
fi

# Create screen cast directory
echo "📁 Creating screen cast directory..."
sudo mkdir -p "$SCREEN_CAST_DIR"
sudo chown $USER:$USER "$SCREEN_CAST_DIR"

# Function to force DLNA rescan
force_dlna_rescan() {
    echo "🔄 Forcing DLNA rescan..."
    sudo systemctl restart minidlna
    sleep 3
}

# Function to capture screen segment
capture_segment() {
    local output_file="$1"
    local duration="$2"
    
    echo "📹 Capturing segment: $output_file"
    
    ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -video_size ${VIDEO_WIDTH}x${VIDEO_HEIGHT} \
        -i :0.0 \
        -f alsa \
        -i default \
        -c:v libx264 \
        -preset slow \
        -profile:v baseline \
        -level 3.0 \
        -pix_fmt yuv420p \
        -b:v $VIDEO_BITRATE \
        -maxrate $VIDEO_BITRATE \
        -bufsize 4000k \
        -c:a aac \
        -b:a $AUDIO_BITRATE \
        -t $duration \
        "$output_file" 2>/dev/null
}

# Function to rotate segments
rotate_segments() {
    local current_segment="$1"
    
    # Move existing segments
    for i in $(seq $((MAX_SEGMENTS-1)) -1 1); do
        local old_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
        local new_file="$SCREEN_CAST_DIR/live_screen_$((i+1)).mp4"
        
        if [ -f "$old_file" ]; then
            mv "$old_file" "$new_file"
        fi
    done
    
    # Move current segment to position 1
    mv "$current_segment" "$SCREEN_CAST_DIR/live_screen_1.mp4"
    
    # Set permissions
    chmod 644 "$SCREEN_CAST_DIR/live_screen_1.mp4"
}

# Function to cleanup old segments
cleanup_old_segments() {
    echo "🧹 Cleaning up old segments..."
    
    # Remove segments beyond MAX_SEGMENTS
    for i in $(seq $((MAX_SEGMENTS+1)) 10); do
        local old_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
        if [ -f "$old_file" ]; then
            rm -f "$old_file"
        fi
    done
}

# Function to update stream
update_stream() {
    local temp_file="/tmp/screen_cast_temp_$$.mp4"
    local segment_file="$SCREEN_CAST_DIR/live_screen_temp.mp4"
    
    # Capture new segment
    capture_segment "$temp_file" $SEGMENT_DURATION
    
    if [ -f "$temp_file" ]; then
        # Move to screen cast directory
        mv "$temp_file" "$segment_file"
        
        # Rotate segments
        rotate_segments "$segment_file"
        
        # Cleanup old segments
        cleanup_old_segments
        
        # Force DLNA rescan
        force_dlna_rescan
        
        # Show status
        local file_size=$(ls -lh "$SCREEN_CAST_DIR/live_screen_1.mp4" | awk '{print $5}')
        echo "✅ $(date): Segment updated - Size: $file_size"
        
        # Show available segments
        echo "📁 Available segments:"
        for i in $(seq 1 $MAX_SEGMENTS); do
            local segment_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
            if [ -f "$segment_file" ]; then
                local size=$(ls -lh "$segment_file" | awk '{print $5}')
                local age=$(stat -c %Y "$segment_file")
                local now=$(date +%s)
                local age_seconds=$((now - age))
                echo "   live_screen_$i.mp4 - $size (${age_seconds}s ago)"
            fi
        done
    else
        echo "❌ $(date): Error capturing segment"
    fi
}

# Function to show help
show_help() {
    echo "Continuous Screen Casting with Segmented Video"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --duration Set segment duration in seconds (default: 30)"
    echo "  -s, --segments Set maximum segments to keep (default: 3)"
    echo "  -r, --resolution Set video resolution (default: 1280x720)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start with default settings"
    echo "  $0 -d 60 -s 5        # 60-second segments, keep 5"
    echo "  $0 -r 1920x1080      # Full HD resolution"
    echo ""
    echo "Control:"
    echo "  Ctrl+C               # Stop casting"
    echo "  Check $SCREEN_CAST_DIR for segments"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--duration)
            SEGMENT_DURATION="$2"
            shift 2
            ;;
        -s|--segments)
            MAX_SEGMENTS="$2"
            shift 2
            ;;
        -r|--resolution)
            IFS='x' read -r VIDEO_WIDTH VIDEO_HEIGHT <<< "$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Initial setup
echo "🚀 Initializing continuous screen casting..."

# Check if MiniDLNA is running
if ! systemctl is-active --quiet minidlna; then
    echo "⚠️  MiniDLNA not running. Starting it..."
    sudo systemctl start minidlna
    sleep 5
fi

# Create initial empty segments to establish the pattern
echo "📁 Creating initial segment structure..."
for i in $(seq 1 $MAX_SEGMENTS); do
    touch "$SCREEN_CAST_DIR/live_screen_$i.mp4"
done

# Force initial DLNA rescan
force_dlna_rescan

echo "🎬 Starting continuous capture loop..."
echo "📺 Segments will be available at:"
echo "   http://$LOCAL_IP:8200/live_screen_1.mp4 (current)"
echo "   http://$LOCAL_IP:8200/live_screen_2.mp4 (previous)"
echo "   http://$LOCAL_IP:8200/live_screen_3.mp4 (oldest)"
echo ""
echo "Press Ctrl+C to stop..."

# Set up signal handler for graceful shutdown
trap 'echo ""; echo "🛑 Stopping continuous screen casting..."; exit 0' INT

# Main loop
while true; do
    update_stream
    sleep $SEGMENT_DURATION
done