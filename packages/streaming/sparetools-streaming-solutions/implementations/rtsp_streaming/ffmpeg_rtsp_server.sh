#!/bin/bash
# FFmpeg RTSP Server for Screen Casting
# Provides RTSP stream of desktop screen capture

# Configuration
RTSP_PORT=8554
STREAM_PATH="/screen"
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_BITRATE=2000k
AUDIO_BITRATE=128k

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "Starting FFmpeg RTSP Server..."
echo "Stream URL: rtsp://$LOCAL_IP:$RTSP_PORT$STREAM_PATH"

# Check if X11 display is available
if [ -z "$DISPLAY" ]; then
    echo "Error: No X11 display available"
    exit 1
fi

# Start FFmpeg RTSP server
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
    -f rtsp \
    -rtsp_transport tcp \
    rtsp://0.0.0.0:$RTSP_PORT$STREAM_PATH