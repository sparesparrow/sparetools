#!/bin/bash
# Screen Capture Script for UPnP/DLNA Casting

SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${SCREEN_CAST_DIR}/screen_cast_${TIMESTAMP}.mp4"

echo "Starting screen capture to: $OUTPUT_FILE"

# Screen capture using ffmpeg
# -f x11grab : capture X11 display
# -i :0.0 : capture display :0
# -f alsa -i default : capture audio (optional)
# -c:v libx264 : H.264 video codec
# -preset ultrafast : fast encoding
# -tune zerolatency : low latency
# -c:a aac : AAC audio codec
ffmpeg -f x11grab -i :0.0 \
       -f alsa -i default \
       -c:v libx264 -preset ultrafast -tune zerolatency \
       -c:a aac -b:a 128k \
       -vf "scale=1280:720" \
       -y "$OUTPUT_FILE" &

FFMPEG_PID=$!

echo "Screen capture started with PID: $FFMPEG_PID"
echo "Press Ctrl+C to stop capture"

# Wait for interrupt
trap "kill $FFMPEG_PID; echo 'Screen capture stopped'; exit 0" INT
wait $FFMPEG_PID