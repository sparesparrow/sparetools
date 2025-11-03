#!/bin/bash
# Monitor Integration Workflow Performance
# Usage: ./scripts/monitor-integration-workflow.sh [run-id]

set -e

WORKFLOW_NAME="integration.yml"
LIMIT=${1:-5}

echo "🔍 Monitoring Integration Workflow Performance"
echo "================================================"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install it first."
    echo "   Visit: https://cli.github.com/"
    exit 1
fi

# Get recent workflow runs
echo "📊 Recent Workflow Runs:"
echo ""
gh run list --workflow="$WORKFLOW_NAME" --limit "$LIMIT" --json databaseId,status,conclusion,createdAt,updatedAt,duration \
  | jq -r '.[] | "\(.databaseId) | \(.status) | \(.conclusion // "N/A") | \(.duration/1000/60 | floor)min | \(.createdAt)"' \
  | awk 'BEGIN {printf "%-12s %-10s %-12s %-8s %s\n", "Run ID", "Status", "Conclusion", "Duration", "Created At"} 
         {print}' \
  | column -t -s '|'

echo ""
echo ""

# If specific run ID provided, get detailed info
if [ -n "$1" ] && [ "$1" != "5" ]; then
    RUN_ID=$1
    echo "📋 Detailed Information for Run $RUN_ID:"
    echo ""
    
    # Get run details
    gh run view "$RUN_ID" --workflow="$WORKFLOW_NAME" --json name,status,conclusion,createdAt,updatedAt,duration,headBranch,event,workflowName \
      | jq -r '"Status: \(.status)\nConclusion: \(.conclusion // "N/A")\nDuration: \(.duration/1000/60) minutes\nBranch: \(.headBranch)\nEvent: \(.event)"'
    
    echo ""
    echo "📝 Job Summary:"
    gh run view "$RUN_ID" --workflow="$WORKFLOW_NAME" --log | grep -E "^(##|✅|❌)" | head -20
fi

echo ""
echo "💡 Tips:"
echo "  - View full run: gh run view <run-id> --log"
echo "  - Watch live run: gh run watch"
echo "  - Download artifacts: gh run download <run-id>"
echo ""
echo "📈 Performance Targets:"
echo "  - First run (no cache): 15-20 minutes"
echo "  - Cached run: 8-12 minutes (40-60% improvement)"
echo "  - Cache hit rate: >70%"
