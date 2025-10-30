#!/usr/bin/env python3
"""
Status reporter for OpenSSL CI integration.

Reports build results back to the OpenSSL repository using GitHub APIs:
- Commit Status API for status checks
- Check Runs API for detailed reports
- PR Comments for formatted results
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional
from github import Github
from github.GithubException import GithubException


class StatusReporter:
    """Reports build status back to OpenSSL repository."""
    
    def __init__(self, github_token: str, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize with GitHub API token and retry configuration."""
        self.github = Github(github_token)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def analyze_artifacts(self, artifacts_dir: str) -> Dict[str, Any]:
        """Analyze build artifacts and generate summary."""
        results = {
            'total_jobs': 0,
            'successful_jobs': 0,
            'failed_jobs': 0,
            'builds': [],
            'performance': {
                'total_build_time': 0,
                'average_build_time': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }
        }
        
        if not os.path.exists(artifacts_dir):
            print(f"Warning: Artifacts directory {artifacts_dir} not found", file=sys.stderr)
            return results
        
        # Process each artifact
        for item in os.listdir(artifacts_dir):
            item_path = os.path.join(artifacts_dir, item)
            if not os.path.isdir(item_path):
                continue
            
            # Look for performance reports
            perf_file = os.path.join(item_path, 'performance_report.json')
            if os.path.exists(perf_file):
                try:
                    with open(perf_file) as f:
                        perf_data = json.load(f)
                    
                    # Extract build info from directory name
                    # Format: openssl-{profile}-{os}
                    parts = item.split('-')
                    if len(parts) >= 3:
                        profile = '-'.join(parts[1:-1])
                        os_name = parts[-1]
                    else:
                        profile = 'unknown'
                        os_name = 'unknown'
                    
                    build_info = {
                        'profile': profile,
                        'os': os_name,
                        'status': perf_data.get('status', 'unknown'),
                        'build_time': perf_data.get('build_time', 0),
                        'cache_hit': perf_data.get('cache_hit', False),
                        'packages': perf_data.get('packages', 0)
                    }
                    
                    results['builds'].append(build_info)
                    results['total_jobs'] += 1
                    
                    if build_info['status'] == 'success':
                        results['successful_jobs'] += 1
                    else:
                        results['failed_jobs'] += 1
                    
                    # Update performance metrics
                    results['performance']['total_build_time'] += build_info['build_time']
                    if build_info['cache_hit']:
                        results['performance']['cache_hits'] += 1
                    else:
                        results['performance']['cache_misses'] += 1
                        
                except Exception as e:
                    print(f"Error processing {perf_file}: {e}", file=sys.stderr)
        
        # Calculate averages
        if results['total_jobs'] > 0:
            results['performance']['average_build_time'] = (
                results['performance']['total_build_time'] / results['total_jobs']
            )
        
        return results
    
    def _retry_github_api_call(self, func, *args, **kwargs):
        """Retry GitHub API calls with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except GithubException as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Check if it's a retryable error
                if e.status in [500, 502, 503, 504, 429]:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"GitHub API error (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay}s...", file=sys.stderr)
                    time.sleep(delay)
                else:
                    # Non-retryable error
                    raise e
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                delay = self.retry_delay * (2 ** attempt)
                print(f"Unexpected error (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
        
        return None

    def create_status_check(self, repo_name: str, sha: str, results: Dict[str, Any]) -> str:
        """Create commit status check."""
        try:
            repo = self._retry_github_api_call(self.github.get_repo, repo_name)
            
            # Determine overall status
            if results['failed_jobs'] == 0:
                state = 'success'
                description = f"✅ All {results['successful_jobs']} builds successful"
            elif results['successful_jobs'] == 0:
                state = 'failure'
                description = f"❌ All {results['failed_jobs']} builds failed"
            else:
                state = 'failure'
                description = f"⚠️ {results['successful_jobs']}/{results['total_jobs']} builds successful"
            
            # Create status check
            status = self._retry_github_api_call(
                repo.get_commit(sha).create_status,
                state=state,
                target_url=f"https://github.com/sparesparrow/openssl-tools/actions",
                description=description,
                context="OpenSSL Tools CI"
            )
            
            print(f"Created status check: {state} - {description}", file=sys.stderr)
            return status.url
            
        except GithubException as e:
            print(f"Error creating status check: {e}", file=sys.stderr)
            return ""
    
    def create_check_run(self, repo_name: str, sha: str, results: Dict[str, Any]) -> str:
        """Create detailed check run."""
        try:
            repo = self._retry_github_api_call(self.github.get_repo, repo_name)
            
            # Determine conclusion
            if results['failed_jobs'] == 0:
                conclusion = 'success'
                title = f"✅ OpenSSL Tools CI - All {results['successful_jobs']} builds successful"
            elif results['successful_jobs'] == 0:
                conclusion = 'failure'
                title = f"❌ OpenSSL Tools CI - All {results['failed_jobs']} builds failed"
            else:
                conclusion = 'failure'
                title = f"⚠️ OpenSSL Tools CI - {results['successful_jobs']}/{results['total_jobs']} builds successful"
            
            # Generate detailed output
            output = self._generate_check_run_output(results)
            
            # Create check run
            check_run = self._retry_github_api_call(
                repo.create_check_run,
                name="OpenSSL Tools CI",
                head_sha=sha,
                status="completed",
                conclusion=conclusion,
                output=output
            )
            
            print(f"Created check run: {conclusion} - {title}", file=sys.stderr)
            return check_run.html_url
            
        except GithubException as e:
            print(f"Error creating check run: {e}", file=sys.stderr)
            return ""
    
    def _generate_check_run_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed output for check run."""
        output = {
            'title': f"OpenSSL Tools CI Results",
            'summary': self._generate_summary(results),
            'text': self._generate_detailed_text(results)
        }
        return output
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate summary text."""
        total = results['total_jobs']
        success = results['successful_jobs']
        failed = results['failed_jobs']
        
        perf = results['performance']
        avg_time = perf['average_build_time']
        cache_hits = perf['cache_hits']
        cache_misses = perf['cache_misses']
        
        summary = f"""## Build Results
        
