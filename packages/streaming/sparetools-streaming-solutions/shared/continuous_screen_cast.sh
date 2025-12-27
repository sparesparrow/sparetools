#!/bin/bash
# Continuous Screen Casting to DLNA/UPnP TV
# Captures screen in segments and updates DLNA server

SCREEN_CAST_DIR="/var/lib/minidlna/screen_cast"
SEGMENT_DURATION=30  # 30 seconds per segment
OUTPUT_BASE="${SCREEN_CAST_DIR}/live_screen"

echo "Starting continuous screen casting to DLNA..."
echo "Segments: ${SEGMENT_DURATION}s each"
echo "Output: ${OUTPUT_BASE}_*.mp4"

# Function to create TV-compatible segment
create_segment() {
    local segment_num=$1
    local output_file="${OUTPUT_BASE}_${segment_num}.mp4"

    echo "Creating segment ${segment_num}..."

    # TV-compatible settings
    ffmpeg -f x11grab -i :0.0 \
           -t $SEGMENT_DURATION \
           -c:v libx264 -preset fast -profile:v baseline -level 3.0 \
           -pix_fmt yuv420p \
           -vf "scale=1280:720" \
           -y "$output_file" 2>/dev/null

    # Set proper permissions for DLNA
    sudo chown minidlna:minidlna "$output_file" 2>/dev/null

    echo "Segment ${segment_num} ready: $(basename "$output_file")"

    # Force DLNA rescan
    sudo minidlnad -R 2>/dev/null

    return $?
}

# Main loop
segment_num=1
echo "Press Ctrl+C to stop continuous casting"

while true; do
    if create_segment $segment_num; then
        echo "✅ Segment $segment_num completed and shared via DLNA"
    else
        echo "❌ Failed to create segment $segment_num"
    fi

    # Clean up old segments (keep last 3)
    if [ $segment_num -gt 3 ]; then
        old_segment=$((segment_num - 3))
        old_file="${OUTPUT_BASE}_${old_segment}.mp4"
        if [ -f "$old_file" ]; then
            rm -f "$old_file"
            echo "🗑️  Cleaned up old segment $old_segment"
        fi
    fi

    segment_num=$((segment_num + 1))
done