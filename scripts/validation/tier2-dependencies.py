#!/usr/bin/env python3
"""
Tier 2 Validation: Dependency Resolution and Compatibility

Validates dependency resolution, version compatibility, and cross-consumer
dependencies to ensure packages can be built and consumed together.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config, get_consumer_packages, validate_consumer_setup


class DependencyValidator:
    """Validates dependency resolution and compatibility."""

    def __init__(self, verbose: bool = False, offline: bool = False):
        """Initialize dependency validator.

        Args:
            verbose: Enable verbose output
            offline: Work offline (don't access remote repos)
        """
        self.verbose = verbose
        self.offline = offline
        self.results = {
            "dependency_resolution": {},
            "version_compatibility": {},
            "cross_consumer_deps": {},
            "circular_dependencies": [],
            "missing_dependencies": [],
            "conflicting_versions": []
        }

    def log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[TIER2] {message}")

    def validate_dependencies(self, consumers: List[str] = None) -> bool:
        """Run complete dependency validation.

        Args:
            consumers: Specific consumers to validate

        Returns:
            True if all validations pass
        """
        print("🔍 Running Tier 2 Validation: Dependency Resolution")

        consumers_to_check = consumers or ["openssl", "mia", "mcp", "android", "audio", "automotive"]

        # Validate consumer configurations
        self._validate_consumer_configs(consumers_to_check)

        # Test dependency resolution
        self._validate_dependency_resolution(consumers_to_check)

        # Check version compatibility
        self._validate_version_compatibility(consumers_to_check)

        # Validate cross-consumer dependencies
        self._validate_cross_consumer_dependencies(consumers_to_check)

        # Check for circular dependencies
        self._check_circular_dependencies(consumers_to_check)

        # Report results
        self._report_results()

        # Return success if no critical issues
        critical_issues = (
            len(self.results["missing_dependencies"]) +
            len(self.results["conflicting_versions"]) +
            len(self.results["circular_dependencies"])
        )

        success = critical_issues == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} - {critical_issues} critical issues found")

        return success

    def _validate_consumer_configs(self, consumers: List[str]) -> None:
        """Validate consumer configurations."""
        self.log("Validating consumer configurations...")

        for consumer in consumers:
            result = validate_consumer_setup(consumer)
            if not result["config_valid"]:
                self.results["missing_dependencies"].append({
                    "type": "consumer_config",
                    "consumer": consumer,
                    "issue": "Invalid or missing .consumer.yaml"
                })

    def _validate_dependency_resolution(self, consumers: List[str]) -> None:
        """Test dependency resolution for each consumer."""
        self.log("Testing dependency resolution...")

        for consumer in consumers:
            config = load_consumer_config(consumer)
            if not config:
                continue

            packages = config.get("packages", [])
            foundation_deps = config.get("dependencies", {}).get("foundation", [])

            # Test foundation dependencies
            for dep in foundation_deps:
                if not self._check_package_exists(dep):
                    self.results["missing_dependencies"].append({
                        "type": "foundation_dependency",
                        "consumer": consumer,
                        "dependency": dep,
                        "required_by": packages
                    })

            # Test consumer package dependencies
            for package in packages:
                package_deps = self._get_package_dependencies(package)
                for dep in package_deps:
                    if not self._check_package_exists(dep):
                        self.results["missing_dependencies"].append({
                            "type": "package_dependency",
                            "consumer": consumer,
                            "package": package,
                            "dependency": dep
                        })

    def _validate_version_compatibility(self, consumers: List[str]) -> None:
        """Validate version compatibility across consumers."""
        self.log("Validating version compatibility...")

        # Collect all package versions used across consumers
        package_versions: Dict[str, Set[str]] = {}

        for consumer in consumers:
            config = load_consumer_config(consumer)
            if not config:
                continue

            # Check foundation dependencies
            foundation_deps = config.get("dependencies", {}).get("foundation", [])
            for dep in foundation_deps:
                package_name, version = self._parse_package_spec(dep)
                if package_name not in package_versions:
                    package_versions[package_name] = set()
                package_versions[package_name].add(version)

        # Check for version conflicts
        for package_name, versions in package_versions.items():
            if len(versions) > 1:
                self.results["conflicting_versions"].append({
                    "package": package_name,
                    "versions": list(versions),
                    "consumers": self._find_consumers_using_package(package_name, consumers)
                })

    def _validate_cross_consumer_dependencies(self, consumers: List[str]) -> None:
        """Validate cross-consumer dependencies."""
        self.log("Validating cross-consumer dependencies...")

        consumer_deps = {
            "openssl": [],  # Foundation for crypto
            "mia": ["openssl"],  # Uses OpenSSL for security
            "mcp": ["openssl"],  # May use OpenSSL for secure MCP
            "android": ["openssl"],  # Uses OpenSSL in JNI
            "audio": [],  # Independent
            "automotive": ["mia"]  # Extends MIA
        }

        for consumer, required_consumers in consumer_deps.items():
            if consumer not in consumers:
                continue

            for required_consumer in required_consumers:
                if required_consumer not in consumers:
                    continue

                # Check if required consumer's packages are accessible
                required_config = load_consumer_config(required_consumer)
                if not required_config:
                    self.results["cross_consumer_deps"][f"{consumer}->{required_consumer}"] = {
                        "status": "missing_config",
                        "issue": f"{required_consumer} consumer config not found"
                    }
                    continue

                # Validate that required packages can be imported
                required_packages = required_config.get("packages", [])
                for package in required_packages:
                    if not self._check_cross_consumer_access(consumer, required_consumer, package):
                        self.results["cross_consumer_deps"][f"{consumer}->{required_consumer}"] = {
                            "status": "access_denied",
                            "issue": f"{consumer} cannot access {package} from {required_consumer}"
                        }

    def _check_circular_dependencies(self, consumers: List[str]) -> None:
        """Check for circular dependencies between consumers."""
        self.log("Checking for circular dependencies...")

        # Simple circular dependency check
        # In a more complex system, this would use graph algorithms

        consumer_deps = {
            "openssl": [],
            "mia": ["openssl"],
            "mcp": ["openssl"],
            "android": ["openssl"],
            "audio": [],
            "automotive": ["mia"]
        }

        # Check for direct circular dependencies
        for consumer, deps in consumer_deps.items():
            for dep in deps:
                if dep in consumer_deps and consumer in consumer_deps[dep]:
                    self.results["circular_dependencies"].append({
                        "consumers": [consumer, dep],
                        "type": "direct"
                    })

    def _check_package_exists(self, package_spec: str) -> bool:
        """Check if a package exists in the monorepo.

        Args:
            package_spec: Package specification (name/version)

        Returns:
            True if package exists
        """
        package_name, _ = self._parse_package_spec(package_spec)

        # Check foundation packages
        foundation_path = Path("packages") / "foundation" / package_name
        if foundation_path.exists():
            return True

        # Check consumer packages
        for consumer_dir in (Path("packages") / "consumers").iterdir():
            if consumer_dir.is_dir():
                package_path = consumer_dir / package_name
                if package_path.exists():
                    return True

        return False

    def _get_package_dependencies(self, package_name: str) -> List[str]:
        """Get dependencies for a package.

        Args:
            package_name: Name of package

        Returns:
            List of dependency specifications
        """
        # This would parse conanfile.py to extract dependencies
        # For now, return known dependencies
        known_deps = {
            "sparetools-openssl": ["sparetools-base/2.0.0"],
            "sparetools-mia": ["sparetools-base/2.0.0", "sparetools-openssl/3.3.2"],
            "sparetools-mcp-orchestrator": ["sparetools-base/2.0.0"],
            "sparetools-android": ["sparetools-base/2.0.0", "sparetools-openssl/3.3.2"]
        }

        return known_deps.get(package_name, [])

    def _parse_package_spec(self, package_spec: str) -> Tuple[str, str]:
        """Parse package specification into name and version.

        Args:
            package_spec: Package spec like "sparetools-base/2.0.0"

        Returns:
            Tuple of (package_name, version)
        """
        if "/" in package_spec:
            name, version = package_spec.split("/", 1)
            return name, version
        else:
            return package_spec, ""

    def _find_consumers_using_package(self, package_name: str, consumers: List[str]) -> List[str]:
        """Find consumers that use a specific package.

        Args:
            package_name: Package to search for
            consumers: List of consumers to check

        Returns:
            List of consumers using the package
        """
        using_consumers = []

        for consumer in consumers:
            config = load_consumer_config(consumer)
            if not config:
                continue

            # Check foundation dependencies
            foundation_deps = config.get("dependencies", {}).get("foundation", [])
            for dep in foundation_deps:
                dep_name, _ = self._parse_package_spec(dep)
                if dep_name == package_name:
                    using_consumers.append(consumer)
                    break

        return using_consumers

    def _check_cross_consumer_access(self, from_consumer: str, to_consumer: str, package: str) -> bool:
        """Check if one consumer can access another's package.

        Args:
            from_consumer: Consumer requesting access
            to_consumer: Consumer owning the package
            package: Package name

        Returns:
            True if access is allowed
        """
        # In current architecture, all consumers can access foundation packages
        # and their own packages. Cross-consumer access requires explicit configuration.

        if to_consumer == "openssl":  # OpenSSL is widely used
            return True

        # For now, allow access if explicitly configured
        # In a more complex system, this would check access control policies
        return from_consumer == to_consumer

    def _report_results(self) -> None:
        """Report validation results."""
        print("\nDependency Validation Results:")

        if self.results["missing_dependencies"]:
            print(f"❌ Missing Dependencies: {len(self.results['missing_dependencies'])}")
            for dep in self.results["missing_dependencies"]:
                print(f"  - {dep['type']}: {dep.get('consumer', 'unknown')} -> {dep.get('dependency', 'unknown')}")

        if self.results["conflicting_versions"]:
            print(f"❌ Version Conflicts: {len(self.results['conflicting_versions'])}")
            for conflict in self.results["conflicting_versions"]:
                print(f"  - {conflict['package']}: {', '.join(conflict['versions'])} (used by {', '.join(conflict['consumers'])})")

        if self.results["circular_dependencies"]:
            print(f"❌ Circular Dependencies: {len(self.results['circular_dependencies'])}")
            for cycle in self.results["circular_dependencies"]:
                print(f"  - {cycle['type']}: {' -> '.join(cycle['consumers'])}")

        if self.results["cross_consumer_deps"]:
            print(f"⚠️  Cross-Consumer Issues: {len(self.results['cross_consumer_deps'])}")
            for dep, info in self.results["cross_consumer_deps"].items():
                print(f"  - {dep}: {info['issue']}")

        # Summary
        total_issues = (
            len(self.results["missing_dependencies"]) +
            len(self.results["conflicting_versions"]) +
            len(self.results["circular_dependencies"])
        )

        if total_issues == 0:
            print("✅ No dependency issues found")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tier 2 Validation: Dependency Resolution and Compatibility"
    )

    parser.add_argument(
        "--consumer",
        action="append",
        help="Specific consumer to validate"
    )

    parser.add_argument(
        "--offline",
        action="store_true",
        help="Work offline (don't access remote repos)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = DependencyValidator(verbose=args.verbose, offline=args.offline)
    success = validator.validate_dependencies(consumers=args.consumer)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()