- **Total Jobs**: {total}
- **Successful**: {success} ✅
- **Failed**: {failed} {'❌' if failed > 0 else ''}
- **Average Build Time**: {avg_time:.1f}s
- **Cache Hit Rate**: {cache_hits}/{cache_hits + cache_misses} ({cache_hits/(cache_hits + cache_misses)*100:.1f}% if total > 0 else 0%)

"""
        return summary
    
    def _generate_detailed_text(self, results: Dict[str, Any]) -> str:
        """Generate detailed text with build table."""
        text = "## Build Details\n\n"
        
        if not results['builds']:
            text += "No build results available.\n"
            return text
        
        # Create table header
        text += "| Profile | OS | Status | Build Time | Cache | Packages |\n"
        text += "|---------|----|--------|------------|-------|----------|\n"
        
        # Add each build result
        for build in results['builds']:
            status_emoji = "✅" if build['status'] == 'success' else "❌"
            cache_emoji = "🎯" if build['cache_hit'] else "🔄"
            
            text += f"| {build['profile']} | {build['os']} | {status_emoji} {build['status']} | {build['build_time']}s | {cache_emoji} | {build['packages']} |\n"
        
        text += "\n## Performance Metrics\n\n"
        text += f"- **Total Build Time**: {results['performance']['total_build_time']}s\n"
        text += f"- **Average Build Time**: {results['performance']['average_build_time']:.1f}s\n"
        text += f"- **Cache Hits**: {results['performance']['cache_hits']}\n"
        text += f"- **Cache Misses**: {results['performance']['cache_misses']}\n"
        
        return text
    
    def create_pr_comment(self, repo_name: str, pr_number: int, results: Dict[str, Any]) -> str:
        """Create formatted PR comment."""
        try:
            repo = self._retry_github_api_call(self.github.get_repo, repo_name)
            pr = self._retry_github_api_call(repo.get_pull, pr_number)
            
            # Generate comment body
            comment_body = self._generate_pr_comment_body(results)
            
            # Create comment
            comment = self._retry_github_api_call(pr.create_issue_comment, comment_body)
            
            print(f"Created PR comment on #{pr_number}", file=sys.stderr)
            return comment.html_url
            
        except GithubException as e:
            print(f"Error creating PR comment: {e}", file=sys.stderr)
            return ""
    
    def _generate_pr_comment_body(self, results: Dict[str, Any]) -> str:
        """Generate PR comment body."""
        total = results['total_jobs']
        success = results['successful_jobs']
        failed = results['failed_jobs']
        
        # Determine overall status
        if failed == 0:
            status_emoji = "✅"
            status_text = "All builds successful"
        elif success == 0:
            status_emoji = "❌"
            status_text = "All builds failed"
        else:
            status_emoji = "⚠️"
            status_text = f"{success}/{total} builds successful"
        
        body = f"""## {status_emoji} OpenSSL Tools CI Results

