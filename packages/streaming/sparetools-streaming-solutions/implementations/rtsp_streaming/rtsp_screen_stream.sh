#!/bin/bash
# RTSP Screen Stream
# Real-time screen streaming using FFmpeg UDP streaming (compatible with RTSP clients)

# Configuration
STREAM_PORT=8554
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_FPS=25
VIDEO_BITRATE=2000k
AUDIO_BITRATE=128k

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "RTSP Screen Stream"
echo "=================="
echo "Starting real-time screen streaming..."
echo "Stream URL: udp://$LOCAL_IP:$STREAM_PORT"
echo ""

# Check if X11 display is available
if [ -z "$DISPLAY" ]; then
    echo "Error: No X11 display available"
    exit 1
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: FFmpeg not found. Please install FFmpeg first."
    exit 1
fi

# Function to start streaming server using FFmpeg UDP streaming
start_streaming_server() {
    echo "Starting streaming server on port $STREAM_PORT..."
    
    # Start FFmpeg with UDP output
    ffmpeg \
        -f x11grab \
        -framerate $VIDEO_FPS \
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
        -g 50 \
        -keyint_min 25 \
        -sc_threshold 0 \
        -c:a aac \
        -b:a $AUDIO_BITRATE \
        -f mpegts \
        "udp://$LOCAL_IP:$STREAM_PORT" 2>/dev/null &
    
    FFMPEG_PID=$!
    echo "FFmpeg streaming server started (PID: $FFMPEG_PID)"
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server is running
    if kill -0 $FFMPEG_PID 2>/dev/null; then
        echo "✅ Streaming server is running successfully!"
        echo ""
        echo "Stream Information:"
        echo "  URL: udp://$LOCAL_IP:$STREAM_PORT"
        echo "  Resolution: ${VIDEO_WIDTH}x${VIDEO_HEIGHT}"
        echo "  Frame Rate: $VIDEO_FPS fps"
        echo "  Video Bitrate: $VIDEO_BITRATE"
        echo "  Audio Bitrate: $AUDIO_BITRATE"
        echo ""
        echo "Client Playback:"
        echo "  VLC: Media → Open Network Stream → udp://@$LOCAL_IP:$STREAM_PORT"
        echo "  FFmpeg: ffmpeg -i udp://$LOCAL_IP:$STREAM_PORT -c copy output.mp4"
        echo "  Python: python3 rtsp_client_test.py udp://$LOCAL_IP:$STREAM_PORT"
        echo ""
        echo "Press Ctrl+C to stop the stream"
        
        # Wait for user interrupt
        trap 'echo ""; echo "Stopping streaming server..."; kill $FFMPEG_PID 2>/dev/null; echo "Streaming server stopped."; exit 0' INT
        wait $FFMPEG_PID
    else
        echo "❌ Failed to start streaming server"
        exit 1
    fi
}

# Function to test stream
test_stream() {
    echo "Testing stream connectivity..."
    
    # Test with FFmpeg client
    timeout 10s ffmpeg -i "udp://$LOCAL_IP:$STREAM_PORT" -t 5 -f null - 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Stream test successful"
    else
        echo "⚠️  Stream test failed - server may still be starting"
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        start_streaming_server
        ;;
    "test")
        test_stream
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [start|test|help]"
        echo ""
        echo "Commands:"
        echo "  start  - Start screen streaming (default)"
        echo "  test   - Test stream connectivity"
        echo "  help   - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Start streaming"
        echo "  $0 start             # Start streaming"
        echo "  $0 test              # Test stream"
        echo ""
        echo "Stream URL: udp://$LOCAL_IP:$STREAM_PORT"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac