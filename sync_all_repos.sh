#!/bin/bash

# Script to sync all git repositories under ~/projects
# Handles fetch, merge/pull, and reports status
# Automatically stashes uncommitted changes during sync

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
total_repos=0
up_to_date=0
pulled_changes=0
pushed_changes=0
conflicts=0
errors=0

# Function to sync a single repository
sync_repo() {
    local repo_path="$1"
    local repo_dir="$(dirname "$repo_path")"
    local repo_name="$(basename "$repo_dir")"

    echo -e "\n${BLUE}=== Syncing: $repo_name ===${NC}"
    echo -e "${BLUE}Path: $repo_dir${NC}"

    cd "$repo_dir" 2>/dev/null || {
        echo -e "${RED}❌ Cannot access directory: $repo_dir${NC}"
        ((errors++))
        return
    }

    # Check if this is a valid git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Not a valid git repository: $repo_dir${NC}"
        ((errors++))
        return
    fi

    ((total_repos++))

    # Check current branch
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || echo "main")

    # Check if remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  No remote 'origin' found for $repo_name${NC}"
        return
    fi

    # Check for uncommitted changes and handle them
    local has_changes=false
    if ! git diff --quiet 2>/dev/null || ! git diff --staged --quiet 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Uncommitted changes in $repo_name - stashing temporarily${NC}"
        has_changes=true
        if git stash push -m "Auto-stash for sync" 2>/dev/null; then
            echo -e "${GREEN}✓ Changes stashed${NC}"
        else
            echo -e "${RED}❌ Failed to stash changes in $repo_name${NC}"
            ((errors++))
            return
        fi
    fi

    # Fetch from remote
    echo "📡 Fetching from remote..."
    if git fetch origin 2>/dev/null; then
        echo -e "${GREEN}✓ Fetch successful${NC}"
    else
        echo -e "${RED}❌ Failed to fetch from remote for $repo_name${NC}"
        # Restore stashed changes if any
        if [ "$has_changes" = true ]; then
            git stash pop 2>/dev/null || true
        fi
        ((errors++))
        return
    fi

    # Check if we're ahead, behind, or diverged
    local ahead_behind
    ahead_behind=$(git rev-list --left-right --count HEAD...origin/"$current_branch" 2>/dev/null || echo "0 0")

    local ahead=$(echo "$ahead_behind" | cut -d' ' -f1)
    local behind=$(echo "$ahead_behind" | cut -d' ' -f2)

    if [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Diverged: $ahead commits ahead, $behind commits behind${NC}"
        echo "   Manual merge required for $repo_name"
        ((conflicts++))
    elif [ "$behind" -gt 0 ]; then
        echo "⬇️  Pulling $behind commits..."
        if git pull --ff-only origin "$current_branch" 2>/dev/null; then
            echo -e "${GREEN}✅ Successfully pulled changes in $repo_name${NC}"
            ((pulled_changes++))
        else
            echo -e "${RED}❌ Failed to pull changes in $repo_name${NC}"
            ((errors++))
        fi
    elif [ "$ahead" -gt 0 ]; then
        echo "⬆️  Pushing $ahead commits..."
        if git push origin "$current_branch" 2>/dev/null; then
            echo -e "${GREEN}✅ Successfully pushed changes in $repo_name${NC}"
            ((pushed_changes++))
        else
            echo -e "${RED}❌ Failed to push changes in $repo_name${NC}"
            ((errors++))
        fi
    else
        echo -e "${GREEN}✅ Already up to date: $repo_name${NC}"
        ((up_to_date++))
    fi

    # Restore stashed changes if any
    if [ "$has_changes" = true ]; then
        echo "🔄 Restoring stashed changes..."
        if git stash pop 2>/dev/null; then
            echo -e "${GREEN}✅ Restored stashed changes in $repo_name${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not restore stashed changes in $repo_name${NC}"
        fi
    fi
}

# Main script
echo -e "${BLUE}🚀 Starting repository sync for all repos under ~/projects${NC}"
echo -e "${BLUE}This may take several minutes depending on the number of repositories...${NC}"

# Get list of repositories and sync each one
find ~/projects -name ".git" -type d 2>/dev/null | while read -r repo_path; do
    sync_repo "$repo_path"
done

# Summary
echo -e "\n${BLUE}=== SYNC SUMMARY ===${NC}"
echo "Total repositories processed: $total_repos"
echo -e "${GREEN}✅ Up to date: $up_to_date${NC}"
echo -e "${GREEN}⬇️  Pulled changes: $pulled_changes${NC}"
echo -e "${GREEN}⬆️  Pushed changes: $pushed_changes${NC}"

if [ $conflicts -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Conflicts/Diverged: $conflicts${NC}"
fi

if [ $errors -gt 0 ]; then
    echo -e "${RED}❌ Errors: $errors${NC}"
fi

echo -e "\n${BLUE}🎉 Repository sync complete!${NC}"