**Status**: {status_text}

### Summary
- **Total Jobs**: {total}
- **Successful**: {success}
- **Failed**: {failed}
- **Average Build Time**: {results['performance']['average_build_time']:.1f}s
- **Cache Hit Rate**: {results['performance']['cache_hits']}/{results['performance']['cache_hits'] + results['performance']['cache_misses']} ({results['performance']['cache_hits']/(results['performance']['cache_hits'] + results['performance']['cache_misses'])*100:.1f}% if total > 0 else 0%)

### Build Details
| Profile | OS | Status | Build Time | Cache | Packages |
|---------|----|--------|------------|-------|----------|
"""
        
        for build in results['builds']:
            status_emoji = "✅" if build['status'] == 'success' else "❌"
            cache_emoji = "🎯" if build['cache_hit'] else "🔄"
            
            body += f"| {build['profile']} | {build['os']} | {status_emoji} {build['status']} | {build['build_time']}s | {cache_emoji} | {build['packages']} |\n"
        
        body += "\n---\n*Generated by OpenSSL Tools CI*"
        
        return body


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Report build status to OpenSSL repository')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--sha', required=True, help='Commit SHA')
    parser.add_argument('--artifacts-dir', required=True, help='Directory containing build artifacts')
    parser.add_argument('--reason', default='', help='Build reason/trigger')
    parser.add_argument('--pr-number', type=int, help='PR number for commenting')
    parser.add_argument('--comment', action='store_true', help='Create PR comment')
    parser.add_argument('--github-token', help='GitHub token (or use GITHUB_TOKEN env var)')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum retry attempts for GitHub API calls')
    parser.add_argument('--retry-delay', type=float, default=1.0, help='Initial retry delay in seconds')
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = args.github_token or os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GitHub token required", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize reporter with retry configuration
        reporter = StatusReporter(github_token, args.max_retries, args.retry_delay)
        
        # Analyze artifacts
        results = reporter.analyze_artifacts(args.artifacts_dir)
        print(f"Analyzed {results['total_jobs']} builds: {results['successful_jobs']} successful, {results['failed_jobs']} failed", file=sys.stderr)
        
        # Create status check
        status_url = reporter.create_status_check(args.repo, args.sha, results)
        
        # Create check run
        check_url = reporter.create_check_run(args.repo, args.sha, results)
        
        # Create PR comment if requested
        if args.comment and args.pr_number:
            comment_url = reporter.create_pr_comment(args.repo, args.pr_number, results)
            print(f"PR comment URL: {comment_url}", file=sys.stderr)
        
        print(f"Status check URL: {status_url}", file=sys.stderr)
        print(f"Check run URL: {check_url}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error reporting status: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()