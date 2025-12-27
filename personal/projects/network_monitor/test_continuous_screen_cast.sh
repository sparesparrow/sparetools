#!/bin/bash
# Test Continuous Screen Casting Functionality
# Verifies that the continuous screen casting system is working correctly

SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
TEST_DURATION=120  # 2 minutes
SEGMENT_DURATION=30

echo "🧪 Testing Continuous Screen Casting System"
echo "==========================================="
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    local errors=0
    
    # Check if X11 display is available
    if [ -z "$DISPLAY" ]; then
        echo "❌ X11 display not available"
        errors=$((errors + 1))
    else
        echo "✅ X11 display available: $DISPLAY"
    fi
    
    # Check if ffmpeg is installed
    if ! command -v ffmpeg &> /dev/null; then
        echo "❌ ffmpeg not found"
        errors=$((errors + 1))
    else
        echo "✅ ffmpeg available: $(ffmpeg -version | head -1)"
    fi
    
    # Check if MiniDLNA is installed
    if ! command -v minidlnad &> /dev/null; then
        echo "❌ MiniDLNA not found"
        errors=$((errors + 1))
    else
        echo "✅ MiniDLNA available"
    fi
    
    # Check if screen cast directory exists
    if [ ! -d "$SCREEN_CAST_DIR" ]; then
        echo "❌ Screen cast directory not found: $SCREEN_CAST_DIR"
        errors=$((errors + 1))
    else
        echo "✅ Screen cast directory exists: $SCREEN_CAST_DIR"
    fi
    
    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) failed. Please fix them before testing."
        return 1
    fi
    
    echo "✅ All prerequisites met"
    return 0
}

# Function to test screen capture
test_screen_capture() {
    echo ""
    echo "📹 Testing screen capture..."
    
    local test_file="/tmp/test_screen_capture.mp4"
    local duration=5
    
    echo "   Capturing $duration seconds of screen..."
    
    ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -video_size 1280x720 \
        -i :0.0 \
        -f alsa \
        -i default \
        -c:v libx264 \
        -preset fast \
        -profile:v baseline \
        -level 3.0 \
        -pix_fmt yuv420p \
        -t $duration \
        "$test_file" 2>/dev/null
    
    if [ -f "$test_file" ]; then
        local size=$(ls -lh "$test_file" | awk '{print $5}')
        echo "   ✅ Screen capture successful - Size: $size"
        rm -f "$test_file"
        return 0
    else
        echo "   ❌ Screen capture failed"
        return 1
    fi
}

# Function to test DLNA connectivity
test_dlna_connectivity() {
    echo ""
    echo "🌐 Testing DLNA connectivity..."
    
    local local_ip=$(hostname -I | awk '{print $1}')
    local dlna_url="http://$local_ip:8200/"
    
    echo "   Testing DLNA server at: $dlna_url"
    
    if curl -s --connect-timeout 5 "$dlna_url" > /dev/null; then
        echo "   ✅ DLNA server accessible"
        return 0
    else
        echo "   ❌ DLNA server not accessible"
        return 1
    fi
}

# Function to test segment creation
test_segment_creation() {
    echo ""
    echo "📁 Testing segment creation..."
    
    # Create test segment
    local test_segment="$SCREEN_CAST_DIR/test_segment.mp4"
    local duration=10
    
    echo "   Creating test segment ($duration seconds)..."
    
    ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -video_size 1280x720 \
        -i :0.0 \
        -f alsa \
        -i default \
        -c:v libx264 \
        -preset fast \
        -profile:v baseline \
        -level 3.0 \
        -pix_fmt yuv420p \
        -t $duration \
        "$test_segment" 2>/dev/null
    
    if [ -f "$test_segment" ]; then
        local size=$(ls -lh "$test_segment" | awk '{print $5}')
        echo "   ✅ Test segment created - Size: $size"
        
        # Test DLNA access
        local local_ip=$(hostname -I | awk '{print $1}')
        local segment_url="http://$local_ip:8200/test_segment.mp4"
        
        echo "   Testing DLNA access to segment..."
        if curl -s --connect-timeout 5 "$segment_url" > /dev/null; then
            echo "   ✅ Segment accessible via DLNA"
        else
            echo "   ⚠️  Segment not yet accessible via DLNA (may need rescan)"
        fi
        
        # Cleanup
        rm -f "$test_segment"
        return 0
    else
        echo "   ❌ Test segment creation failed"
        return 1
    fi
}

