#!/bin/bash
# Workflow Performance Monitoring Script
# Monitors cache hit rates, build times, and performance trends

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$REPO_DIR/build_results"
mkdir -p "$OUTPUT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Workflow Performance Monitor ===${NC}"
echo ""

# Function to get workflow runs
get_workflow_runs() {
    local workflow=$1
    local limit=${2:-10}
    gh run list --workflow="$workflow" --limit="$limit" --json databaseId,status,conclusion,createdAt,displayTitle
}

# Function to analyze cache effectiveness
analyze_cache() {
    local run_id=$1
    echo -e "${BLUE}Analyzing cache for run $run_id...${NC}"
    
    # Check for cache hits
    local cache_hits=$(gh run view "$run_id" --log 2>/dev/null | grep -c "Cache restored from key" 2>/dev/null | head -1 || echo "0")
    local cache_misses=$(gh run view "$run_id" --log 2>/dev/null | grep -c "Cache not found" 2>/dev/null | head -1 || echo "0")
    local cache_saves=$(gh run view "$run_id" --log 2>/dev/null | grep -c "Saved cache" 2>/dev/null | head -1 || echo "0")
    
    # Clean up any newlines
    cache_hits=$(echo "$cache_hits" | tr -d '\n' | head -1)
    cache_misses=$(echo "$cache_misses" | tr -d '\n' | head -1)
    cache_saves=$(echo "$cache_saves" | tr -d '\n' | head -1)
    
    echo "  Cache hits: $cache_hits"
    echo "  Cache misses: $cache_misses"
    echo "  Cache saves: $cache_saves"
    
    if [ "$cache_hits" -gt 0 ]; then
        echo -e "${GREEN}  ✓ Cache is being used effectively${NC}"
    else
        echo -e "${YELLOW}  ⚠ No cache hits detected${NC}"
    fi
}

# Function to extract build timing
extract_build_timing() {
    local run_id=$1
    echo -e "${BLUE}Extracting build timing for run $run_id...${NC}"
    
    # Look for timing information in logs
    local timing=$(gh run view "$run_id" --log 2>/dev/null | grep -i "build.*completed\|duration\|minutes\|seconds" | head -5)
    
    if [ -n "$timing" ]; then
        echo "  Found timing information:"
        echo "$timing" | sed 's/^/    /'
    else
        echo -e "${YELLOW}  ⚠ No timing information found${NC}"
    fi
}

# Function to check workflow duration
check_workflow_duration() {
    local run_id=$1
    local run_info=$(gh run view "$run_id" --json startedAt,updatedAt 2>/dev/null)
    
    if [ -n "$run_info" ]; then
        local started=$(echo "$run_info" | jq -r '.startedAt')
        local updated=$(echo "$run_info" | jq -r '.updatedAt')
        
        if [ "$started" != "null" ] && [ "$updated" != "null" ]; then
            # Calculate duration (simple approach)
            echo "  Run duration: Check GitHub UI for exact timing"
        fi
    fi
}

# Main analysis function
analyze_workflow() {
    local workflow=$1
    local name=$2
    
    echo -e "${BLUE}=== Analyzing $name ===${NC}"
    
    local runs=$(get_workflow_runs "$workflow" 5)
    local run_count=$(echo "$runs" | jq 'length')
    
    if [ "$run_count" -eq 0 ]; then
        echo -e "${YELLOW}  No runs found for $workflow${NC}"
        return
    fi
    
    echo "  Found $run_count recent runs"
    
    # Analyze each run
    for i in $(seq 0 $((run_count - 1))); do
        local run_id=$(echo "$runs" | jq -r ".[$i].databaseId")
        local status=$(echo "$runs" | jq -r ".[$i].status")
        local conclusion=$(echo "$runs" | jq -r ".[$i].conclusion")
        
        echo ""
        echo -e "${BLUE}Run $run_id ($status/$conclusion)${NC}"
        
        if [ "$status" == "completed" ]; then
            analyze_cache "$run_id"
            extract_build_timing "$run_id"
            check_workflow_duration "$run_id"
        else
            echo "  Run still in progress, skipping detailed analysis"
        fi
    done
    
    echo ""
}

# Generate performance report
generate_report() {
    local report_file="$OUTPUT_DIR/performance-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << 'EOF'
# Workflow Performance Report

Generated: $(date)

## Summary

This report provides insights into workflow performance, cache effectiveness, and build times.

## CI Workflow Analysis

EOF

    echo "Report generated: $report_file"
}

# Main execution
main() {
    echo "Monitoring workflows..."
    echo ""
    
    # Analyze CI workflow
    analyze_workflow "ci.yml" "CI - Build and Test"
    
    # Analyze publish workflow
    analyze_workflow "publish.yml" "Publish Packages"
    
    # Analyze nightly workflow
    analyze_workflow "nightly.yml" "Nightly Comprehensive Testing"
    
    # Analyze security workflow
    analyze_workflow "security.yml" "Security Scanning & Compliance"
    
    echo ""
    echo -e "${GREEN}=== Analysis Complete ===${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Check GitHub Actions UI for detailed logs"
    echo "  2. Review cache hit rates in workflow summaries"
    echo "  3. Monitor build timing in step summaries"
    echo "  4. Compare performance before/after optimizations"
}

# Run main function
main "$@"
