#!/bin/bash
# Optimized Continuous Screen Casting Script
# Provides pseudo-real-time streaming via continuous file updates

# Configuration
STREAM_DIR="/var/lib/continuous-stream"
STREAM_FILE="live_screen.mp4"
SEGMENT_DURATION=8
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_BITRATE=1500k
AUDIO_BITRATE=96k

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "Starting Optimized Continuous Screen Casting..."
echo "Stream Directory: $STREAM_DIR"
echo "Stream File: $STREAM_FILE"
echo "DLNA URL: http://$LOCAL_IP:8200/"

# Check if X11 display is available
if [ -z "$DISPLAY" ]; then
    echo "Error: No X11 display available"
    exit 1
fi

# Create stream directory
mkdir -p "$STREAM_DIR"

# Function to force DLNA rescan
force_dlna_rescan() {
    sudo systemctl restart minidlna
    sleep 2
}

# Function to capture screen segment
capture_segment() {
    local output_file="$1"
    local duration="$2"
    
    ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -video_size ${VIDEO_WIDTH}x${VIDEO_HEIGHT} \
        -i :0.0 \
        -f alsa \
        -i default \
        -c:v libx264 \
        -preset ultrafast \
        -tune zerolatency \
        -profile:v baseline \
        -level 3.0 \
        -pix_fmt yuv420p \
        -b:v $VIDEO_BITRATE \
        -maxrate $VIDEO_BITRATE \
        -bufsize 3000k \
        -c:a aac \
        -b:a $AUDIO_BITRATE \
        -t $duration \
        "$output_file" 2>/dev/null
}

# Function to update stream file
update_stream() {
    local temp_file="/tmp/stream_temp_$$.mp4"
    local target_file="$STREAM_DIR/$STREAM_FILE"
    
    # Capture new segment
    capture_segment "$temp_file" $SEGMENT_DURATION
    
    if [ -f "$temp_file" ]; then
        # Move to stream directory
        mv "$temp_file" "$target_file"
        
        # Set permissions
        chmod 644 "$target_file"
        
        # Force DLNA rescan
        force_dlna_rescan
        
        echo "$(date): Stream updated - $(ls -lh "$target_file" | awk '{print $5}')"
    else
        echo "$(date): Error capturing segment"
    fi
}

# Initial setup
echo "Initializing continuous stream..."

# Start MiniDLNA with continuous stream config
sudo systemctl stop minidlna
sudo minidlnad -f /etc/minidlna/continuous-stream.conf -R

# Wait for MiniDLNA to start
sleep 3

# Main loop
echo "Starting continuous capture loop..."
while true; do
    update_stream
    sleep $SEGMENT_DURATION
done