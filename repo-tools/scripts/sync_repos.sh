#!/bin/bash

# Script to sync all git repositories in ~/projects
# Pull latest changes and push any local commits

REPOS=(
    "/home/sparrow/projects/1984"
    "/home/sparrow/projects/anthropic-tools"
    "/home/sparrow/projects/awesome-cursor-mpc-server"
    "/home/sparrow/projects/awesome-mcp-servers"
    "/home/sparrow/projects/btc-pay-server"
    "/home/sparrow/projects/bzeed-mobility"
    "/home/sparrow/projects/claude-desktop-debian"
    "/home/sparrow/projects/cliphist-android"
    "/home/sparrow/projects/codemcp"
    "/home/sparrow/projects/cpy"
    "/home/sparrow/projects/cpy-tools"
    "/home/sparrow/projects/crewAI"
    "/home/sparrow/projects/cursor-audio-notifications"
    "/home/sparrow/projects/cursor-rules"
    "/home/sparrow/projects/ddp-rs"
    "/home/sparrow/projects/elevenlabs-agents"
    "/home/sparrow/projects/esp32-bpm-detector"
    "/home/sparrow/projects/extension-template-full"
    "/home/sparrow/projects/extension-template-minimal"
    "/home/sparrow/projects/extension-template-webview"
    "/home/sparrow/projects/flight-rs"
    "/home/sparrow/projects/fuzz-corpora"
    "/home/sparrow/projects/github-events"
    "/home/sparrow/projects/honeybot"
    "/home/sparrow/projects/human-action"
    "/home/sparrow/projects/L1B3RT4S"
    "/home/sparrow/projects/libcurl"
    "/home/sparrow/projects/mcp-cypress-tool"
    "/home/sparrow/projects/mcp-fbs"
    "/home/sparrow/projects/mcp-project-orchestrator"
    "/home/sparrow/projects/mcp-prompts"
    "/home/sparrow/projects/mcp-prompts-aidl"
    "/home/sparrow/projects/mcp-prompts-catalog"
    "/home/sparrow/projects/mcp-prompts-contracts"
    "/home/sparrow/projects/mcp-prompts-esp32"
    "/home/sparrow/projects/mcp-prompts-pg"
    "/home/sparrow/projects/mcp-prompts-rs"
    "/home/sparrow/projects/mcp-prompts-ts"
    "/home/sparrow/projects/mcp-prompts-vscode"
    "/home/sparrow/projects/mcp-router"
    "/home/sparrow/projects/MCPServer.cpp"
    "/home/sparrow/projects/mcp-servers"
    "/home/sparrow/projects/mcp-shell-server"
    "/home/sparrow/projects/mcp-transport-telegram"
    "/home/sparrow/projects/mia"
    "/home/sparrow/projects/NucleusESP32"
    "/home/sparrow/projects/sparetools"
)

echo "Starting repository sync..."

for repo in "${REPOS[@]}"; do
    echo "=========================================="
    echo "Processing: $repo"
    echo "=========================================="

    if [ ! -d "$repo" ]; then
        echo "Repository directory does not exist: $repo"
        continue
    fi

    cd "$repo" || continue

    # Get repo name for display
    repo_name=$(basename "$repo")

    echo "Checking status for $repo_name..."
    git status --porcelain
    status_exit=$?

    # Check if there are uncommitted changes
    if [ $status_exit -ne 0 ]; then
        echo "Warning: git status failed for $repo_name"
        continue
    fi

    # Check for uncommitted changes
    if git status --porcelain | grep -q .; then
        echo "Uncommitted changes found in $repo_name. Skipping sync."
        git status
        continue
    fi

    # Get current branch
    current_branch=$(git branch --show-current)
    echo "Current branch: $current_branch"

    # Fetch latest changes
    echo "Fetching latest changes..."
    if ! git fetch origin; then
        echo "Failed to fetch for $repo_name"
        continue
    fi

    # Check if we're behind origin
    behind_count=$(git rev-list HEAD..origin/"$current_branch" --count 2>/dev/null || echo "0")

    if [ "$behind_count" -gt 0 ]; then
        echo "Pulling $behind_count commits..."
        if ! git pull origin "$current_branch"; then
            echo "Failed to pull for $repo_name"
            continue
        fi
    else
        echo "Already up to date with origin/$current_branch"
    fi

    # Check if we have commits to push
    ahead_count=$(git rev-list origin/"$current_branch"..HEAD --count 2>/dev/null || echo "0")

    if [ "$ahead_count" -gt 0 ]; then
        echo "Pushing $ahead_count commits..."
        if ! git push origin "$current_branch"; then
            echo "Failed to push for $repo_name"
            continue
        fi
    else
        echo "No commits to push"
    fi

    echo "Successfully synced $repo_name"
done

echo "=========================================="
echo "Repository sync completed!"
echo "=========================================="