#!/usr/bin/env python3
"""
GitHub Actions Workflow Manager
Comprehensive tool for monitoring, analyzing, and fixing workflow issues.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Import from the same package
from .monitor import WorkflowMonitor
from .recovery import WorkflowRecovery
from .health_check import WorkflowHealthChecker

class WorkflowManager:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        # Initialize components
        self.monitor = WorkflowMonitor(repo_owner, repo_name, token)
        self.recovery = WorkflowRecovery(repo_owner, repo_name, token)
        self.health_checker = WorkflowHealthChecker(repo_owner, repo_name, token)
    
    def check_status(self, hours_back: int = 24):
        """Check current workflow status"""
        print(f"🔍 Checking workflow status for {self.repo_owner}/{self.repo_name}")
        print(f"⏰ Looking back {hours_back} hours...")
        
        # Get failed jobs
        failed_jobs = self.monitor.analyze_failed_jobs(hours_back)
        
        if not failed_jobs:
            print("✅ No failed jobs found!")
            return
        
        # Generate report
        report = self.monitor.generate_failure_report(failed_jobs)
        print(report)
        
        # Generate suggestions
        suggestions = self.monitor.suggest_fixes(failed_jobs)
        if suggestions:
            print("\n💡 Suggested Fixes:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
    
    def auto_fix(self, max_retries: int = 3):
        """Automatically fix failed workflows"""
        print(f"🤖 Auto-fixing failed workflows for {self.repo_owner}/{self.repo_name}")
        
        # Get failed jobs
        failed_jobs = self.monitor.analyze_failed_jobs(24)
        
        if not failed_jobs:
            print("✅ No failed jobs to fix!")
            return
        
        # Implement retry strategy
        results = self.recovery.implement_retry_strategy(failed_jobs, max_retries)
        
        print(f"\n📊 Auto-fix Results:")
        print(f"   ✅ Successful retries: {results['successful_retries']}")
        print(f"   ❌ Failed retries: {results['failed_retries']}")
        print(f"   ⏭️ Skipped retries: {results['skipped_retries']}")
    
    def health_check(self, days_back: int = 30):
        """Perform comprehensive health check"""
        print(f"🏥 Performing health check for {self.repo_owner}/{self.repo_name}")
        
        # Generate health report
        report = self.health_checker.generate_health_report(days_back)
        print(report)
    
    def retry_run(self, run_id: int):
        """Retry a specific workflow run"""
        print(f"🔄 Retrying workflow run {run_id}")
        
        success = self.recovery.rerun_failed_jobs(run_id)
        if success:
            print("✅ Retry triggered successfully")
            # Wait for completion
            self.recovery.wait_for_completion(run_id)
        else:
            print("❌ Failed to trigger retry")
    
    def monitor_continuously(self, interval_minutes: int = 30):
        """Monitor workflows continuously"""
        import time
        
        print(f"🔄 Starting continuous monitoring (interval: {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Checking workflows...")
                
                # Check for failures
                failed_jobs = self.monitor.analyze_failed_jobs(1)  # Last hour
                
                if failed_jobs:
                    print(f"🚨 Found {len(failed_jobs)} failed jobs!")
                    
                    # Auto-fix if configured
                    if os.getenv('AUTO_FIX_ENABLED', 'false').lower() == 'true':
                        print("🤖 Auto-fixing enabled, attempting fixes...")
                        self.auto_fix()
                    else:
                        print("💡 Auto-fix disabled. Set AUTO_FIX_ENABLED=true to enable.")
                else:
                    print("✅ No failed jobs found")
                
                # Wait for next check
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    
    def setup_notifications(self):
        """Setup workflow failure notifications"""
        print("🔔 Setting up workflow failure notifications")
        
        # This would integrate with notification services
        # For now, just provide instructions
        print("""
To setup notifications:

1. GitHub Notifications:
   - Go to repository Settings > Notifications
   - Enable email notifications for workflow failures

2. Slack Integration:
   - Add GitHub app to your Slack workspace
   - Configure webhook for workflow failures

3. Email Alerts:
   - Use GitHub's built-in email notifications
   - Configure in repository settings

4. Custom Webhook:
   - Set up webhook endpoint
   - Configure in repository settings
        """)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='GitHub Actions Workflow Manager')
    parser.add_argument('--owner', default='sparesparrow', help='Repository owner')
    parser.add_argument('--repo', default='openssl-tools', help='Repository name')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check workflow status')
    status_parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    
    # Auto-fix command
    fix_parser = subparsers.add_parser('fix', help='Auto-fix failed workflows')
    fix_parser.add_argument('--max-retries', type=int, default=3, help='Maximum retries')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Perform health check')
    health_parser.add_argument('--days', type=int, default=30, help='Days to look back')
    
    # Retry command
    retry_parser = subparsers.add_parser('retry', help='Retry specific workflow run')
    retry_parser.add_argument('run_id', type=int, help='Workflow run ID to retry')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor workflows continuously')
    monitor_parser.add_argument('--interval', type=int, default=30, help='Check interval in minutes')
    
    # Notifications command
    subparsers.add_parser('notifications', help='Setup notifications')
    
    args = parser.parse_args()
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token")
        sys.exit(1)
    
    # Initialize manager
    manager = WorkflowManager(args.owner, args.repo)
    
    # Execute command
    if args.command == 'status':
        manager.check_status(args.hours)
    elif args.command == 'fix':
        manager.auto_fix(args.max_retries)
    elif args.command == 'health':
        manager.health_check(args.days)
    elif args.command == 'retry':
        manager.retry_run(args.run_id)
    elif args.command == 'monitor':
        manager.monitor_continuously(args.interval)
    elif args.command == 'notifications':
        manager.setup_notifications()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
