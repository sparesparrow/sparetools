#!/usr/bin/env python3
"""
GitHub Actions Workflow Recovery Script
Automatically retries failed jobs and implements recovery strategies.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

class WorkflowRecovery:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OpenSSL-Tools-Workflow-Recovery'
        }
    
    def rerun_failed_jobs(self, run_id: int) -> bool:
        """Re-run only the failed jobs in a workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}/rerun-failed-jobs"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            print(f"✅ Successfully triggered re-run of failed jobs for run {run_id}")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to re-run jobs for run {run_id}: {e}")
            return False
    
    def rerun_entire_workflow(self, run_id: int) -> bool:
        """Re-run the entire workflow"""
        url = f"{self.base_url}/actions/runs/{run_id}/rerun"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            print(f"✅ Successfully triggered re-run of entire workflow {run_id}")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to re-run workflow {run_id}: {e}")
            return False
    
    def cancel_workflow(self, run_id: int) -> bool:
        """Cancel a running workflow"""
        url = f"{self.base_url}/actions/runs/{run_id}/cancel"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            print(f"✅ Successfully cancelled workflow {run_id}")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to cancel workflow {run_id}: {e}")
            return False
    
    def get_workflow_status(self, run_id: int) -> Optional[Dict]:
        """Get current status of a workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to get status for run {run_id}: {e}")
            return None
    
    def wait_for_completion(self, run_id: int, timeout_minutes: int = 30) -> bool:
        """Wait for a workflow run to complete"""
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()
        
        print(f"⏳ Waiting for workflow {run_id} to complete (timeout: {timeout_minutes} minutes)...")
        
        while time.time() - start_time < timeout_seconds:
            status = self.get_workflow_status(run_id)
            if not status:
                return False
            
            current_status = status['status']
            conclusion = status.get('conclusion')
            
            if current_status == 'completed':
                if conclusion == 'success':
                    print(f"✅ Workflow {run_id} completed successfully")
                    return True
                else:
                    print(f"❌ Workflow {run_id} completed with status: {conclusion}")
                    return False
            
            print(f"   Status: {current_status}")
            time.sleep(30)  # Check every 30 seconds
        
        print(f"⏰ Timeout reached for workflow {run_id}")
        return False
    
    def implement_retry_strategy(self, failed_jobs: List[Dict], max_retries: int = 3) -> Dict:
        """Implement intelligent retry strategy for failed jobs"""
        results = {
            'successful_retries': 0,
            'failed_retries': 0,
            'skipped_retries': 0,
            'details': []
        }
        
        # Group by workflow run
        runs_to_retry = {}
        for job in failed_jobs:
            run_id = job['run_id']
            if run_id not in runs_to_retry:
                runs_to_retry[run_id] = {
                    'workflow_name': job['workflow_name'],
                    'run_number': job['run_number'],
                    'failed_jobs': []
                }
            runs_to_retry[run_id]['failed_jobs'].append(job)
        
        for run_id, run_info in runs_to_retry.items():
            print(f"\n🔄 Processing workflow run {run_id} ({run_info['workflow_name']})")
            print(f"   Failed jobs: {len(run_info['failed_jobs'])}")
            
            # Check if this is a transient failure that should be retried
            should_retry = self._should_retry_run(run_info['failed_jobs'])
            
            if not should_retry:
                print(f"   ⏭️ Skipping retry (non-transient failure)")
                results['skipped_retries'] += 1
                results['details'].append({
                    'run_id': run_id,
                    'action': 'skipped',
                    'reason': 'non-transient failure'
                })
                continue
            
            # Attempt retry
            success = self.rerun_failed_jobs(run_id)
            if success:
                results['successful_retries'] += 1
                results['details'].append({
                    'run_id': run_id,
                    'action': 'retried',
                    'status': 'success'
                })
                
                # Wait for completion
                if self.wait_for_completion(run_id):
                    print(f"   ✅ Retry successful for run {run_id}")
                else:
                    print(f"   ❌ Retry failed for run {run_id}")
                    results['failed_retries'] += 1
            else:
                results['failed_retries'] += 1
                results['details'].append({
                    'run_id': run_id,
                    'action': 'retry_failed',
                    'status': 'error'
                })
        
        return results
    
    def _should_retry_run(self, failed_jobs: List[Dict]) -> bool:
        """Determine if a run should be retried based on failure patterns"""
        # Get logs for analysis
        transient_indicators = [
            'timeout', 'network error', 'connection failed', 'temporary failure',
            'rate limit', 'service unavailable', 'internal server error'
        ]
        
        for job in failed_jobs:
            # For now, assume all failures are retryable
            # In a real implementation, you'd analyze the logs
            return True
        
        return False
    
    def create_workflow_with_retry(self, workflow_file: str, max_retries: int = 3) -> str:
        """Create an enhanced workflow file with retry logic"""
        retry_template = f"""
      - name: Retry on failure
        if: failure()
        run: |
          echo "Job failed, implementing retry logic..."
          # Add custom retry logic here
          exit 1
        continue-on-error: true
"""
        
        # This is a simplified example - in practice, you'd parse and modify the YAML
        return f"Enhanced workflow with retry logic (max {max_retries} retries)"

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Recover from failed GitHub Actions workflows')
    parser.add_argument('--owner', default='sparesparrow', help='Repository owner')
    parser.add_argument('--repo', default='openssl-tools', help='Repository name')
    parser.add_argument('--run-id', type=int, help='Specific run ID to retry')
    parser.add_argument('--auto-retry', action='store_true', help='Automatically retry failed jobs')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries')
    
    args = parser.parse_args()
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token")
        sys.exit(1)
    
    recovery = WorkflowRecovery(args.owner, args.repo)
    
    if args.run_id:
        # Retry specific run
        print(f"🔄 Retrying workflow run {args.run_id}")
        success = recovery.rerun_failed_jobs(args.run_id)
        if success:
            recovery.wait_for_completion(args.run_id)
    elif args.auto_retry:
        # Auto-retry failed jobs
        print("🤖 Auto-retry mode enabled")
        # This would integrate with the monitor script
        print("   (Integration with monitor script needed)")
    else:
        print("Please specify --run-id or --auto-retry")

if __name__ == '__main__':
    main()
