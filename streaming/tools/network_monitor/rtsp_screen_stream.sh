#!/bin/bash
# Real-Time RTSP Screen Streaming
# Provides true real-time streaming with <2 second latency

# Configuration
RTSP_PORT=8554
RTSP_PATH="/screen"
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_BITRATE=3000k
AUDIO_BITRATE=128k
FRAMERATE=30
GOP_SIZE=30
BUFFER_SIZE=1000k

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
RTSP_URL="rtsp://$LOCAL_IP:$RTSP_PORT$RTSP_PATH"

echo "🎬 Starting Real-Time RTSP Screen Streaming"
echo "=========================================="
echo "📺 RTSP URL: $RTSP_URL"
echo "📐 Resolution: ${VIDEO_WIDTH}x${VIDEO_HEIGHT}"
echo "⚡ Target Latency: <2 seconds"
echo ""

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

# Check if port is available
if netstat -tuln | grep -q ":$RTSP_PORT "; then
    echo "❌ Error: Port $RTSP_PORT is already in use"
    echo "   Please stop the existing service or use a different port"
    exit 1
fi

# Function to show help
show_help() {
    echo "Real-Time RTSP Screen Streaming"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -p, --port        Set RTSP port (default: 8554)"
    echo "  -r, --resolution  Set video resolution (default: 1280x720)"
    echo "  -b, --bitrate     Set video bitrate (default: 3000k)"
    echo "  -f, --framerate   Set framerate (default: 30)"
    echo "  -g, --gop         Set GOP size (default: 30)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Start with default settings"
    echo "  $0 -p 8555 -r 1920x1080     # Custom port and resolution"
    echo "  $0 -b 5000k -f 60           # High bitrate, 60fps"
    echo ""
    echo "RTSP URL will be: rtsp://[your-ip]:[port]/screen"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            RTSP_PORT="$2"
            shift 2
            ;;
        -r|--resolution)
            IFS='x' read -r VIDEO_WIDTH VIDEO_HEIGHT <<< "$2"
            shift 2
            ;;
        -b|--bitrate)
            VIDEO_BITRATE="$2"
            shift 2
            ;;
        -f|--framerate)
            FRAMERATE="$2"
            shift 2
            ;;
        -g|--gop)
            GOP_SIZE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Update RTSP URL with new port
RTSP_URL="rtsp://$LOCAL_IP:$RTSP_PORT$RTSP_PATH"

echo "🚀 Starting RTSP server..."
echo "📡 Port: $RTSP_PORT"
echo "📐 Resolution: ${VIDEO_WIDTH}x${VIDEO_HEIGHT}"
echo "🎥 Bitrate: $VIDEO_BITRATE"
echo "🔄 Framerate: $FRAMERATE"
echo "📦 GOP Size: $GOP_SIZE"
echo ""

# Set up signal handler for graceful shutdown
trap 'echo ""; echo "🛑 Stopping RTSP server..."; kill $FFMPEG_PID 2>/dev/null; exit 0' INT

# Start RTSP server with ultra-low latency settings
echo "🎬 Starting screen capture and RTSP streaming..."
echo "📺 Stream URL: $RTSP_URL"
echo ""
echo "To connect from another device:"
echo "  VLC: Media -> Open Network Stream -> $RTSP_URL"
echo "  FFplay: ffplay $RTSP_URL"
echo "  GStreamer: gst-launch-1.0 rtspsrc location=$RTSP_URL ! decodebin ! autovideosink"
echo ""
echo "Press Ctrl+C to stop streaming..."

# Ultra-low latency FFmpeg command
ffmpeg \
    -f x11grab \
    -framerate $FRAMERATE \
    -video_size ${VIDEO_WIDTH}x${VIDEO_HEIGHT} \
    -i :0.0 \
    -f alsa \
    -i default \
    -c:v libx264 \
    -preset ultrafast \
    -tune zerolatency \
    -profile:v baseline \
    -level 3.1 \
    -pix_fmt yuv420p \
    -b:v $VIDEO_BITRATE \
    -maxrate $VIDEO_BITRATE \
    -bufsize $BUFFER_SIZE \
    -g $GOP_SIZE \
    -keyint_min $GOP_SIZE \
    -sc_threshold 0 \
    -c:a aac \
    -b:a $AUDIO_BITRATE \
    -ar 44100 \
    -ac 2 \
    -f rtsp \
    -rtsp_transport tcp \
    -muxdelay 0.1 \
    -muxpreload 0.1 \
    "rtsp://0.0.0.0:$RTSP_PORT$RTSP_PATH" &

FFMPEG_PID=$!

# Wait for FFmpeg to start
sleep 3

# Check if FFmpeg is still running
if ! kill -0 $FFMPEG_PID 2>/dev/null; then
    echo "❌ Error: Failed to start RTSP server"
    exit 1
fi

echo "✅ RTSP server started successfully!"
echo "🆔 Process ID: $FFMPEG_PID"
echo ""

# Monitor the stream
while kill -0 $FFMPEG_PID 2>/dev/null; do
    sleep 1
done

echo "❌ RTSP server stopped unexpectedly"
exit 1