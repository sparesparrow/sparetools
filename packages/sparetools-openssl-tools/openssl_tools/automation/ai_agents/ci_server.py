#!/usr/bin/env python3
"""MCP server for CI/CD context in agent-loop.sh"""
import asyncio
import json
import os
import subprocess
import sys
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
server = Server("openssl-ci")

@server.list_tools()
async def list_tools() -> list[Any]:
    """List available MCP tools for CI context"""
    return [
        {
            "name": "get_workflow_runs",
            "description": "Get recent workflow runs for the repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "default": 30}
                }
            }
        },
        {
            "name": "get_failed_job_logs",
            "description": "Get logs for failed workflow jobs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "run_id": {"type": "string"}
                },
                "required": ["run_id"]
            }
        },
        {
            "name": "get_pr_status",
            "description": "Get pull request status and checks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pr_number": {"type": "number"}
                },
                "required": ["pr_number"]
            }
        },
        {
            "name": "get_recent_commits",
            "description": "Get recent commits on the current branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "default": 15}
                }
            }
        },
        {
            "name": "get_workflow_file",
            "description": "Get the contents of a workflow file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"}
                },
                "required": ["workflow_name"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[Any]:
    """Execute MCP tool calls"""
    try:
        if name == "get_workflow_runs":
            limit = arguments.get("limit", 30)
            result = subprocess.run(
                ["gh", "run", "list", "--limit", str(limit), "--json", 
                 "databaseId,displayTitle,workflowName,status,conclusion,headBranch,createdAt,updatedAt"],
                capture_output=True, text=True, check=True
            )
            return [{"type": "text", "text": result.stdout}]
        
        elif name == "get_failed_job_logs":
            run_id = arguments["run_id"]
            result = subprocess.run(
                ["gh", "run", "view", str(run_id), "--log-failed"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return [{"type": "text", "text": result.stdout}]
            else:
                return [{"type": "text", "text": f"Failed to get logs for run {run_id}: {result.stderr}"}]
        
        elif name == "get_pr_status":
            pr_number = arguments["pr_number"]
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json",
                 "statusCheckRollup,headRefName,baseRefName,mergeable,mergeStateStatus,author,title"],
                capture_output=True, text=True, check=True
            )
            return [{"type": "text", "text": result.stdout}]
        
        elif name == "get_recent_commits":
            limit = arguments.get("limit", 15)
            result = subprocess.run(
                ["git", "log", f"--oneline", f"-n", str(limit)],
                capture_output=True, text=True, check=True
            )
            return [{"type": "text", "text": result.stdout}]
        
        elif name == "get_workflow_file":
            workflow_name = arguments["workflow_name"]
            # Try both enabled and disabled workflows
            for base_path in [".github/workflows", ".github/workflows-disabled"]:
                workflow_path = f"{base_path}/{workflow_name}"
                if os.path.exists(workflow_path):
                    with open(workflow_path, 'r') as f:
                        content = f.read()
                    return [{"type": "text", "text": f"Workflow file: {workflow_path}\n\n{content}"}]
            
            return [{"type": "text", "text": f"Workflow file not found: {workflow_name}"}]
        
        else:
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
            
    except subprocess.CalledProcessError as e:
        return [{"type": "text", "text": f"Error executing {name}: {e.stderr}"}]
    except Exception as e:
        return [{"type": "text", "text": f"Error: {str(e)}"}]

async def main():
    """Main entry point for MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

