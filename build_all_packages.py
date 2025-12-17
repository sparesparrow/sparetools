#!/usr/bin/env python3
"""
SpareTools Package Builder

Builds and optionally publishes all SpareTools packages to a Conan repository.
Handles dependency ordering and provides comprehensive build reporting.

Usage:
    python build_all_packages.py [--export-local] [--remote REMOTE] [--dry-run] [--verbose]
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
import time


class PackageBuilder:
    """Builds all SpareTools packages with proper dependency ordering."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.build_results = []

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        if self.dry_run:
            print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
            # Return mock successful result
            class MockResult:
                def __init__(self):
                    self.returncode = 0
                    self.stdout = "DRY RUN - Command not executed"
                    self.stderr = ""
            return MockResult()

        if self.verbose:
            print(f"[EXEC] {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=not self.verbose,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def get_package_info(self, conanfile_path: Path) -> Dict[str, str]:
        """Extract package name and version from conanfile.py."""
        try:
            # Read the conanfile.py
            with open(conanfile_path, 'r') as f:
                content = f.read()

            # Extract name and version using simple parsing
            name = None
            version = None

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('name = ') and 'sparetools' in line:
                    name = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('version = '):
                    version = line.split('=')[1].strip().strip('"\'')
                if name and version:
                    break

            return {'name': name, 'version': version, 'path': str(conanfile_path.parent)}

        except Exception as e:
            print(f"Warning: Could not parse {conanfile_path}: {e}")
            return {'name': None, 'version': None, 'path': str(conanfile_path.parent)}

    def find_all_packages(self) -> List[Dict[str, str]]:
        """Find all packages in the repository."""
        packages = []

        # Find all conanfile.py files (excluding test packages)
        for conanfile in self.project_root.rglob('packages/**/conanfile.py'):
            if 'test_package' not in str(conanfile):
                info = self.get_package_info(conanfile)
                if info['name']:
                    packages.append(info)

        return packages

    def get_build_order(self, packages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Determine build order based on dependencies."""
        # Foundation packages first (no external dependencies)
        foundation = [p for p in packages if 'foundation' in p['path']]
        consumers = [p for p in packages if 'consumers' in p['path'] and 'deprecated' not in p['path']]
        deprecated = [p for p in packages if 'deprecated' in p['path']]

        # Within foundation, order matters for dependencies
        foundation_order = [
            'sparetools-recipe-base',  # Base for all others
            'sparetools-base',         # Depends on recipe-base
            'sparetools-cpython',      # Independent
            'sparetools-test-harness', # Depends on base
            'sparetools-shared-dev-tools', # Depends on base
            'sparetools-bootstrap',    # Depends on base, cpython
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

        return ordered_foundation + consumers + deprecated

    def build_package(self, package: Dict[str, str], export_local: bool = False,
                     remote: Optional[str] = None) -> bool:
        """Build a single package."""
        start_time = time.time()

        package_name = package['name']
        package_version = package['version']
        package_path = Path(package['path'])

        print(f"\n🔨 Building {package_name}/{package_version}")
        print(f"   Path: {package_path}")

        try:
            # Create build directory
            build_dir = package_path / "build"
            if not self.dry_run:
                build_dir.mkdir(exist_ok=True)

            # Build the package
            print("   📦 Creating package...")
            result = self.run_command(
                ["conan", "create", ".", "--name", package_name, "--version", package_version, "--user", "sparetools", "--channel", "stable"],
                cwd=package_path
            )

            if result.returncode != 0:
                print(f"❌ Failed to build {package_name}")
                self.build_results.append({
                    'name': package_name,
                    'version': package_version,
                    'status': 'failed',
                    'duration': time.time() - start_time,
                    'error': 'Build failed'
                })
                return False

            # Export to local cache if requested
            if export_local:
                print("   📤 Exporting to local cache...")
                self.run_command([
                    "conan", "export", ".", "--name", package_name, "--version", package_version, "--user", "sparetools", "--channel", "stable"
                ], cwd=package_path)

            # Upload to remote if specified
            if remote:
                print(f"   ☁️  Uploading to {remote}...")
                self.run_command([
                    "conan", "upload", "--name", package_name, "--version", package_version, "--user", "sparetools", "--channel", "stable", "-r", remote, "--force"
                ])

            build_time = time.time() - start_time
            print(f"✅ Successfully built {package_name}/{package_version} in {build_time:.1f}s")

            self.build_results.append({
                'name': package_name,
                'version': package_version,
                'status': 'success',
                'duration': build_time
            })

            return True

        except Exception as e:
            build_time = time.time() - start_time
            print(f"❌ Failed to build {package_name}: {e}")
            self.build_results.append({
                'name': package_name,
                'version': package_version,
                'status': 'failed',
                'duration': build_time,
                'error': str(e)
            })
            return False

    def build_all_packages(self, export_local: bool = False, remote: Optional[str] = None) -> bool:
        """Build all packages in dependency order."""
        print("🚀 SpareTools Package Builder")
        print("=" * 50)

        # Find all packages
        packages = self.find_all_packages()
        print(f"📋 Found {len(packages)} packages to build")

        # Get build order
        build_order = self.get_build_order(packages)
        print(f"📋 Build order determined: {len(build_order)} packages")

        # Build each package
        success_count = 0
        total_count = len(build_order)

        for i, package in enumerate(build_order, 1):
            print(f"\n[{i}/{total_count}] Building {package['name']}")
            if self.build_package(package, export_local, remote):
                success_count += 1

        # Generate summary report
        self.generate_report()

        print("\n" + "=" * 50)
        print(f"📊 BUILD SUMMARY: {success_count}/{total_count} packages built successfully")

        if success_count == total_count:
            print("🎉 ALL PACKAGES BUILT SUCCESSFULLY!")
            return True
        else:
            print(f"⚠️  {total_count - success_count} packages failed to build")
            return False

    def generate_report(self):
        """Generate a comprehensive build report."""
        report_file = self.project_root / "build_report.json"

        report = {
            'timestamp': time.time(),
            'total_packages': len(self.build_results),
            'successful_builds': len([r for r in self.build_results if r['status'] == 'success']),
            'failed_builds': len([r for r in self.build_results if r['status'] == 'failed']),
            'total_build_time': sum(r['duration'] for r in self.build_results),
            'results': self.build_results
        }

        if not self.dry_run:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            print(f"\n📄 Detailed report saved to: {report_file}")

        # Print summary
        print("\n📊 BUILD RESULTS:")
        print("-" * 30)
        for result in self.build_results:
            status = "✅" if result['status'] == 'success' else "❌"
            duration = ".1f"
            print("6")

def main():
    parser = argparse.ArgumentParser(description="Build all SpareTools packages")
    parser.add_argument("--export-local", action="store_true",
                       help="Export packages to local Conan cache")
    parser.add_argument("--remote", help="Upload packages to specified Conan remote")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be built without actually building")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")

    args = parser.parse_args()

    builder = PackageBuilder(dry_run=args.dry_run, verbose=args.verbose)
    success = builder.build_all_packages(
        export_local=args.export_local,
        remote=args.remote
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()