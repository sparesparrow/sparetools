#!/bin/bash
# RTSP Client Test Script
# Tests RTSP stream connectivity and playback

# Configuration
DEFAULT_RTSP_URL="rtsp://192.168.200.44:8554/screen"
TEST_DURATION=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 RTSP Client Test${NC}"
echo "=================="
echo ""

# Function to show help
show_help() {
    echo "RTSP Client Test Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [RTSP_URL]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -d, --duration    Set test duration in seconds (default: 30)"
    echo "  -v, --verbose     Enable verbose output"
    echo ""
    echo "RTSP_URL:"
    echo "  Default: $DEFAULT_RTSP_URL"
    echo "  Format: rtsp://[ip]:[port]/[path]"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Test default URL"
    echo "  $0 rtsp://192.168.1.100:8554/screen  # Test custom URL"
    echo "  $0 -d 60 -v                          # 60-second test with verbose output"
}

# Function to test RTSP connectivity
test_rtsp_connectivity() {
    local rtsp_url="$1"
    local verbose="$2"
    
    echo -e "${YELLOW}🔍 Testing RTSP connectivity...${NC}"
    
    # Extract IP and port from RTSP URL
    local ip_port=$(echo "$rtsp_url" | sed 's|rtsp://||' | sed 's|/.*||')
    local ip=$(echo "$ip_port" | cut -d: -f1)
    local port=$(echo "$ip_port" | cut -d: -f2)
    
    if [ "$verbose" = "true" ]; then
        echo "  IP: $ip"
        echo "  Port: $port"
    fi
    
    # Test TCP connectivity
    if timeout 5 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null; then
        echo -e "  ✅ TCP connection successful"
    else
        echo -e "  ❌ TCP connection failed"
        return 1
    fi
    
    # Test RTSP handshake
    if command -v ffprobe &> /dev/null; then
        echo -e "  🔍 Testing RTSP handshake..."
        if ffprobe -v quiet -rtsp_transport tcp -i "$rtsp_url" -show_entries format=duration 2>/dev/null; then
            echo -e "  ✅ RTSP handshake successful"
        else
            echo -e "  ❌ RTSP handshake failed"
            return 1
        fi
    else
        echo -e "  ⚠️  ffprobe not available, skipping handshake test"
    fi
    
    return 0
}

# Function to test with VLC
test_with_vlc() {
    local rtsp_url="$1"
    local duration="$2"
    local verbose="$3"
    
    echo -e "${YELLOW}🎬 Testing with VLC...${NC}"
    
    if ! command -v vlc &> /dev/null; then
        echo -e "  ❌ VLC not found"
        return 1
    fi
    
    echo -e "  📺 Starting VLC playback for $duration seconds..."
    echo -e "  🔗 URL: $rtsp_url"
    
    if [ "$verbose" = "true" ]; then
        vlc --intf dummy --rtsp-tcp "$rtsp_url" --play-and-exit --run-time=$duration 2>&1 &
    else
        vlc --intf dummy --rtsp-tcp "$rtsp_url" --play-and-exit --run-time=$duration > /dev/null 2>&1 &
    fi
    
    local vlc_pid=$!
    
    # Wait for VLC to start
    sleep 2
    
    if kill -0 $vlc_pid 2>/dev/null; then
        echo -e "  ✅ VLC started successfully"
        echo -e "  ⏱️  Playing for $duration seconds..."
        
        # Wait for duration
        sleep $duration
        
        # Stop VLC
        kill $vlc_pid 2>/dev/null
        wait $vlc_pid 2>/dev/null
        
        echo -e "  ✅ VLC test completed"
        return 0
    else
        echo -e "  ❌ VLC failed to start"
        return 1
    fi
}

# Function to test with FFplay
test_with_ffplay() {
    local rtsp_url="$1"
    local duration="$2"
    local verbose="$3"
    
    echo -e "${YELLOW}🎬 Testing with FFplay...${NC}"
    
    if ! command -v ffplay &> /dev/null; then
        echo -e "  ❌ FFplay not found"
        return 1
    fi
    
    echo -e "  📺 Starting FFplay for $duration seconds..."
    echo -e "  🔗 URL: $rtsp_url"
    
    local ffplay_cmd="ffplay -rtsp_transport tcp -t $duration -autoexit -noborder -an"
    
    if [ "$verbose" = "true" ]; then
        $ffplay_cmd "$rtsp_url" &
    else
        $ffplay_cmd "$rtsp_url" > /dev/null 2>&1 &
    fi
    
    local ffplay_pid=$!
    
    # Wait for FFplay to start
    sleep 2
    
    if kill -0 $ffplay_pid 2>/dev/null; then
        echo -e "  ✅ FFplay started successfully"
        echo -e "  ⏱️  Playing for $duration seconds..."
        
        # Wait for duration
        sleep $duration
        
        # Stop FFplay
        kill $ffplay_pid 2>/dev/null
        wait $ffplay_pid 2>/dev/null
        
        echo -e "  ✅ FFplay test completed"
        return 0
    else
        echo -e "  ❌ FFplay failed to start"
        return 1
    fi
}

