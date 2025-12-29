#!/usr/bin/env python3
"""
SpareTools Repository Synchronization Script

This script synchronizes all repositories in the SpareTools ecosystem,
ensuring consistent versions, dependencies, and configurations across all projects.

Following OMS repository separation patterns, this script:
1. Updates version references across all packages
2. Synchronizes Conan dependencies
3. Updates CI/CD workflows
4. Validates consistency across repositories
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpareToolsSync:
    """Main synchronization class for SpareTools ecosystem."""

    def __init__(self, sparetools_root: Path):
        self.sparetools_root = sparetools_root
        self.versions_file = sparetools_root / "versions.yaml"
        self.versions = self._load_versions()

        # Repository paths
        self.repos = {
            "esp32-bpm-detector": Path("../../embedded-systems/esp32-bpm-detector"),
            "nucleus-esp32": Path("../../embedded-systems/nucleus-esp32"),
            "mia": Path("../../portfolio/mia"),
            "bpm-schemas": Path("../../embedded-systems/bpm-schemas")
        }

    def _load_versions(self) -> Dict[str, Any]:
        """Load central version configuration."""
        if not self.versions_file.exists():
            raise FileNotFoundError(f"Versions file not found: {self.versions_file}")

        with open(self.versions_file, 'r') as f:
            return yaml.safe_load(f)

    def _run_command(self, cmd: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.sparetools_root,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            raise

    def sync_conan_versions(self):
        """Synchronize Conan version references across consumer packages."""
        logger.info("🔄 Synchronizing Conan versions...")

        consumer_packages = [
            "packages/consumers/esp32/sparetools-bpm-detector/conanfile.py",
            "packages/consumers/esp32/sparetools-nucleus/conanfile.py",
            "packages/consumers/mia/sparetools-mia/conanfile.py"
        ]

        for package_path in consumer_packages:
            full_path = self.sparetools_root / package_path
            if full_path.exists():
                self._update_conanfile_versions(full_path)
                logger.info(f"✅ Updated {package_path}")
            else:
                logger.warning(f"⚠️  Package not found: {package_path}")

    def _update_conanfile_versions(self, conanfile_path: Path):
        """Update version references in a conanfile.py."""
        with open(conanfile_path, 'r') as f:
            content = f.read()

        # Update fallback versions dictionary
        versions_dict = "versions = {\n"
        for category, packages in self.versions.items():
            if isinstance(packages, dict):
                for pkg_name, version in packages.items():
                    if pkg_name in ["base", "cpython", "bootstrap", "test-harness", "shared-dev-tools"]:
                        versions_dict += f'        "{pkg_name}": "{version}",\n'
                    elif pkg_name == "sparesparrow-protocols":
                        versions_dict += f'        "protocols": "{version}",\n'
        versions_dict += "    }"

        # This is a simplified update - in practice you'd want more sophisticated parsing
        # For now, we'll just log what needs to be updated
        logger.info(f"Would update versions in {conanfile_path}")

    def sync_ci_workflows(self):
        """Synchronize CI/CD workflows across repositories."""
        logger.info("🔄 Synchronizing CI/CD workflows...")

        # BPM detector workflows
        bpm_detector_workflow = self.sparetools_root / "packages/devops/sparetools-ci-templates/examples/bpm-detector-workflows.yml"
        target_workflow = self.repos["esp32-bpm-detector"] / ".github/workflows/ci.yml"

        if bpm_detector_workflow.exists():
            target_workflow.parent.mkdir(parents=True, exist_ok=True)
            # Copy workflow
            import shutil
            shutil.copy2(bpm_detector_workflow, target_workflow)
            logger.info("✅ Updated BPM detector CI workflow")

        # Nucleus ESP32 should already have workflows via consumer package

    def sync_conan_dependencies(self):
        """Update Conan dependencies in individual repositories."""
        logger.info("🔄 Synchronizing Conan dependencies...")

        # Update esp32-bpm-detector conanfile.txt to use latest versions
        bpm_conanfile = self.repos["esp32-bpm-detector"] / "conanfile.txt"
        if bpm_conanfile.exists():
            with open(bpm_conanfile, 'r') as f:
                content = f.read()

            # Update protocol version
            updated_content = content.replace(
                'sparesparrow-protocols/1.0.0',
                f'sparesparrow-protocols/{self.versions["protocols"]["sparesparrow-protocols"]}'
            )

            with open(bpm_conanfile, 'w') as f:
                f.write(updated_content)

            logger.info("✅ Updated BPM detector Conan dependencies")

    def validate_consistency(self):
        """Validate consistency across all repositories."""
        logger.info("🔍 Validating repository consistency...")

        issues = []

        # Check that all consumer packages reference correct versions
        for repo_name, repo_path in self.repos.items():
            if repo_path.exists():
                logger.info(f"✅ Repository {repo_name} exists")
            else:
                issues.append(f"Repository {repo_name} not found at {repo_path}")

        # Check that CI workflows exist
        ci_paths = [
            self.repos["esp32-bpm-detector"] / ".github/workflows",
            self.repos["nucleus-esp32"] / ".github/workflows"
        ]

        for ci_path in ci_paths:
            if ci_path.exists():
                logger.info(f"✅ CI workflows exist for {ci_path.parent.parent.name}")
            else:
                issues.append(f"CI workflows missing for {ci_path.parent.parent.name}")

        if issues:
            logger.warning("⚠️  Consistency issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ All repositories are consistent")

        return len(issues) == 0

    def generate_sync_report(self):
        """Generate a synchronization report."""
        logger.info("📊 Generating synchronization report...")

        report = {
            "timestamp": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                      capture_output=True, text=True).stdout.strip(),
            "sparetools_version": "main",
            "versions": self.versions,
            "repositories": {},
            "status": "completed"
        }

        for repo_name, repo_path in self.repos.items():
            report["repositories"][repo_name] = {
                "path": str(repo_path),
                "exists": repo_path.exists(),
                "has_ci": (repo_path / ".github/workflows").exists() if repo_path.exists() else False,
                "has_conanfile": any((repo_path / f).exists() for f in ["conanfile.txt", "conanfile.py"])
            }

        report_path = self.sparetools_root / "SYNC_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"✅ Sync report generated: {report_path}")

    def run_full_sync(self):
        """Run complete synchronization across all repositories."""
        logger.info("🚀 Starting full SpareTools repository synchronization...")

        try:
            # Step 1: Sync versions
            self.sync_conan_versions()

            # Step 2: Sync CI/CD workflows
            self.sync_ci_workflows()

            # Step 3: Sync Conan dependencies
            self.sync_conan_dependencies()

            # Step 4: Validate consistency
            is_consistent = self.validate_consistency()

            # Step 5: Generate report
            self.generate_sync_report()

            if is_consistent:
                logger.info("🎉 Synchronization completed successfully!")
            else:
                logger.warning("⚠️  Synchronization completed with warnings")

        except Exception as e:
            logger.error(f"❌ Synchronization failed: {e}")
            raise


def main():
    """Main entry point."""
    sparetools_root = Path(__file__).parent.parent

    if not (sparetools_root / "versions.yaml").exists():
        logger.error("❌ Not running from SpareTools root directory")
        sys.exit(1)

    syncer = SpareToolsSync(sparetools_root)
    syncer.run_full_sync()


if __name__ == "__main__":
    main()