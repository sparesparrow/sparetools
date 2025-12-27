#!/bin/bash
# FFmpeg HLS Server for Screen Casting
# Generates HLS segments for real-time screen streaming

# Configuration
HLS_DIR="/var/lib/hls-server"
SEGMENT_DURATION=5
PLAYLIST_SIZE=3
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_BITRATE=2000k
AUDIO_BITRATE=128k

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "Starting FFmpeg HLS Server..."
echo "HLS Directory: $HLS_DIR"
echo "Playlist URL: http://$LOCAL_IP:8080/hls/screen.m3u8"

# Check if X11 display is available
if [ -z "$DISPLAY" ]; then
    echo "Error: No X11 display available"
    exit 1
fi

# Create HLS directory
mkdir -p "$HLS_DIR"

# Start FFmpeg HLS server
ffmpeg \
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
    -bufsize 4000k \
    -c:a aac \
    -b:a $AUDIO_BITRATE \
    -f hls \
    -hls_time $SEGMENT_DURATION \
    -hls_list_size $PLAYLIST_SIZE \
    -hls_flags delete_segments \
    -hls_segment_filename "$HLS_DIR/segment_%03d.ts" \
    "$HLS_DIR/screen.m3u8"