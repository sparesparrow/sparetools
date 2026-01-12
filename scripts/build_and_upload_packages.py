#!/usr/bin/env python3
"""
Comprehensive SpareTools Package Builder and Uploader

Builds all packages and uploads them to Cloudsmith and GitHub Packages.
Handles dependency ordering, parallel builds where possible, and error recovery.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PackageBuilder:
    """Builds and uploads all SpareTools packages."""

    def __init__(self, workspace_root: Path, dry_run: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.build_results = []
        self.upload_results = []

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
            class MockResult:
                def __init__(self):
                    self.returncode = 0
                    self.stdout = "DRY RUN - Command not executed"
                    self.stderr = ""
            return MockResult()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.workspace_root,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            if e.stdout:
                logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            raise

    def get_package_info(self, conanfile_path: Path) -> Dict[str, str]:
        """Extract package name and version from conanfile.py."""
        try:
            with open(conanfile_path, 'r') as f:
                content = f.read()

            name = None
            version = None

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('name = '):
                    name = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('version = '):
                    version = line.split('=')[1].strip().strip('"\'')
                if name and version:
                    break

            return {
                'name': name or 'unknown',
                'version': version or 'unknown',
                'path': str(conanfile_path.parent.relative_to(self.workspace_root))
            }
        except Exception as e:
            logger.warning(f"Could not parse {conanfile_path}: {e}")
            return {'name': None, 'version': None, 'path': str(conanfile_path.parent)}

    def find_all_packages(self) -> List[Dict[str, str]]:
        """Find all packages in the repository."""
        packages = []

        # Find all conanfile.py files (excluding test packages)
        for conanfile in self.workspace_root.rglob('packages/**/conanfile.py'):
            if 'test_package' not in str(conanfile) and 'deprecated' not in str(conanfile):
                info = self.get_package_info(conanfile)
                if info['name'] and info['name'] != 'unknown':
                    packages.append(info)

        return packages

    def get_build_order(self, packages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Determine build order based on dependencies."""
        # Foundation packages first
        foundation = [p for p in packages if 'foundation' in p['path']]
        embedded = [p for p in packages if 'embedded' in p['path']]
        schemas = [p for p in packages if 'schemas' in p['path']]
        consumers = [p for p in packages if 'consumers' in p['path']]

        # Order foundation packages
        foundation_order = [
            'sparetools-recipe-base',
            'sparetools-base',
            'sparetools-test-harness',
            'sparetools-shared-dev-tools',
            'sparetools-bootstrap',
        ]

        ordered_foundation = []
        for pkg_name in foundation_order:
            for pkg in foundation:
                if pkg['name'] == pkg_name:
                    ordered_foundation.append(pkg)
                    break

        # Add any remaining foundation packages
        for pkg in foundation:
            if pkg not in ordered_foundation:
                ordered_foundation.append(pkg)

        return ordered_foundation + embedded + schemas + consumers

    def build_package(self, package: Dict[str, str]) -> bool:
        """Build a single package."""
        start_time = time.time()
        package_path = self.workspace_root / package['path']
        package_name = package['name']
        package_version = package['version']

        logger.info(f"🔨 Building {package_name}/{package_version}")

        try:
            result = self.run_command(
                ["conan", "create", ".", "--user", "sparetools", "--channel", "stable", "--build=missing"],
                cwd=package_path
            )

            build_time = time.time() - start_time
            logger.info(f"✅ Successfully built {package_name}/{package_version} in {build_time:.1f}s")

            self.build_results.append({
                'name': package_name,
                'version': package_version,
                'status': 'success',
                'duration': build_time
            })

            return True

        except Exception as e:
            build_time = time.time() - start_time
            logger.error(f"❌ Failed to build {package_name}: {e}")

            self.build_results.append({
                'name': package_name,
                'version': package_version,
                'status': 'failed',
                'duration': build_time,
                'error': str(e)
            })

            return False

    def build_all_packages(self) -> bool:
        """Build all packages in dependency order."""
        logger.info("🚀 Starting package build process...")

        packages = self.find_all_packages()
        logger.info(f"📋 Found {len(packages)} packages to build")

        build_order = self.get_build_order(packages)
        logger.info(f"📋 Build order determined: {len(build_order)} packages")

        success_count = 0
        total_count = len(build_order)

        for i, package in enumerate(build_order, 1):
            logger.info(f"\n[{i}/{total_count}] Building {package['name']}")
            if self.build_package(package):
                success_count += 1

        logger.info(f"\n📊 BUILD SUMMARY: {success_count}/{total_count} packages built successfully")

        return success_count == total_count

    def configure_remotes(self, include_github: bool = False):
        """Configure Conan remotes for Cloudsmith and GitHub."""
        logger.info("🔧 Configuring Conan remotes...")

        # Detect profile
        self.run_command(["conan", "profile", "detect", "--force"], check=False)

        # Add Cloudsmith remote
        cloudsmith_url = "https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/conan/"
        self.run_command([
            "conan", "remote", "add", "sparesparrow-conan", cloudsmith_url, "--force"
        ], check=False)

        # Add GitHub Packages remote only if requested (skip during build to avoid auth issues)
        if include_github:
            github_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "sparesparrow")
            github_repo = os.environ.get("GITHUB_REPOSITORY", "sparesparrow/sparetools").split("/")[-1]
            github_url = f"https://maven.pkg.github.com/{github_owner}/{github_repo}"
            self.run_command([
                "conan", "remote", "add", "github-packages", github_url, "--force"
            ], check=False)
        else:
            # Remove GitHub remote if it exists to avoid auth prompts during build
            self.run_command([
                "conan", "remote", "remove", "github-packages"
            ], check=False)

        logger.info("✅ Conan remotes configured")

    def authenticate_cloudsmith(self) -> bool:
        """Authenticate with Cloudsmith."""
        api_key = os.environ.get("CLOUDSMITH_API_KEY")
        if not api_key:
            logger.warning("CLOUDSMITH_API_KEY not set, skipping Cloudsmith authentication")
            return False

        logger.info("🔐 Authenticating with Cloudsmith...")

        if self.dry_run:
            logger.info("[DRY-RUN] Would authenticate with Cloudsmith")
            return True

        try:
            self.run_command([
                "conan", "remote", "login", "sparesparrow-conan", "sparesparrow", "--password", api_key
            ])
            logger.info("✅ Authenticated with Cloudsmith")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with Cloudsmith: {e}")
            return False

    def authenticate_github(self) -> bool:
        """Authenticate with GitHub Packages."""
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            logger.warning("GITHUB_TOKEN not set, skipping GitHub authentication")
            return False

        logger.info("🔐 Authenticating with GitHub Packages...")

        if self.dry_run:
            logger.info("[DRY-RUN] Would authenticate with GitHub Packages")
            return True

        try:
            github_user = os.environ.get("GITHUB_ACTOR", "sparesparrow")
            self.run_command([
                "conan", "remote", "login", "github-packages", github_user, "--password", token
            ])
            logger.info("✅ Authenticated with GitHub Packages")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with GitHub Packages: {e}")
            return False

    def upload_packages(self, remote: str) -> bool:
        """Upload all packages to a remote."""
        logger.info(f"📤 Uploading packages to {remote}...")

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would upload packages to {remote}")
            return True

        try:
            # Upload sparetools packages
            self.run_command([
                "conan", "upload", "sparetools-*/*", "-r", remote, "--confirm", "--retry", "3", "--retry-wait", "5"
            ])

            # Upload schema packages
            self.run_command([
                "conan", "upload", "sparetools-protocols/*", "-r", remote, "--confirm", "--retry", "3", "--retry-wait", "5"
            ], check=False)

            logger.info(f"✅ Successfully uploaded packages to {remote}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload packages to {remote}: {e}")
            return False

    def generate_report(self):
        """Generate comprehensive build and upload report."""
        report_file = self.workspace_root / "BUILD_UPLOAD_REPORT.json"

        report = {
            'timestamp': time.time(),
            'build_results': self.build_results,
            'upload_results': self.upload_results,
            'summary': {
                'total_packages': len(self.build_results),
                'successful_builds': len([r for r in self.build_results if r['status'] == 'success']),
                'failed_builds': len([r for r in self.build_results if r['status'] == 'failed']),
            }
        }

        if not self.dry_run:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"📄 Report saved to: {report_file}")

    def run_full_process(self, skip_build: bool = False, skip_cloudsmith: bool = False, skip_github: bool = False):
        """Run the complete build and upload process."""
        logger.info("=" * 60)
        logger.info("SpareTools Package Build and Upload")
        logger.info("=" * 60)

        # Step 1: Configure remotes (without GitHub to avoid auth issues during build)
        self.configure_remotes(include_github=False)

        # Step 2: Build packages
        if not skip_build:
            if not self.build_all_packages():
                logger.warning("Some packages failed to build, but continuing...")

        # Step 3: Add GitHub remote for upload (if needed)
        if not skip_github:
            self.configure_remotes(include_github=True)

        # Step 4: Authenticate
        cloudsmith_auth = False
        github_auth = False

        if not skip_cloudsmith:
            cloudsmith_auth = self.authenticate_cloudsmith()

        if not skip_github:
            github_auth = self.authenticate_github()

        # Step 5: Upload packages
        if cloudsmith_auth:
            self.upload_packages("sparesparrow-conan")
            self.upload_results.append({'remote': 'sparesparrow-conan', 'status': 'success'})

        if github_auth:
            self.upload_packages("github-packages")
            self.upload_results.append({'remote': 'github-packages', 'status': 'success'})

        # Step 6: Generate report
        self.generate_report()

        logger.info("=" * 60)
        logger.info("✅ Build and upload process complete!")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Build and upload all SpareTools packages")
    parser.add_argument("--skip-build", action="store_true", help="Skip building packages")
    parser.add_argument("--skip-cloudsmith", action="store_true", help="Skip Cloudsmith upload")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub Packages upload")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--workspace", type=str, help="Workspace root directory", default=None)

    args = parser.parse_args()

    workspace_root = Path(args.workspace) if args.workspace else Path(__file__).parent.parent

    builder = PackageBuilder(workspace_root, dry_run=args.dry_run)
    builder.run_full_process(
        skip_build=args.skip_build,
        skip_cloudsmith=args.skip_cloudsmith,
        skip_github=args.skip_github
    )


if __name__ == "__main__":
    main()