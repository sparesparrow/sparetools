#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def run_command(cmd: List[str], cwd: Path = None, capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def sync_repository(repo_dir: Path) -> Tuple[str, bool]:
    """Sync a single repository. Returns (status_message, success)"""
    repo_name = repo_dir.name

    print(f"\n{Colors.BLUE}=== Syncing: {repo_name} ==={Colors.NC}")
    print(f"{Colors.BLUE}Path: {repo_dir}{Colors.NC}")

    # Check if directory exists and is accessible
    if not repo_dir.exists():
        return f"{Colors.RED}❌ Directory does not exist{Colors.NC}", False

    # Change to repository directory
    original_cwd = os.getcwd()
    try:
        os.chdir(repo_dir)
    except PermissionError:
        return f"{Colors.RED}❌ Cannot access directory{Colors.NC}", False

    try:
        # Check if this is a valid git repository
        returncode, _, _ = run_command(["git", "rev-parse", "--git-dir"])
        if returncode != 0:
            return f"{Colors.RED}❌ Not a valid git repository{Colors.NC}", False

        # Check current branch
        returncode, stdout, _ = run_command(["git", "branch", "--show-current"])
        current_branch = stdout.strip() if returncode == 0 else "main"

        # Check if remote exists
        returncode, _, _ = run_command(["git", "remote", "get-url", "origin"])
        if returncode != 0:
            return f"{Colors.YELLOW}⚠️  No remote 'origin' found{Colors.NC}", True

        # Check for uncommitted changes
        returncode1, _, _ = run_command(["git", "diff", "--quiet"])
        returncode2, _, _ = run_command(["git", "diff", "--staged", "--quiet"])
        has_changes = returncode1 != 0 or returncode2 != 0

        stashed = False
        if has_changes:
            print(f"{Colors.YELLOW}⚠️  Uncommitted changes - stashing temporarily{Colors.NC}")
            returncode, _, _ = run_command(["git", "stash", "push", "-m", "Auto-stash for sync"])
            if returncode == 0:
                stashed = True
                print(f"{Colors.GREEN}✓ Changes stashed{Colors.NC}")
            else:
                return f"{Colors.RED}❌ Failed to stash changes{Colors.NC}", False

        # Fetch from remote
        print("📡 Fetching from remote...")
        returncode, _, stderr = run_command(["git", "fetch", "origin"])
        if returncode != 0:
            if stashed:
                run_command(["git", "stash", "pop"])
            return f"{Colors.RED}❌ Failed to fetch: {stderr.strip()}{Colors.NC}", False

        print(f"{Colors.GREEN}✓ Fetch successful{Colors.NC}")

        # Check ahead/behind status
        returncode, stdout, _ = run_command([
            "git", "rev-list", "--left-right", "--count",
            "HEAD...origin/" + current_branch
        ])
        if returncode == 0:
            ahead_behind = stdout.strip().split()
            ahead = int(ahead_behind[0]) if len(ahead_behind) > 0 else 0
            behind = int(ahead_behind[1]) if len(ahead_behind) > 1 else 0
        else:
            ahead, behind = 0, 0

        if ahead > 0 and behind > 0:
            if stashed:
                run_command(["git", "stash", "pop"])
            return f"{Colors.YELLOW}⚠️  Diverged: {ahead} ahead, {behind} behind (manual merge required){Colors.NC}", False
        elif behind > 0:
            print(f"⬇️  Pulling {behind} commits...")
            returncode, _, stderr = run_command(["git", "pull", "--ff-only", "origin", current_branch])
            if returncode == 0:
                result = f"{Colors.GREEN}✅ Successfully pulled changes{Colors.NC}"
            else:
                result = f"{Colors.RED}❌ Failed to pull: {stderr.strip()}{Colors.NC}"
        elif ahead > 0:
            print(f"⬆️  Pushing {ahead} commits...")
            returncode, _, stderr = run_command(["git", "push", "origin", current_branch])
            if returncode == 0:
                result = f"{Colors.GREEN}✅ Successfully pushed changes{Colors.NC}"
            else:
                result = f"{Colors.RED}❌ Failed to push: {stderr.strip()}{Colors.NC}"
        else:
            result = f"{Colors.GREEN}✅ Already up to date{Colors.NC}"

        # Restore stashed changes
        if stashed:
            print("🔄 Restoring stashed changes...")
            returncode, _, _ = run_command(["git", "stash", "pop"])
            if returncode == 0:
                print(f"{Colors.GREEN}✅ Restored stashed changes{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}⚠️  Could not restore stashed changes{Colors.NC}")

        return result, True

    finally:
        os.chdir(original_cwd)

def main():
    print(f"{Colors.BLUE}🚀 Starting repository sync for all repos under ~/projects{Colors.NC}")

    # Find all git repositories
    projects_dir = Path.home() / "projects"
    repo_paths = []

    try:
        for git_dir in projects_dir.rglob(".git"):
            if git_dir.is_dir():
                repo_paths.append(git_dir.parent)
    except PermissionError:
        print(f"{Colors.YELLOW}⚠️  Some directories are not accessible due to permissions{Colors.NC}")

    print(f"Found {len(repo_paths)} repositories to process")

    # Counters
    total_repos = 0
    up_to_date = 0
    pulled_changes = 0
    pushed_changes = 0
    conflicts = 0
    errors = 0

    # Process each repository
    for repo_dir in sorted(repo_paths):
        total_repos += 1
        status_msg, success = sync_repository(repo_dir)

        if "Already up to date" in status_msg:
            up_to_date += 1
        elif "Successfully pulled changes" in status_msg:
            pulled_changes += 1
        elif "Successfully pushed changes" in status_msg:
            pushed_changes += 1
        elif "Diverged" in status_msg:
            conflicts += 1
        elif not success:
            errors += 1

        print(status_msg)

        # Progress indicator
        if total_repos % 10 == 0:
            print(f"{Colors.BLUE}Processed {total_repos}/{len(repo_paths)} repositories...{Colors.NC}")

    # Summary
    print(f"\n{Colors.BLUE}=== SYNC SUMMARY ==={Colors.NC}")
    print(f"Total repositories processed: {total_repos}")
    print(f"{Colors.GREEN}✅ Up to date: {up_to_date}{Colors.NC}")
    print(f"{Colors.GREEN}⬇️  Pulled changes: {pulled_changes}{Colors.NC}")
    print(f"{Colors.GREEN}⬆️  Pushed changes: {pushed_changes}{Colors.NC}")

    if conflicts > 0:
        print(f"{Colors.YELLOW}⚠️  Conflicts/Diverged: {conflicts}{Colors.NC}")

    if errors > 0:
        print(f"{Colors.RED}❌ Errors: {errors}{Colors.NC}")

    print(f"\n{Colors.BLUE}🎉 Repository sync complete!{Colors.NC}")

if __name__ == "__main__":
    main()