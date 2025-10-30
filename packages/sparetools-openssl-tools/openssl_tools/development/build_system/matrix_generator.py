#!/usr/bin/env python3
"""
Intelligent build matrix generator for OpenSSL CI.

Analyzes changed files in OpenSSL repository and generates an optimized
build matrix based on the type of changes detected.
"""

import argparse
import json
import sys
from typing import Dict, List, Set, Any
from github import Github
from github.GithubException import GithubException


class BuildMatrixGenerator:
    """Generates optimized build matrices based on file changes."""
    
    def __init__(self, github_token: str):
        """Initialize with GitHub API token."""
        self.github = Github(github_token)
        
        # Define file category mappings
        self.category_mappings = {
            'crypto': {
                'patterns': ['crypto/', 'include/openssl/'],
                'profiles': ['linux-gcc-release', 'windows-msvc', 'macos-clang'],
                'priority': 'high'
            },
            'ssl': {
                'patterns': ['ssl/', 'include/openssl/ssl'],
                'profiles': ['linux-gcc-release', 'windows-msvc', 'macos-clang'],
                'priority': 'high'
            },
            'fips': {
                'patterns': ['providers/fips/', 'fips/'],
                'profiles': ['linux-fips'],
                'priority': 'critical',
                'separate_cache': True
            },
            'test': {
                'patterns': ['test/', 'fuzz/'],
                'profiles': ['linux-gcc-debug'],
                'priority': 'medium'
            },
            'build_system': {
                'patterns': ['conanfile.py', 'Configure', 'config/', 'Makefile'],
                'profiles': ['linux-gcc-release', 'linux-gcc-debug', 'windows-msvc', 'macos-clang', 'linux-fips'],
                'priority': 'critical'
            },
            'documentation': {
                'patterns': ['doc/', '*.md', 'README'],
                'profiles': [],
                'priority': 'low'
            }
        }
        
        # Base build configurations
        self.base_configs = {
            'linux-gcc-release': {
                'os': 'ubuntu-22.04',
                'profile': 'linux-gcc-release',
                'cache_key': 'linux-gcc11-rel'
            },
            'linux-gcc-debug': {
                'os': 'ubuntu-22.04',
                'profile': 'linux-gcc-debug',
                'cache_key': 'linux-gcc11-debug'
            },
            'linux-fips': {
                'os': 'ubuntu-22.04',
                'profile': 'linux-fips',
                'cache_key': 'linux-fips',
                'separate_cache': True
            },
            'windows-msvc': {
                'os': 'windows-2022',
                'profile': 'windows-msvc',
                'cache_key': 'win-msvc2022'
            },
            'macos-clang': {
                'os': 'macos-13',
                'profile': 'macos-clang',
                'cache_key': 'macos-clang15'
            }
        }
    
    def get_changed_files(self, repo_name: str, sha: str) -> List[str]:
        """Get list of changed files for a given commit."""
        try:
            repo = self.github.get_repo(repo_name)
            commit = repo.get_commit(sha)
            return [file.filename for file in commit.files]
        except GithubException as e:
            print(f"Error fetching changed files: {e}", file=sys.stderr)
            return []
    
    def categorize_changes(self, changed_files: List[str]) -> Dict[str, Set[str]]:
        """Categorize changed files by type."""
        categories = {category: set() for category in self.category_mappings.keys()}
        
        for file_path in changed_files:
            for category, config in self.category_mappings.items():
                for pattern in config['patterns']:
                    if pattern.endswith('/'):
                        # Directory pattern
                        if file_path.startswith(pattern):
                            categories[category].add(file_path)
                            break
                    elif pattern.startswith('*'):
                        # Extension pattern
                        if file_path.endswith(pattern[1:]):
                            categories[category].add(file_path)
                            break
                    else:
                        # Exact filename pattern
                        if file_path == pattern or file_path.endswith('/' + pattern):
                            categories[category].add(file_path)
                            break
        
        return categories
    
    def select_profiles(self, categories: Dict[str, Set[str]]) -> Set[str]:
        """Select build profiles based on categorized changes."""
        selected_profiles = set()
        
        # Check each category
        for category, files in categories.items():
            if not files:
                continue
                
            config = self.category_mappings[category]
            profiles = config['profiles']
            
            if not profiles:
                continue
                
            # Add all profiles for this category
            selected_profiles.update(profiles)
            
            print(f"Category '{category}': {len(files)} files changed", file=sys.stderr)
            print(f"  Files: {', '.join(sorted(files)[:5])}{'...' if len(files) > 5 else ''}", file=sys.stderr)
            print(f"  Selected profiles: {', '.join(profiles)}", file=sys.stderr)
        
        # If no specific changes detected, use minimal build
        if not selected_profiles:
            print("No specific changes detected, using minimal build", file=sys.stderr)
            selected_profiles.add('linux-gcc-release')
        
        return selected_profiles
    
    def generate_matrix(self, profiles: Set[str]) -> List[Dict[str, Any]]:
        """Generate build matrix from selected profiles."""
        matrix = []
        
        for profile in profiles:
            if profile in self.base_configs:
                config = self.base_configs[profile].copy()
                matrix.append(config)
            else:
                print(f"Warning: Unknown profile '{profile}'", file=sys.stderr)
        
        return matrix
    
    def generate_build_matrix(self, repo_name: str, sha: str, reason: str = "") -> Dict[str, Any]:
        """Generate complete build matrix for given repository and commit."""
        print(f"Analyzing changes in {repo_name}@{sha}", file=sys.stderr)
        print(f"Build reason: {reason}", file=sys.stderr)
        
        # Get changed files
        changed_files = self.get_changed_files(repo_name, sha)
        if not changed_files:
            print("No changed files found, using minimal build", file=sys.stderr)
            changed_files = []
        
        print(f"Found {len(changed_files)} changed files", file=sys.stderr)
        
        # Categorize changes
        categories = self.categorize_changes(changed_files)
        
        # Select profiles
        selected_profiles = self.select_profiles(categories)
        
        # Generate matrix
        matrix = self.generate_matrix(selected_profiles)
        
        # Create result
        result = {
            'include': matrix,
            'total_jobs': len(matrix),
            'selected_profiles': list(selected_profiles),
            'changed_files_count': len(changed_files),
            'categories': {k: list(v) for k, v in categories.items() if v},
            'reason': reason,
            'sha': sha
        }
        
        return result


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate build matrix for OpenSSL CI')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--sha', required=True, help='Commit SHA to analyze')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--reason', default='', help='Build reason/trigger')
    parser.add_argument('--github-token', help='GitHub token (or use GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = args.github_token or sys.stdin.read().strip()
    if not github_token:
        print("Error: GitHub token required", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Generate build matrix
        generator = BuildMatrixGenerator(github_token)
        result = generator.generate_build_matrix(args.repo, args.sha, args.reason)
        
        # Write output
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Generated build matrix with {result['total_jobs']} jobs", file=sys.stderr)
        print(f"Selected profiles: {', '.join(result['selected_profiles'])}", file=sys.stderr)
        print(f"Matrix written to: {args.output}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error generating build matrix: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()