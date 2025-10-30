#!/usr/bin/env python3
"""
GitHub Actions Workflow Health Check
Monitors workflow health and provides recommendations for improvement.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import yaml

class WorkflowHealthChecker:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OpenSSL-Tools-Health-Checker'
        }
    
    def get_workflow_runs(self, workflow_id: str = None, limit: int = 100) -> List[Dict]:
        """Get recent workflow runs"""
        url = f"{self.base_url}/actions/runs"
        params = {'per_page': limit}
        
        if workflow_id:
            params['workflow_id'] = workflow_id
            
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
    
    def analyze_workflow_health(self, days_back: int = 30) -> Dict:
        """Analyze overall workflow health"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all workflow runs
        runs = self.get_workflow_runs(limit=200)
        recent_runs = []
        for run in runs:
            run_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            cutoff_time_aware = cutoff_date.replace(tzinfo=run_time.tzinfo)
            if run_time > cutoff_time_aware:
                recent_runs.append(run)
        
        health_metrics = {
            'total_runs': len(recent_runs),
            'successful_runs': 0,
            'failed_runs': 0,
            'cancelled_runs': 0,
            'in_progress_runs': 0,
            'success_rate': 0.0,
            'average_duration': 0.0,
            'failure_patterns': {},
            'performance_issues': [],
            'recommendations': []
        }
        
        total_duration = 0
        completed_runs = 0
        
        for run in recent_runs:
            status = run['status']
            conclusion = run.get('conclusion')
            
            if status == 'completed':
                completed_runs += 1
                if conclusion == 'success':
                    health_metrics['successful_runs'] += 1
                elif conclusion == 'failure':
                    health_metrics['failed_runs'] += 1
                    self._analyze_failure_pattern(run, health_metrics)
                elif conclusion == 'cancelled':
                    health_metrics['cancelled_runs'] += 1
                
                # Calculate duration
                if run.get('run_started_at') and run.get('updated_at'):
                    start = datetime.fromisoformat(run['run_started_at'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                    total_duration += duration
            elif status in ['queued', 'in_progress']:
                health_metrics['in_progress_runs'] += 1
        
        # Calculate metrics
        if completed_runs > 0:
            health_metrics['success_rate'] = (health_metrics['successful_runs'] / completed_runs) * 100
            health_metrics['average_duration'] = total_duration / completed_runs
        
        # Generate recommendations
        health_metrics['recommendations'] = self._generate_recommendations(health_metrics)
        
        return health_metrics
    
    def _analyze_failure_pattern(self, run: Dict, health_metrics: Dict):
        """Analyze failure patterns in a workflow run"""
        jobs = self.get_workflow_jobs(run['id'])
        
        for job in jobs:
            if job['conclusion'] == 'failure':
                job_name = job['name']
                if job_name not in health_metrics['failure_patterns']:
                    health_metrics['failure_patterns'][job_name] = 0
                health_metrics['failure_patterns'][job_name] += 1
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on health metrics"""
        recommendations = []
        
        # Success rate recommendations
        if metrics['success_rate'] < 80:
            recommendations.append("🔴 Low success rate detected. Consider implementing retry logic and improving error handling.")
        elif metrics['success_rate'] < 95:
            recommendations.append("🟡 Success rate could be improved. Review common failure patterns.")
        else:
            recommendations.append("🟢 Excellent success rate! Keep up the good work.")
        
        # Duration recommendations
        if metrics['average_duration'] > 3600:  # More than 1 hour
            recommendations.append("⏱️ Long average duration detected. Consider optimizing build performance and using caching.")
        elif metrics['average_duration'] > 1800:  # More than 30 minutes
            recommendations.append("⏱️ Moderate duration. Consider parallelization and build optimization.")
        
        # Failure pattern recommendations
        if metrics['failure_patterns']:
            most_failed_job = max(metrics['failure_patterns'].items(), key=lambda x: x[1])
            if most_failed_job[1] > 3:
                recommendations.append(f"🔧 Job '{most_failed_job[0]}' fails frequently. Investigate and fix underlying issues.")
        
        # Cancellation recommendations
        if metrics['cancelled_runs'] > metrics['total_runs'] * 0.1:  # More than 10% cancelled
            recommendations.append("⏹️ High cancellation rate. Consider optimizing workflow efficiency.")
        
        return recommendations
    
    def check_workflow_configuration(self) -> Dict:
        """Check workflow configuration for best practices"""
        config_issues = []
        recommendations = []
        
        # Check workflow files
        workflow_files = [
            '.github/workflows/main.yml',
            '.github/workflows/conan-ci.yml',
            '.github/workflows/conan-ci-enhanced.yml'
        ]
        
        for workflow_file in workflow_files:
            if os.path.exists(workflow_file):
                issues = self._check_workflow_file(workflow_file)
                config_issues.extend(issues)
        
        # Generate configuration recommendations
        if any('timeout' in issue.lower() for issue in config_issues):
            recommendations.append("⏱️ Add timeout configurations to prevent hanging jobs")
        
        if any('retry' in issue.lower() for issue in config_issues):
            recommendations.append("🔄 Implement retry logic for transient failures")
        
        if any('cache' in issue.lower() for issue in config_issues):
            recommendations.append("💾 Add caching to improve build performance")
        
        return {
            'config_issues': config_issues,
            'recommendations': recommendations
        }
    
    def _check_workflow_file(self, file_path: str) -> List[str]:
        """Check individual workflow file for issues"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for common issues
            if 'timeout-minutes' not in content:
                issues.append(f"Missing timeout configuration in {file_path}")
            
            if 'continue-on-error' not in content and 'retry' not in content.lower():
                issues.append(f"No retry logic in {file_path}")
            
            if 'cache' not in content.lower():
                issues.append(f"No caching strategy in {file_path}")
            
            if 'fail-fast: true' in content:
                issues.append(f"fail-fast enabled in {file_path} - consider setting to false")
            
        except Exception as e:
            issues.append(f"Error reading {file_path}: {e}")
        
        return issues
    
    def generate_health_report(self, days_back: int = 30) -> str:
        """Generate comprehensive health report"""
        print(f"🔍 Analyzing workflow health for the last {days_back} days...")
        
        # Get health metrics
        health_metrics = self.analyze_workflow_health(days_back)
        
        # Get configuration analysis
        config_analysis = self.check_workflow_configuration()
        
        # Generate report
        report = f"""
# GitHub Actions Workflow Health Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Repository: {self.repo_owner}/{self.repo_name}
Period: Last {days_back} days

## 📊 Overall Health Metrics

- **Total Runs**: {health_metrics['total_runs']}
- **Successful Runs**: {health_metrics['successful_runs']}
- **Failed Runs**: {health_metrics['failed_runs']}
- **Cancelled Runs**: {health_metrics['cancelled_runs']}
- **In Progress**: {health_metrics['in_progress_runs']}
- **Success Rate**: {health_metrics['success_rate']:.1f}%
- **Average Duration**: {health_metrics['average_duration']/60:.1f} minutes

## 🔍 Failure Patterns

"""
        
        if health_metrics['failure_patterns']:
            for job_name, count in sorted(health_metrics['failure_patterns'].items(), 
                                        key=lambda x: x[1], reverse=True):
                report += f"- **{job_name}**: {count} failures\n"
        else:
            report += "No significant failure patterns detected.\n"
        
        report += "\n## 💡 Recommendations\n\n"
        
        for recommendation in health_metrics['recommendations']:
            report += f"- {recommendation}\n"
        
        if config_analysis['recommendations']:
            report += "\n## ⚙️ Configuration Recommendations\n\n"
            for recommendation in config_analysis['recommendations']:
                report += f"- {recommendation}\n"
        
        if config_analysis['config_issues']:
            report += "\n## ⚠️ Configuration Issues\n\n"
            for issue in config_analysis['config_issues']:
                report += f"- {issue}\n"
        
        report += f"\n## 🎯 Next Steps\n\n"
        report += f"1. Review and address the recommendations above\n"
        report += f"2. Implement retry logic for transient failures\n"
        report += f"3. Add proper timeout configurations\n"
        report += f"4. Consider using the enhanced workflow file\n"
        report += f"5. Monitor success rates after implementing changes\n"
        
        return report

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check GitHub Actions workflow health')
    parser.add_argument('--owner', default='sparesparrow', help='Repository owner')
    parser.add_argument('--repo', default='openssl-tools', help='Repository name')
    parser.add_argument('--days', type=int, default=30, help='Days to look back')
    parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token")
        sys.exit(1)
    
    checker = WorkflowHealthChecker(args.owner, args.repo)
    
    # Generate report
    report = checker.generate_health_report(args.days)
    print(report)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to {args.output}")

if __name__ == '__main__':
    main()
