#!/bin/bash
# Monitor workflow runs after PR #5 improvements
# Usage: ./scripts/monitor-pr5-workflows.sh [workflow-run-id]

set -e

WORKFLOW_RUN_ID="${1:-19021125013}"
REPO="sparesparrow/sparetools"

echo "🔍 Monitoring workflow run: $WORKFLOW_RUN_ID"
echo "Repository: $REPO"
echo ""

# Get workflow details
RUN_INFO=$(gh run view "$WORKFLOW_RUN_ID" --json status,conclusion,name,headBranch,event,createdAt,updatedAt,url)

STATUS=$(echo "$RUN_INFO" | jq -r '.status')
CONCLUSION=$(echo "$RUN_INFO" | jq -r '.conclusion // "in-progress"')
NAME=$(echo "$RUN_INFO" | jq -r '.name')
BRANCH=$(echo "$RUN_INFO" | jq -r '.headBranch')
EVENT=$(echo "$RUN_INFO" | jq -r '.event')
URL=$(echo "$RUN_INFO" | jq -r '.url')

echo "📊 Workflow Status"
echo "=================="
echo "Name: $NAME"
echo "Branch: $BRANCH"
echo "Event: $EVENT"
echo "Status: $STATUS"
echo "Conclusion: $CONCLUSION"
echo "URL: $URL"
echo ""

# Get job statuses
echo "📋 Job Status"
echo "============"
gh run view "$WORKFLOW_RUN_ID" --json jobs --jq '.jobs[] | "\(.name): \(.status) \(.conclusion // "")"' | while read -r line; do
  if [[ "$line" == *"completed"* && "$line" == *"success"* ]]; then
    echo "  ✅ $line"
  elif [[ "$line" == *"completed"* && "$line" == *"failure"* ]]; then
    echo "  ❌ $line"
  elif [[ "$line" == *"in_progress"* ]]; then
    echo "  🔄 $line"
  elif [[ "$line" == *"queued"* ]]; then
    echo "  ⏳ $line"
  else
    echo "  ℹ️  $line"
  fi
done

echo ""

# Check for build-test jobs specifically
echo ""
echo "🔨 Build Test Jobs Status"
echo "========================"
gh run view "$WORKFLOW_RUN_ID" --json jobs --jq '.jobs[] | select(.name | contains("build-test") or contains("Build")) | "\(.name): \(.status) \(.conclusion // "")"' | while read -r line; do
  if [[ "$line" == *"completed"* && "$line" == *"success"* ]]; then
    echo "  ✅ $line"
  elif [[ "$line" == *"completed"* && "$line" == *"failure"* ]]; then
    echo "  ❌ $line"
  elif [[ "$line" == *"in_progress"* ]]; then
    echo "  🔄 $line"
  else
    echo "  ℹ️  $line"
  fi
done

# Get timing information if available
echo "⏱️  Timing"
echo "=========="
CREATED=$(echo "$RUN_INFO" | jq -r '.createdAt')
UPDATED=$(echo "$RUN_INFO" | jq -r '.updatedAt')
echo "Started: $CREATED"
echo "Last updated: $UPDATED"

# Calculate duration if completed
if [ "$STATUS" == "completed" ]; then
  echo ""
  echo "✅ Workflow completed with status: $CONCLUSION"
  if [ "$CONCLUSION" != "success" ]; then
    echo ""
    echo "⚠️  Workflow did not succeed. Check logs:"
    echo "   gh run view $WORKFLOW_RUN_ID --log"
  fi
else
  echo ""
  echo "🔄 Workflow still running. Check again later:"
  echo "   ./scripts/monitor-pr5-workflows.sh $WORKFLOW_RUN_ID"
fi

echo ""
echo "📖 View on GitHub: $URL"
