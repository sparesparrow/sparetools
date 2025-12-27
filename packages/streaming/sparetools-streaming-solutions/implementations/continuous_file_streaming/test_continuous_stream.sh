#!/bin/bash
# Test Continuous Stream
# Test the continuous streaming functionality

echo "Testing Continuous Stream..."
echo "============================"

# Configuration
STREAM_DIR="/var/lib/continuous-stream"
STREAM_FILE="live_screen.mp4"
TARGET_FILE="$STREAM_DIR/$STREAM_FILE"

# Check if stream file exists
if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: Stream file not found at $TARGET_FILE"
    echo "Make sure the continuous stream is running"
    exit 1
fi

echo "Stream file found: $TARGET_FILE"
echo "File size: $(ls -lh "$TARGET_FILE" | awk '{print $5}')"
echo "Last modified: $(stat -c %y "$TARGET_FILE")"

# Test file properties
echo ""
echo "File Properties:"
echo "================"
ffprobe -v quiet -print_format json -show_format -show_streams "$TARGET_FILE" | jq '.'

# Test DLNA accessibility
echo ""
echo "DLNA Accessibility:"
echo "==================="
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "DLNA Server: http://$LOCAL_IP:8200/"
echo "Stream URL: http://$LOCAL_IP:8200/$STREAM_FILE"

# Test if file is accessible via DLNA
if curl -s -I "http://$LOCAL_IP:8200/$STREAM_FILE" | head -1 | grep -q "200 OK"; then
    echo "✓ File accessible via DLNA"
else
    echo "✗ File not accessible via DLNA"
fi

# Monitor file changes
echo ""
echo "Monitoring file changes for 30 seconds..."
echo "=========================================="
echo "Press Ctrl+C to stop monitoring"

start_time=$(date +%s)
last_modified=$(stat -c %Y "$TARGET_FILE")

while true; do
    current_modified=$(stat -c %Y "$TARGET_FILE")
    if [ "$current_modified" != "$last_modified" ]; then
        echo "$(date): File updated - $(ls -lh "$TARGET_FILE" | awk '{print $5}')"
        last_modified=$current_modified
    fi
    
    current_time=$(date +%s)
    if [ $((current_time - start_time)) -ge 30 ]; then
        break
    fi
    
    sleep 1
done

echo "Test completed!"