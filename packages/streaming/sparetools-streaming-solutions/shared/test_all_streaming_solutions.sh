#!/bin/bash
# Test All Streaming Solutions
# Comprehensive test script for all three streaming approaches

echo "Testing All Streaming Solutions"
echo "==============================="
echo ""

# Configuration
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Test RTSP Streaming
echo "1. Testing RTSP Streaming"
echo "========================="
echo "RTSP URL: rtsp://$LOCAL_IP:8554/screen"
echo ""

# Check if RTSP server is running
if pgrep -f "gstreamer_rtsp_server.py\|ffmpeg_rtsp_server.sh" > /dev/null; then
    echo "✓ RTSP server is running"
    echo "Testing RTSP client..."
    python3 rtsp_streaming/rtsp_client_test.py "rtsp://$LOCAL_IP:8554/screen" &
    RTSP_PID=$!
    sleep 10
    kill $RTSP_PID 2>/dev/null
    echo "RTSP test completed"
else
    echo "✗ RTSP server is not running"
    echo "Start with: python3 rtsp_streaming/gstreamer_rtsp_server.py"
fi

echo ""

# Test HLS Streaming
echo "2. Testing HLS Streaming"
echo "========================"
echo "HLS URL: http://$LOCAL_IP:8080/hls/screen.m3u8"
echo ""

# Check if HLS server is running
if pgrep -f "hls_http_server.py\|ffmpeg_hls_server.sh" > /dev/null; then
    echo "✓ HLS server is running"
    echo "Testing HLS client..."
    python3 hls_streaming/hls_client_test.py "http://$LOCAL_IP:8080/hls/screen.m3u8" &
    HLS_PID=$!
    sleep 10
    kill $HLS_PID 2>/dev/null
    echo "HLS test completed"
else
    echo "✗ HLS server is not running"
    echo "Start with: python3 hls_streaming/hls_http_server.py"
fi

echo ""

# Test Continuous File Streaming
echo "3. Testing Continuous File Streaming"
echo "===================================="
echo "DLNA URL: http://$LOCAL_IP:8200/"
echo ""

# Check if continuous stream is running
if pgrep -f "optimized_continuous_cast.sh" > /dev/null; then
    echo "✓ Continuous stream is running"
    echo "Testing continuous stream..."
    bash continuous_file_streaming/test_continuous_stream.sh
else
    echo "✗ Continuous stream is not running"
    echo "Start with: bash continuous_file_streaming/optimized_continuous_cast.sh"
fi

echo ""

# Summary
echo "Summary"
echo "======="
echo "RTSP: $(pgrep -f "gstreamer_rtsp_server.py\|ffmpeg_rtsp_server.sh" > /dev/null && echo "Running" || echo "Not running")"
echo "HLS: $(pgrep -f "hls_http_server.py\|ffmpeg_hls_server.sh" > /dev/null && echo "Running" || echo "Not running")"
echo "Continuous: $(pgrep -f "optimized_continuous_cast.sh" > /dev/null && echo "Running" || echo "Not running")"
echo ""

echo "To start all services:"
echo "1. RTSP: python3 rtsp_streaming/gstreamer_rtsp_server.py"
echo "2. HLS: python3 hls_streaming/hls_http_server.py"
echo "3. Continuous: bash continuous_file_streaming/optimized_continuous_cast.sh"