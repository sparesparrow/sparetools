#!/usr/bin/env python3
"""Simplified CI context server for agent-loop.sh (no MCP dependency)"""
import json
import os
import subprocess
import sys
from typing import Any, Dict, List

def get_workflow_runs(limit: int = 30) -> str:
    """Get recent workflow runs for the repository"""
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--limit", str(limit), "--json", 
             "databaseId,displayTitle,workflowName,status,conclusion,headBranch,createdAt,updatedAt"],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting workflow runs: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_failed_job_logs(run_id: str) -> str:
    """Get logs for failed workflow jobs"""
    try:
        result = subprocess.run(
            ["gh", "run", "view", str(run_id), "--log-failed"],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Failed to get logs for run {run_id}: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_pr_status(pr_number: int) -> str:
    """Get pull request status and checks"""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json",
             "statusCheckRollup,headRefName,baseRefName,mergeable,mergeStateStatus,author,title"],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting PR status: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_recent_commits(limit: int = 15) -> str:
    """Get recent commits on the current branch"""
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-n", str(limit)],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting commits: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_workflow_file(workflow_name: str) -> str:
    """Get the contents of a workflow file"""
    try:
        # Try both enabled and disabled workflows
        for base_path in [".github/workflows", ".github/workflows-disabled"]:
            workflow_path = f"{base_path}/{workflow_name}"
            if os.path.exists(workflow_path):
                with open(workflow_path, 'r') as f:
                    content = f.read()
                return f"Workflow file: {workflow_path}\n\n{content}"
        
        return f"Workflow file not found: {workflow_name}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Simple CLI interface for CI context tools"""
    if len(sys.argv) < 2:
        print("Usage: python3 ci-server-simple.py <tool> [args...]")
        print("Available tools:")
        print("  get_workflow_runs [limit]")
        print("  get_failed_job_logs <run_id>")
        print("  get_pr_status <pr_number>")
        print("  get_recent_commits [limit]")
        print("  get_workflow_file <workflow_name>")
        sys.exit(1)
    
    tool = sys.argv[1]
    
    try:
        if tool == "get_workflow_runs":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            result = get_workflow_runs(limit)
        elif tool == "get_failed_job_logs":
            if len(sys.argv) < 3:
                print("Error: run_id required")
                sys.exit(1)
            result = get_failed_job_logs(sys.argv[2])
        elif tool == "get_pr_status":
            if len(sys.argv) < 3:
                print("Error: pr_number required")
                sys.exit(1)
            result = get_pr_status(int(sys.argv[2]))
        elif tool == "get_recent_commits":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            result = get_recent_commits(limit)
        elif tool == "get_workflow_file":
            if len(sys.argv) < 3:
                print("Error: workflow_name required")
                sys.exit(1)
            result = get_workflow_file(sys.argv[2])
        else:
            print(f"Error: Unknown tool '{tool}'")
            sys.exit(1)
        
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
