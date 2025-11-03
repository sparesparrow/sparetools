#!/bin/bash

echo "📊 OpenSSL Build Performance Monitor"
echo "==================================="

LOG_FILE="performance-logs/$(date +%Y%m%d-%H%M%S)-build-times.log"
mkdir -p performance-logs

log_time() {
    local operation="$1"
    local start_time="$2"
    local end_time="$3"
    local duration=$((end_time - start_time))
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $operation | ${duration}s" >> "$LOG_FILE"
    echo "⏱️  $operation: ${duration}s"
}

# Test foundation layer performance
echo "🔐 Testing Foundation Layer Performance..."
cd openssl-conan-base
START=$(date +%s)
conan create . --build=missing >/dev/null 2>&1
END=$(date +%s)
log_time "openssl-conan-base" "$START" "$END"
cd ..

echo "✅ Performance monitoring complete"

