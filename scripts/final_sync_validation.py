#!/usr/bin/env python3
"""
Final Synchronization Validation Script

Validates that all repositories are properly synchronized with SpareTools
following the OMS repository separation patterns.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncValidator:
    """Validates repository synchronization status."""

    def __init__(self, sparetools_root: Path):
        self.sparetools_root = sparetools_root
        self.versions = self._load_versions()

        # Repository configurations
        self.repos = {
            "esp32-bpm-detector": {
                "path": Path("../../embedded-systems/esp32-bpm-detector"),
                "consumer_package": "sparetools-bpm-detector/0.1.0",
                "expected_protocols": ["sparesparrow-protocols/1.0.0"],
                "type": "esp32"
            },
            "nucleus-esp32": {
                "path": Path("../../embedded-systems/nucleus-esp32"),
                "consumer_package": "sparetools-nucleus/0.1.0",
                "expected_protocols": [],
                "type": "esp32"
            },
            "mia": {
                "path": Path("../../portfolio/mia"),
                "consumer_package": "sparetools-mia/2.0.0",
                "expected_protocols": ["sparesparrow-protocols/1.0.0", "sparetools-embedded/1.0.0"],
                "type": "mia"
            },
            "bpm-schemas": {
                "path": Path("../../embedded-systems/bpm-schemas"),
                "consumer_package": None,
                "expected_protocols": [],
                "type": "schemas"
            }
        }

    def _load_versions(self) -> Dict[str, Any]:
        """Load central version configuration."""
        versions_file = self.sparetools_root / "versions.yaml"
        if not versions_file.exists():
            raise FileNotFoundError(f"Versions file not found: {versions_file}")

        with open(versions_file, 'r') as f:
            return yaml.safe_load(f)

    def validate_repository_structure(self) -> Dict[str, Any]:
        """Validate that all repositories have the expected structure."""
        logger.info("🔍 Validating repository structures...")

        results = {}

        for repo_name, repo_config in self.repos.items():
            repo_path = repo_config["path"]
            result = {
                "exists": repo_path.exists(),
                "has_conanfile": False,
                "has_ci_workflows": False,
                "references_consumer": False,
                "uses_correct_protocols": False,
                "status": "unknown"
            }

            if not repo_path.exists():
                result["status"] = "missing"
                results[repo_name] = result
                continue

            # Check for conanfile
            conanfile_paths = [repo_path / "conanfile.txt", repo_path / "conanfile.py"]
            result["has_conanfile"] = any(p.exists() for p in conanfile_paths)

            # Check for CI workflows
            ci_path = repo_path / ".github" / "workflows"
            result["has_ci_workflows"] = ci_path.exists() and len(list(ci_path.glob("*.yml"))) > 0

            # Check conanfile content (prefer .py over .txt for Python packages)
            if result["has_conanfile"]:
                conanfile_content = ""
                # Prefer .py files for Python-based projects
                for conanfile_path in sorted(conanfile_paths, key=lambda x: 0 if x.suffix == '.py' else 1):
                    if conanfile_path.exists():
                        with open(conanfile_path, 'r') as f:
                            conanfile_content = f.read()
                        break

                # Check if it references the consumer package
                if repo_config["consumer_package"]:
                    consumer_name = repo_config["consumer_package"].split("/")[0]
                    result["references_consumer"] = consumer_name in conanfile_content

                # Check protocol dependencies
                result["uses_correct_protocols"] = all(
                    protocol in conanfile_content
                    for protocol in repo_config["expected_protocols"]
                )

            # Determine status
            if result["exists"] and result["has_conanfile"] and result["has_ci_workflows"]:
                if repo_config["consumer_package"] and result["references_consumer"]:
                    result["status"] = "fully_synced"
                elif not repo_config["consumer_package"]:
                    result["status"] = "fully_synced"
                else:
                    result["status"] = "needs_consumer_reference"
            elif result["exists"]:
                result["status"] = "partially_synced"
            else:
                result["status"] = "missing"

            results[repo_name] = result

        return results

    def validate_consumer_packages(self) -> Dict[str, Any]:
        """Validate that consumer packages are properly structured."""
        logger.info("🔍 Validating consumer packages...")

        results = {}
        consumers_dir = self.sparetools_root / "packages" / "consumers"

        for repo_name, repo_config in self.repos.items():
            if not repo_config["consumer_package"]:
                continue

            consumer_name = repo_config["consumer_package"].split("/")[0]
            consumer_path = consumers_dir / repo_config["type"] / consumer_name

            result = {
                "exists": consumer_path.exists(),
                "has_conanfile": False,
                "has_source": False,
                "has_tests": False,
                "has_docs": False,
                "status": "unknown"
            }

            if not consumer_path.exists():
                result["status"] = "missing"
                results[repo_name] = result
                continue

            # Check components
            result["has_conanfile"] = (consumer_path / "conanfile.py").exists()
            result["has_source"] = (consumer_path / "src").exists() and len(list((consumer_path / "src").rglob("*"))) > 0
            result["has_tests"] = (consumer_path / "test").exists() or (consumer_path / "tests").exists()
            result["has_docs"] = (consumer_path / "README.md").exists()

            # Determine status
            required_components = ["has_conanfile", "has_source", "has_docs"]
            if all(result[comp] for comp in required_components):
                result["status"] = "complete"
            elif result["has_conanfile"]:
                result["status"] = "basic"
            else:
                result["status"] = "incomplete"

            results[repo_name] = result

        return results

    def validate_version_consistency(self) -> Dict[str, Any]:
        """Validate version consistency across all components."""
        logger.info("🔍 Validating version consistency...")

        results = {}

        # Check that consumer package versions match central configuration
        for repo_name, repo_config in self.repos.items():
            if not repo_config["consumer_package"]:
                continue

            consumer_name = repo_config["consumer_package"].split("/")[0]
            expected_version = repo_config["consumer_package"].split("/")[1]

            consumer_path = self.sparetools_root / "packages" / "consumers" / repo_config["type"] / consumer_name
            conanfile_path = consumer_path / "conanfile.py"

            if conanfile_path.exists():
                with open(conanfile_path, 'r') as f:
                    content = f.read()

                # Extract version from conanfile
                version_line = [line for line in content.split('\n') if line.strip().startswith('version = ')]
                if version_line:
                    actual_version = version_line[0].split('"')[1]
                    results[repo_name] = {
                        "expected": expected_version,
                        "actual": actual_version,
                        "consistent": expected_version == actual_version
                    }
                else:
                    results[repo_name] = {
                        "expected": expected_version,
                        "actual": "not_found",
                        "consistent": False
                    }
            else:
                results[repo_name] = {
                    "expected": expected_version,
                    "actual": "no_conanfile",
                    "consistent": False
                }

        return results

    def generate_sync_report(self) -> Dict[str, Any]:
        """Generate comprehensive synchronization report."""
        logger.info("📊 Generating comprehensive sync report...")

        report = {
            "timestamp": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                      capture_output=True, text=True).stdout.strip(),
            "sparetools_version": "main",
            "validation_results": {
                "repository_structure": self.validate_repository_structure(),
                "consumer_packages": self.validate_consumer_packages(),
                "version_consistency": self.validate_version_consistency()
            },
            "summary": {}
        }

        # Generate summary
        repo_results = report["validation_results"]["repository_structure"]
        consumer_results = report["validation_results"]["consumer_packages"]
        version_results = report["validation_results"]["version_consistency"]

        total_repos = len(repo_results)
        fully_synced = sum(1 for r in repo_results.values() if r["status"] == "fully_synced")
        partially_synced = sum(1 for r in repo_results.values() if r["status"] == "partially_synced")
        missing = sum(1 for r in repo_results.values() if r["status"] == "missing")

        consumer_complete = sum(1 for r in consumer_results.values() if r["status"] == "complete")
        total_consumers = len(consumer_results)

        version_consistent = sum(1 for r in version_results.values() if r["consistent"])

        summary = {
            "repositories": {
                "total": total_repos,
                "fully_synced": fully_synced,
                "partially_synced": partially_synced,
                "missing": missing,
                "sync_percentage": (fully_synced / total_repos * 100) if total_repos > 0 else 0
            },
            "consumers": {
                "total": total_consumers,
                "complete": consumer_complete,
                "completion_percentage": (consumer_complete / total_consumers * 100) if total_consumers > 0 else 0
            },
            "versions": {
                "total": len(version_results),
                "consistent": version_consistent,
                "consistency_percentage": (version_consistent / len(version_results) * 100) if version_results else 100
            }
        }

        summary["overall_status"] = "synced" if (
            summary["repositories"]["sync_percentage"] >= 80 and
            summary["consumers"]["completion_percentage"] >= 80 and
            summary["versions"]["consistency_percentage"] >= 100
        ) else "needs_attention"

        report["summary"] = summary

        # Save report
        report_path = self.sparetools_root / "SYNC_VALIDATION_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"✅ Sync validation report generated: {report_path}")

        return report

    def run_validation(self):
        """Run complete validation suite."""
        logger.info("🚀 Starting SpareTools synchronization validation...")

        try:
            report = self.generate_sync_report()

            summary = report["summary"]
            logger.info("📊 Validation Summary:")
            logger.info(f"  Repositories: {summary['repositories']['fully_synced']}/{summary['repositories']['total']} fully synced ({summary['repositories']['sync_percentage']:.1f}%)")
            logger.info(f"  Consumers: {summary['consumers']['complete']}/{summary['consumers']['total']} complete ({summary['consumers']['completion_percentage']:.1f}%)")
            logger.info(f"  Versions: {summary['versions']['consistent']}/{summary['versions']['total']} consistent ({summary['versions']['consistency_percentage']:.1f}%)")

            if summary["overall_status"] == "synced":
                logger.info("🎉 All repositories are properly synchronized!")
            else:
                logger.warning("⚠️ Some repositories need attention")
                logger.warning("Run the individual sync scripts for repositories that need updates")

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            raise


def main():
    """Main entry point."""
    sparetools_root = Path(__file__).parent.parent

    if not (sparetools_root / "versions.yaml").exists():
        logger.error("❌ Not running from SpareTools root directory")
        sys.exit(1)

    validator = SyncValidator(sparetools_root)
    validator.run_validation()


if __name__ == "__main__":
    main()