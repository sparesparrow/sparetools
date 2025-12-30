#!/usr/bin/env python3
"""
Improved Version Management System for SpareTools

Inspired by OMS project's flexible versioning approach, this system provides:
1. Git-based automatic versioning (like OMS)
2. Semantic version validation (like current SpareTools)
3. Flexible version bumping strategies
4. Better integration with CI/CD pipelines
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import json


class ImprovedVersionManager:
    """Enhanced version manager combining best of OMS and SpareTools approaches."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.version_pattern = re.compile(r'version\s*=\s*["\']([^"\']+)["\']')
        self.conanfile_path = self._find_main_conanfile()

    def _find_main_conanfile(self) -> Path:
        """Find the main conanfile.py (prefer foundation packages)."""
        candidates = [
            self.repo_root / 'packages' / 'foundation' / 'sparetools-base' / 'conanfile.py',
            self.repo_root / 'conanfile.py'
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError("No conanfile.py found")

    def get_current_version(self) -> Optional[str]:
        """Get current version from conanfile.py."""
        return self.extract_version_from_file(self.conanfile_path)

    def extract_version_from_file(self, file_path: Path) -> Optional[str]:
        """Extract version from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = self.version_pattern.search(content)
            return match.group(1) if match else None
        except Exception:
            return None

    def generate_git_based_version(self, base_version: str = None) -> str:
        """
        Generate version based on git state (OMS-inspired approach).

        Format: BASE_VERSION+git.COMMIT_COUNT.gHASH[.dirty]
        Example: 2.0.3+git.42.gabc1234.dirty
        """
        try:
            # Get base version
            if base_version is None:
                base_version = self.get_current_version() or "0.0.0"

            # Get commit count since last tag or initial commit
            try:
                result = subprocess.run(
                    ['git', 'rev-list', '--count', 'HEAD'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                commit_count = result.stdout.strip()
            except:
                commit_count = "0"

            # Get short commit hash
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                commit_hash = result.stdout.strip()
            except:
                commit_hash = "unknown"

            # Check if working directory is dirty
            try:
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                is_dirty = bool(result.stdout.strip())
            except:
                is_dirty = False

            # Build version string
            version = f"{base_version}+git.{commit_count}.g{commit_hash}"
            if is_dirty:
                version += ".dirty"

            return version

        except Exception as e:
            print(f"Warning: Could not generate git-based version: {e}")
            return base_version or "0.0.0"

    def parse_semantic_version(self, version: str) -> Tuple[int, int, int, Optional[str]]:
        """Parse semantic version, handling git suffixes gracefully."""
        # Remove git suffix for parsing
        base_version = version.split('+')[0]

        parts = base_version.split('-')
        main_version = parts[0]
        pre_release = parts[1] if len(parts) > 1 else None

        try:
            major, minor, patch = map(int, main_version.split('.'))
            return major, minor, patch, pre_release
        except ValueError:
            raise ValueError(f"Invalid semantic version format: {version}")

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Bump version according to semantic versioning rules."""
        major, minor, patch, pre = self.parse_semantic_version(current_version)

        if bump_type == 'major':
            return f"{major + 1}.0.0"
        elif bump_type == 'minor':
            return f"{major}.{minor + 1}.0"
        elif bump_type == 'patch':
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")

    def analyze_commit_messages(self, since_ref: str = None) -> Dict[str, Any]:
        """
        Analyze commit messages to determine appropriate version bump.
        Similar to conventional commits analysis.
        """
        try:
            if since_ref:
                cmd = ['git', 'log', '--oneline', f'{since_ref}..HEAD']
            else:
                # Get last 50 commits if no reference
                cmd = ['git', 'log', '--oneline', '-50']

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_root
            )

            if result.returncode != 0:
                return {'bump_type': 'patch', 'confidence': 0.0, 'commits': []}

            commits = result.stdout.strip().split('\n')
            commits = [c for c in commits if c.strip()]

            # Analyze commits for conventional commit patterns
            breaking_changes = 0
            features = 0
            fixes = 0
            other = 0

            for commit in commits:
                msg = commit.lower()

                # Check for breaking changes
                if any(keyword in msg for keyword in ['breaking', 'break', 'major', 'incompatible', '!']):
                    breaking_changes += 1

                # Check for features
                elif any(keyword in msg for keyword in ['feat', 'feature', 'add', 'new']):
                    features += 1

                # Check for fixes
                elif any(keyword in msg for keyword in ['fix', 'bug', 'patch']):
                    fixes += 1

                else:
                    other += 1

            # Determine bump type based on analysis
            total_commits = len(commits)
            if total_commits == 0:
                bump_type = 'patch'
                confidence = 0.0
            elif breaking_changes > 0:
                bump_type = 'major'
                confidence = min(breaking_changes / total_commits, 1.0)
            elif features > 0:
                bump_type = 'minor'
                confidence = min(features / total_commits, 1.0)
            else:
                bump_type = 'patch'
                confidence = 0.5  # Default confidence for patch bumps

            return {
                'bump_type': bump_type,
                'confidence': confidence,
                'commits_analyzed': total_commits,
                'breaking_changes': breaking_changes,
                'features': features,
                'fixes': fixes,
                'other': other
            }

        except Exception as e:
            print(f"Warning: Could not analyze commits: {e}")
            return {'bump_type': 'patch', 'confidence': 0.0, 'error': str(e)}

    def update_conanfile_version(self, new_version: str) -> bool:
        """Update version in conanfile.py."""
        return self.bump_version_in_file(self.conanfile_path, new_version)

    def bump_version_in_file(self, file_path: Path, new_version: str) -> bool:
        """Update version in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace version
            new_content = self.version_pattern.sub(f'\\g<1>{new_version}\\g<3>', content)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

        return False

    def validate_version_consistency(self) -> Dict[str, Any]:
        """Validate version consistency across all conanfiles."""
        results = {
            'valid': True,
            'main_version': None,
            'inconsistencies': [],
            'files_checked': 0
        }

        # Find all conanfile.py files
        conanfiles = list(self.repo_root.rglob('conanfile.py'))

        if not conanfiles:
            results['valid'] = False
            results['error'] = 'No conanfile.py files found'
            return results

        # Get main version
        main_version = self.get_current_version()
        results['main_version'] = main_version
        results['files_checked'] = len(conanfiles)

        # Check each file
        for conanfile in conanfiles:
            version = self.extract_version_from_file(conanfile)
            if version and version != main_version:
                results['inconsistencies'].append({
                    'file': str(conanfile.relative_to(self.repo_root)),
                    'expected': main_version,
                    'actual': version
                })

        if results['inconsistencies']:
            results['valid'] = False

        return results

    def generate_version_report(self) -> Dict[str, Any]:
        """Generate comprehensive version report."""
        current_version = self.get_current_version()
        git_version = self.generate_git_based_version(current_version)
        consistency = self.validate_version_consistency()
        commit_analysis = self.analyze_commit_messages()

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'current_version': current_version,
            'git_based_version': git_version,
            'consistency_check': consistency,
            'commit_analysis': commit_analysis,
            'recommendations': self._generate_recommendations(commit_analysis, consistency)
        }

    def _generate_recommendations(self, commit_analysis: Dict, consistency: Dict) -> List[str]:
        """Generate version management recommendations."""
        recommendations = []

        if not consistency['valid']:
            recommendations.append("❌ Fix version inconsistencies across conanfile.py files")
            for inconsistency in consistency['inconsistencies']:
                recommendations.append(f"   {inconsistency['file']}: {inconsistency['actual']} → {inconsistency['expected']}")

        if commit_analysis.get('confidence', 0) < 0.3:
            recommendations.append("⚠️  Low confidence in automatic version bump - consider manual review")

        if commit_analysis.get('breaking_changes', 0) > 0:
            recommendations.append("🚨 Breaking changes detected - consider major version bump")

        if not recommendations:
            recommendations.append("✅ Version management looks good")

        return recommendations


def main():
    parser = argparse.ArgumentParser(description='Improved SpareTools Version Management')
    parser.add_argument('command', choices=[
        'current', 'bump', 'analyze', 'validate', 'report', 'git-version'
    ], help='Command to execute')

    parser.add_argument('--type', choices=['major', 'minor', 'patch'],
                       help='Version bump type (for bump command)')

    parser.add_argument('--auto', action='store_true',
                       help='Automatically determine bump type from commits')

    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    parser.add_argument('--since', help='Reference to analyze commits since (for analyze command)')

    parser.add_argument('--json', action='store_true',
                       help='Output in JSON format')

    args = parser.parse_args()

    try:
        repo_root = Path.cwd()
        manager = ImprovedVersionManager(repo_root)

        if args.command == 'current':
            version = manager.get_current_version()
            if args.json:
                print(json.dumps({'current_version': version}))
            else:
                print(f"Current version: {version}")

        elif args.command == 'git-version':
            version = manager.generate_git_based_version()
            if args.json:
                print(json.dumps({'git_version': version}))
            else:
                print(f"Git-based version: {version}")

        elif args.command == 'bump':
            current_version = manager.get_current_version()
            if not current_version:
                print("❌ Could not determine current version")
                sys.exit(1)

            if args.auto:
                analysis = manager.analyze_commit_messages()
                bump_type = analysis['bump_type']
                print(f"🤖 Auto-detected bump type: {bump_type} (confidence: {analysis['confidence']:.1%})")
            elif args.type:
                bump_type = args.type
            else:
                print("❌ Must specify --type or --auto for bump command")
                sys.exit(1)

            new_version = manager.bump_version(current_version, bump_type)

            if args.dry_run:
                print(f"🔍 Would bump: {current_version} → {new_version}")
            else:
                if manager.update_conanfile_version(new_version):
                    print(f"✅ Bumped version: {current_version} → {new_version}")
                else:
                    print("❌ Failed to update version")
                    sys.exit(1)

        elif args.command == 'analyze':
            analysis = manager.analyze_commit_messages(args.since)
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print("📊 Commit Analysis:")
                print(f"   Bump Type: {analysis['bump_type']}")
                print(f"   Confidence: {analysis['confidence']:.1%}")
                print(f"   Commits: {analysis['commits_analyzed']}")
                print(f"   Breaking: {analysis.get('breaking_changes', 0)}")
                print(f"   Features: {analysis.get('features', 0)}")
                print(f"   Fixes: {analysis.get('fixes', 0)}")

        elif args.command == 'validate':
            consistency = manager.validate_version_consistency()
            if args.json:
                print(json.dumps(consistency, indent=2))
            else:
                if consistency['valid']:
                    print("✅ Version consistency check passed")
                else:
                    print("❌ Version consistency check failed")
                    for inconsistency in consistency['inconsistencies']:
                        print(f"   {inconsistency['file']}: {inconsistency['actual']} → {inconsistency['expected']}")
                    sys.exit(1)

        elif args.command == 'report':
            report = manager.generate_version_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("📋 Version Management Report")
                print("=" * 40)
                print(f"Current Version: {report['current_version']}")
                print(f"Git Version: {report['git_based_version']}")
                print(f"Consistency: {'✅ Valid' if report['consistency_check']['valid'] else '❌ Invalid'}")
                print(f"Recommended Bump: {report['commit_analysis']['bump_type']}")
                print("
Recommendations:"                for rec in report['recommendations']:
                    print(f"  {rec}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()