# Function to run continuous test
run_continuous_test() {
    echo ""
    echo "🔄 Running continuous test ($TEST_DURATION seconds)..."
    echo "   This will test the full continuous casting system"
    echo "   Press Ctrl+C to stop early"
    echo ""
    
    # Start continuous casting in background
    echo "   Starting continuous casting..."
    ./continuous_screen_cast.sh &
    local cast_pid=$!
    
    # Wait a bit for initial segment
    sleep 35
    
    # Monitor segments for the test duration
    local start_time=$(date +%s)
    local end_time=$((start_time + TEST_DURATION))
    local segment_count=0
    
    echo "   Monitoring segments..."
    
    while [ $(date +%s) -lt $end_time ]; do
        # Check for new segments
        local current_segments=$(ls -1 "$SCREEN_CAST_DIR"/live_screen_*.mp4 2>/dev/null | wc -l)
        
        if [ $current_segments -gt $segment_count ]; then
            segment_count=$current_segments
            echo "   ✅ New segment detected (total: $segment_count)"
        fi
        
        sleep 5
    done
    
    # Stop continuous casting
    echo "   Stopping continuous casting..."
    kill $cast_pid 2>/dev/null
    wait $cast_pid 2>/dev/null
    
    echo "   ✅ Continuous test completed"
    echo "   Total segments created: $segment_count"
}

# Function to show test results
show_test_results() {
    echo ""
    echo "📊 Test Results Summary"
    echo "======================"
    
    # Count segments
    local segment_count=$(ls -1 "$SCREEN_CAST_DIR"/live_screen_*.mp4 2>/dev/null | wc -l)
    echo "Segments found: $segment_count"
    
    if [ $segment_count -gt 0 ]; then
        echo ""
        echo "Available segments:"
        for segment in "$SCREEN_CAST_DIR"/live_screen_*.mp4; do
            if [ -f "$segment" ]; then
                local size=$(ls -lh "$segment" | awk '{print $5}')
                local age=$(stat -c %Y "$segment")
                local now=$(date +%s)
                local age_seconds=$((now - age))
                echo "  $(basename "$segment") - $size (${age_seconds}s ago)"
            fi
        done
    fi
    
    echo ""
    echo "DLNA URLs:"
    local local_ip=$(hostname -I | awk '{print $1}')
    for i in $(seq 1 3); do
        local segment_file="$SCREEN_CAST_DIR/live_screen_$i.mp4"
        if [ -f "$segment_file" ]; then
            echo "  http://$local_ip:8200/live_screen_$i.mp4"
        fi
    done
}

# Function to show help
show_help() {
    echo "Continuous Screen Cast Test"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --duration Set test duration in seconds (default: 120)"
    echo "  -s, --segments Set segment duration in seconds (default: 30)"
    echo "  -q, --quick    Run quick test only (no continuous test)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run full test (2 minutes)"
    echo "  $0 -d 60              # Run test for 1 minute"
    echo "  $0 -q                 # Quick test only"
}

# Parse command line arguments
QUICK_TEST=false
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
        -s|--segments)
            SEGMENT_DURATION="$2"
            shift 2
            ;;
        -q|--quick)
            QUICK_TEST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main test execution
echo "Starting tests..."

# Check prerequisites
if ! check_prerequisites; then
    exit 1
fi

# Test screen capture
if ! test_screen_capture; then
    echo "❌ Screen capture test failed"
    exit 1
fi

# Test DLNA connectivity
if ! test_dlna_connectivity; then
    echo "❌ DLNA connectivity test failed"
    exit 1
fi

# Test segment creation
if ! test_segment_creation; then
    echo "❌ Segment creation test failed"
    exit 1
fi

# Run continuous test if not quick mode
if [ "$QUICK_TEST" = false ]; then
    run_continuous_test
fi

# Show results
show_test_results

echo ""
echo "✅ All tests completed successfully!"
echo ""
echo "To start continuous screen casting:"
echo "  ./continuous_screen_cast.sh"
echo ""
echo "To monitor segments:"
echo "  ./monitor_screen_cast.sh"