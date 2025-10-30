#!/usr/bin/env python3
"""
GitHub Actions Workflow Monitor
Monitors workflow runs and identifies failed jobs for automated remediation.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

class WorkflowMonitor:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OpenSSL-Tools-Workflow-Monitor'
        }
    
    def get_workflow_runs(self, workflow_id: str = None, status: str = None, limit: int = 10) -> List[Dict]:
        """Get recent workflow runs"""
        url = f"{self.base_url}/actions/runs"
        params = {'per_page': limit}
        
        if workflow_id:
            params['workflow_id'] = workflow_id
        if status:
            params['status'] = status
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('workflow_runs', [])
        except requests.RequestException as e:
            print(f"Error fetching workflow runs: {e}")
            return []
    
    def get_workflow_jobs(self, run_id: int) -> List[Dict]:
        """Get jobs for a specific workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('jobs', [])
        except requests.RequestException as e:
            print(f"Error fetching jobs for run {run_id}: {e}")
            return []
    
    def get_job_logs(self, run_id: int, job_id: int) -> Optional[str]:
        """Get logs for a specific job"""
        url = f"{self.base_url}/actions/jobs/{job_id}/logs"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching logs for job {job_id}: {e}")
            return None
    
    def analyze_failed_jobs(self, hours_back: int = 24) -> List[Dict]:
        """Analyze failed jobs from the last N hours"""
        failed_jobs = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Get all workflow runs
        runs = self.get_workflow_runs(status='completed', limit=50)
        
        for run in runs:
            run_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            # Make cutoff_time timezone-aware for comparison
            cutoff_time_aware = cutoff_time.replace(tzinfo=run_time.tzinfo)
            if run_time < cutoff_time_aware:
                continue
                
            if run['conclusion'] in ['failure', 'cancelled', 'timed_out']:
                jobs = self.get_workflow_jobs(run['id'])
                
                for job in jobs:
                    if job['conclusion'] in ['failure', 'cancelled', 'timed_out']:
                        failed_jobs.append({
                            'run_id': run['id'],
                            'run_number': run['run_number'],
                            'workflow_name': run['name'],
                            'job_id': job['id'],
                            'job_name': job['name'],
                            'conclusion': job['conclusion'],
                            'created_at': run['created_at'],
                            'html_url': run['html_url'],
                            'job_url': job['html_url']
                        })
        
        return failed_jobs
    
    def categorize_failure(self, job_logs: str) -> Dict[str, str]:
        """Categorize failure type based on logs"""
        categories = {
            'dependency_issue': ['package not found', 'module not found', 'import error'],
            'build_error': ['compilation failed', 'build error', 'make failed'],
            'test_failure': ['test failed', 'assertion failed', 'test error'],
            'timeout': ['timeout', 'timed out', 'time limit exceeded'],
            'permission_error': ['permission denied', 'access denied', 'unauthorized'],
            'network_error': ['connection failed', 'network error', 'fetch failed'],
            'resource_error': ['out of memory', 'disk space', 'resource limit'],
            'configuration_error': ['config error', 'invalid configuration', 'missing config']
        }
        
        logs_lower = job_logs.lower()
        detected_categories = []
        
        for category, keywords in categories.items():
            if any(keyword in logs_lower for keyword in keywords):
                detected_categories.append(category)
        
        return {
            'primary_category': detected_categories[0] if detected_categories else 'unknown',
            'all_categories': detected_categories
        }
    
    def generate_failure_report(self, failed_jobs: List[Dict]) -> str:
        """Generate a comprehensive failure report"""
        if not failed_jobs:
            return "✅ No failed jobs found in the specified time period."
        
        report = f"🚨 Workflow Failure Report - {len(failed_jobs)} failed jobs found\n"
        report += "=" * 60 + "\n\n"
        
        # Group by workflow
        by_workflow = {}
        for job in failed_jobs:
            workflow = job['workflow_name']
            if workflow not in by_workflow:
                by_workflow[workflow] = []
            by_workflow[workflow].append(job)
        
        for workflow, jobs in by_workflow.items():
            report += f"📋 Workflow: {workflow}\n"
            report += f"   Failed Jobs: {len(jobs)}\n"
            
            for job in jobs:
                report += f"   • Job: {job['job_name']}\n"
                report += f"     Status: {job['conclusion']}\n"
                report += f"     Run: #{job['run_number']}\n"
                report += f"     URL: {job['job_url']}\n"
                
                # Get logs and categorize failure
                logs = self.get_job_logs(job['run_id'], job['job_id'])
                if logs:
                    categories = self.categorize_failure(logs)
                    report += f"     Category: {categories['primary_category']}\n"
                
                report += "\n"
        
        return report
    
    def suggest_fixes(self, failed_jobs: List[Dict]) -> List[str]:
        """Suggest fixes based on failure patterns"""
        suggestions = []
        
        # Analyze patterns
        failure_categories = {}
        for job in failed_jobs:
            logs = self.get_job_logs(job['run_id'], job['job_id'])
            if logs:
                categories = self.categorize_failure(logs)
                category = categories['primary_category']
                if category not in failure_categories:
                    failure_categories[category] = 0
                failure_categories[category] += 1
        
        # Generate suggestions
        if 'dependency_issue' in failure_categories:
            suggestions.append("🔧 Fix dependency issues: Update package versions, check import paths")
        
        if 'build_error' in failure_categories:
            suggestions.append("🔧 Fix build errors: Check compiler settings, update build scripts")
        
        if 'test_failure' in failure_categories:
            suggestions.append("🔧 Fix test failures: Review test cases, update test data")
        
        if 'timeout' in failure_categories:
            suggestions.append("⏱️ Fix timeouts: Increase timeout limits, optimize build performance")
        
        if 'permission_error' in failure_categories:
            suggestions.append("🔐 Fix permission errors: Check GitHub token permissions, repository settings")
        
        if 'network_error' in failure_categories:
            suggestions.append("🌐 Fix network errors: Add retry logic, check external dependencies")
        
        return suggestions

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor GitHub Actions workflows')
    parser.add_argument('--owner', default='sparesparrow', help='Repository owner')
    parser.add_argument('--repo', default='openssl-tools', help='Repository name')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token")
        sys.exit(1)
    
    monitor = WorkflowMonitor(args.owner, args.repo)
    
    print(f"🔍 Monitoring workflows for {args.owner}/{args.repo}")
    print(f"⏰ Looking back {args.hours} hours...")
    
    # Analyze failed jobs
    failed_jobs = monitor.analyze_failed_jobs(args.hours)
    
    # Generate report
    report = monitor.generate_failure_report(failed_jobs)
    print(report)
    
    # Generate suggestions
    if failed_jobs:
        suggestions = monitor.suggest_fixes(failed_jobs)
        if suggestions:
            print("\n💡 Suggested Fixes:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to {args.output}")

if __name__ == '__main__':
    main()
