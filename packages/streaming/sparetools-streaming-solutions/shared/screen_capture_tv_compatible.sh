#!/bin/bash
# TV-Compatible Screen Capture for DLNA/UPnP Casting

SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${SCREEN_CAST_DIR}/screen_cast_tv_${TIMESTAMP}.mp4"

echo "Creating TV-compatible screen capture..."
echo "Output: $OUTPUT_FILE"

# TV-compatible ffmpeg settings:
# - H.264 baseline profile (most compatible)
# - AAC audio (if available)
# - MP4 container
# - YUV420P pixel format
# - Reasonable bitrate for streaming
ffmpeg -f x11grab -i :0.0 \
       -f alsa -i default \
       -c:v libx264 -preset slow -profile:v baseline -level 3.0 \
       -pix_fmt yuv420p \
       -c:a aac -b:a 128k \
       -vf "scale=1280:720" \
       -maxrate 2M -bufsize 4M \
       -y "$OUTPUT_FILE" &

FFMPEG_PID=$!

echo "Screen capture started with PID: $FFMPEG_PID"
echo "Press Ctrl+C to stop capture"

# Wait for interrupt
trap "kill $FFMPEG_PID; echo 'Screen capture stopped'; exit 0" INT
wait $FFMPEG_PID