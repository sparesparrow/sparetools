#!/usr/bin/env python3
"""
Unified Workflow Manager
Combines existing workflow automation tools with MCP server capabilities for intelligent workflow analysis and fixing.
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from the same package
from .monitor import WorkflowMonitor
from .recovery import WorkflowRecovery
from .health_check import WorkflowHealthChecker
from .manager import WorkflowManager

# Import MCP GitHub Workflow Fixer
from ..ai_agents.workflow_fixer import GitHubWorkflowFixer


class UnifiedWorkflowManager:
    """
    Unified interface that combines existing workflow automation tools with MCP server capabilities.
    Provides intelligent analysis, monitoring, and automated fixing of GitHub workflows.
    """
    
    def __init__(self, repo: str, token: str = None):
        """
        Initialize the unified workflow manager.
        
        Args:
            repo: Repository in format 'owner/repo'
            token: GitHub token (optional, will use GITHUB_TOKEN env var if not provided)
        """
        self.repo = repo
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        if not self.token:
            raise ValueError("GitHub token is required (GITHUB_TOKEN env var or token parameter)")
        
        # Parse repository owner and name
        if '/' not in repo:
            raise ValueError("Repository must be in format 'owner/repo'")
        
        self.repo_owner, self.repo_name = repo.split('/', 1)
        
        # Initialize existing components
        self.legacy_manager = WorkflowManager(self.repo_owner, self.repo_name, self.token)
        self.monitor = WorkflowMonitor(self.repo_owner, self.repo_name, self.token)
        self.recovery = WorkflowRecovery(self.repo_owner, self.repo_name, self.token)
        self.health_checker = WorkflowHealthChecker(self.repo_owner, self.repo_name, self.token)
        
        # Initialize MCP client
        self.mcp_fixer = GitHubWorkflowFixer(repo, self.token)
    
    async def analyze_workflows(self, limit: int = 20) -> str:
        """
        Analyze workflow failures using MCP server's intelligent analysis.
        
        Args:
            limit: Maximum number of workflow runs to analyze
            
        Returns:
            Detailed analysis report with suggested fixes
        """
        try:
            async with self.mcp_fixer as fixer:
                # Get workflow runs
                runs = await fixer.get_workflow_runs(limit=limit)
                
                # Analyze failures
                analysis = await fixer.analyze_workflow_failures(runs)
                
                return analysis.report
        except Exception as e:
            return f"Analysis failed: {e}"
    
    def monitor_status(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Monitor current workflow status using existing tools.
        
        Args:
            hours_back: Number of hours to look back for status
            
        Returns:
            Status information dictionary
        """
        try:
            return self.legacy_manager.check_status(hours_back)
        except Exception as e:
            return {"error": f"Status monitoring failed: {e}"}
    
    async def fix_issues(self, dry_run: bool = True, max_fixes: int = 3) -> str:
        """
        Apply automated fixes to common workflow issues using MCP server.
        
        Args:
            dry_run: If True, only show what would be changed
            max_fixes: Maximum number of fixes to apply
            
        Returns:
            Results of fix application
        """
        try:
            async with self.mcp_fixer as fixer:
                runs = await fixer.get_workflow_runs(limit=20)
                analysis = await fixer.analyze_workflow_failures(runs)
                
                if not analysis.suggested_fixes:
                    return "No automated fixes available for the detected issues."
                
                results = []
                fixes_applied = 0
                
                for fix in analysis.suggested_fixes:
                    if fixes_applied >= max_fixes:
                        break
                    
                    result = await fixer.apply_fix(fix, dry_run=dry_run)
                    results.append(result)
                    fixes_applied += 1
                
                # Format results
                output = f"## Fix Application Results\n\n"
                output += f"**Mode:** {'Dry Run' if dry_run else 'Applied'}\n"
                output += f"**Fixes Processed:** {fixes_applied}\n\n"
                
                for i, result in enumerate(results, 1):
                    output += f"### Fix {i}: {result['fix']}\n"
                    output += f"**File:** {result['file']}\n"
                    output += f"**Status:** {result['action']}\n"
                    if 'changes' in result:
                        output += f"```\n{result['changes']}\n```\n\n"
                    elif 'message' in result:
                        output += f"{result['message']}\n\n"
                
                if dry_run:
                    output += "\n*Run with dry_run=False to apply these changes*"
                
                return output
        except Exception as e:
            return f"Failed to apply fixes: {e}"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check using existing tools.
        
        Returns:
            Health check results
        """
        try:
            return self.health_checker.comprehensive_health_check()
        except Exception as e:
            return {"error": f"Health check failed: {e}"}
    
    async def recover_failed(self, max_reruns: int = 5) -> str:
        """
        Recover failed workflows using MCP server's rerun capabilities.
        
        Args:
            max_reruns: Maximum number of workflows to rerun
            
        Returns:
            Results of workflow reruns
        """
        try:
            async with self.mcp_fixer as fixer:
                runs = await fixer.get_workflow_runs(limit=20)
                failed_runs = [run for run in runs if run.is_failed][:max_reruns]
                
                if not failed_runs:
                    return "No failed workflows found to rerun."
                
                results = []
                for run in failed_runs:
                    result = await fixer.trigger_workflow_rerun(run.id)
                    results.append(result)
                
                # Format results
                output = f"## Workflow Rerun Results\n\n"
                output += f"**Total Reruns Attempted:** {len(results)}\n\n"
                
                successful = 0
                for result in results:
                    if result['success']:
                        successful += 1
                        output += f"SUCCESS **Run {result['run_id']}:** {result['message']}\n"
                    else:
                        output += f"FAILED **Run {result['run_id']}:** {result['error']}\n"
                
                output += f"\n**Success Rate:** {successful}/{len(results)}\n"
                
                return output
        except Exception as e:
            return f"Failed to rerun workflows: {e}"
    
    async def analyze_and_fix(self, limit: int = 20, dry_run: bool = True) -> str:
        """
        Comprehensive analysis and fixing workflow.
        Combines MCP analysis with legacy monitoring for complete coverage.
        
        Args:
            limit: Maximum number of workflow runs to analyze
            dry_run: If True, only show what would be changed
            
        Returns:
            Combined analysis and fix report
        """
        report = f"# Unified Workflow Analysis Report\n\n"
        report += f"**Repository:** {self.repo}\n"
        report += f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        
        # Get MCP analysis
        report += "## MCP Intelligent Analysis\n\n"
        mcp_analysis = await self.analyze_workflows(limit)
        report += mcp_analysis + "\n\n"
        
        # Get legacy status
        report += "## Legacy Status Monitoring\n\n"
        status = self.monitor_status()
        if isinstance(status, dict) and "error" not in status:
            report += f"Status check completed successfully.\n\n"
        else:
            report += f"Status check: {status}\n\n"
        
        # Get health check
        report += "## Health Check Results\n\n"
        health = self.health_check()
        if isinstance(health, dict) and "error" not in health:
            report += "Health check completed successfully.\n\n"
        else:
            report += f"Health check: {health}\n\n"
        
        # Apply fixes if requested
        if not dry_run:
            report += "## Applied Fixes\n\n"
            fixes = await self.fix_issues(dry_run=False, max_fixes=3)
            report += fixes + "\n\n"
        
        return report


async def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description="Unified Workflow Manager")
    parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo'")
    parser.add_argument("--token", help="GitHub token (optional, uses GITHUB_TOKEN env var)")
    parser.add_argument("--action", choices=["analyze", "monitor", "fix", "health", "recover", "analyze-and-fix"], 
                       default="analyze", help="Action to perform")
    parser.add_argument("--limit", type=int, default=20, help="Maximum workflow runs to analyze")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode (default: True)")
    parser.add_argument("--max-fixes", type=int, default=3, help="Maximum fixes to apply")
    parser.add_argument("--max-reruns", type=int, default=5, help="Maximum workflows to rerun")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    try:
        manager = UnifiedWorkflowManager(args.repo, args.token)
        
        if args.action == "analyze":
            result = await manager.analyze_workflows(args.limit)
        elif args.action == "monitor":
            result = manager.monitor_status()
        elif args.action == "fix":
            result = await manager.fix_issues(args.dry_run, args.max_fixes)
        elif args.action == "health":
            result = manager.health_check()
        elif args.action == "recover":
            result = await manager.recover_failed(args.max_reruns)
        elif args.action == "analyze-and-fix":
            result = await manager.analyze_and_fix(args.limit, args.dry_run)
        else:
            result = "Unknown action"
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(str(result))
            print(f"Results written to {args.output}")
        else:
            print(result)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