# Function to test with GStreamer
test_with_gstreamer() {
    local rtsp_url="$1"
    local duration="$2"
    local verbose="$3"
    
    echo -e "${YELLOW}🎬 Testing with GStreamer...${NC}"
    
    if ! command -v gst-launch-1.0 &> /dev/null; then
        echo -e "  ❌ GStreamer not found"
        return 1
    fi
    
    echo -e "  📺 Starting GStreamer for $duration seconds..."
    echo -e "  🔗 URL: $rtsp_url"
    
    local gst_cmd="gst-launch-1.0 rtspsrc location=$rtsp_url ! decodebin ! autovideosink"
    
    if [ "$verbose" = "true" ]; then
        timeout $duration $gst_cmd &
    else
        timeout $duration $gst_cmd > /dev/null 2>&1 &
    fi
    
    local gst_pid=$!
    
    # Wait for GStreamer to start
    sleep 2
    
    if kill -0 $gst_pid 2>/dev/null; then
        echo -e "  ✅ GStreamer started successfully"
        echo -e "  ⏱️  Playing for $duration seconds..."
        
        # Wait for duration
        wait $gst_pid 2>/dev/null
        
        echo -e "  ✅ GStreamer test completed"
        return 0
    else
        echo -e "  ❌ GStreamer failed to start"
        return 1
    fi
}

# Function to measure latency
measure_latency() {
    local rtsp_url="$1"
    local verbose="$2"
    
    echo -e "${YELLOW}⏱️  Measuring latency...${NC}"
    
    if ! command -v ffprobe &> /dev/null; then
        echo -e "  ❌ ffprobe not available for latency measurement"
        return 1
    fi
    
    # Start latency measurement
    local start_time=$(date +%s.%N)
    
    # Try to get stream info
    if ffprobe -v quiet -rtsp_transport tcp -i "$rtsp_url" -show_entries format=duration 2>/dev/null; then
        local end_time=$(date +%s.%N)
        local latency=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")
        
        if [ "$latency" != "unknown" ]; then
            echo -e "  📊 Connection latency: ${latency}s"
        else
            echo -e "  ⚠️  Could not calculate latency"
        fi
    else
        echo -e "  ❌ Could not measure latency"
        return 1
    fi
}

# Function to show test results
show_test_results() {
    local rtsp_url="$1"
    local total_tests="$2"
    local passed_tests="$3"
    
    echo ""
    echo -e "${BLUE}📊 Test Results Summary${NC}"
    echo "========================"
    echo "RTSP URL: $rtsp_url"
    echo "Total Tests: $total_tests"
    echo "Passed Tests: $passed_tests"
    echo "Failed Tests: $((total_tests - passed_tests))"
    echo ""
    
    if [ $passed_tests -eq $total_tests ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
    elif [ $passed_tests -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some tests passed${NC}"
    else
        echo -e "${RED}❌ All tests failed${NC}"
    fi
}

# Parse command line arguments
VERBOSE=false
RTSP_URL="$DEFAULT_RTSP_URL"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--duration)
            TEST_DURATION="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            if [[ "$1" =~ ^rtsp:// ]]; then
                RTSP_URL="$1"
            else
                echo "Unknown option: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Main test execution
echo "RTSP URL: $RTSP_URL"
echo "Test Duration: $TEST_DURATION seconds"
echo "Verbose: $VERBOSE"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0

# Test 1: RTSP Connectivity
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_rtsp_connectivity "$RTSP_URL" "$VERBOSE"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 2: Latency Measurement
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if measure_latency "$RTSP_URL" "$VERBOSE"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 3: VLC Playback
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_with_vlc "$RTSP_URL" "$TEST_DURATION" "$VERBOSE"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 4: FFplay Playback
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_with_ffplay "$RTSP_URL" "$TEST_DURATION" "$VERBOSE"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 5: GStreamer Playback
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if test_with_gstreamer "$RTSP_URL" "$TEST_DURATION" "$VERBOSE"; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Show results
show_test_results "$RTSP_URL" "$TOTAL_TESTS" "$PASSED_TESTS"