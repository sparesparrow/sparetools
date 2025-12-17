#!/usr/bin/env python3
"""
Complete Bootstrap Script for SpareTools Monorepo

This script provides the main entry point for bootstrapping the entire
SpareTools ecosystem, including all consumers and foundation packages.

Usage:
    python scripts/bootstrap/complete-bootstrap.py --help
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config, get_consumer_packages


class BootstrapOrchestrator:
    """Orchestrates the complete bootstrap process for SpareTools."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.consumers = ["openssl", "mia", "mcp", "android", "audio", "automotive"]

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[BOOTSTRAP] {message}")

    def validate_environment(self) -> bool:
        """Validate that the environment is ready for bootstrap."""
        self.log("Validating environment...")

        # Check for required tools
        required_tools = ["python", "git"]
        for tool in required_tools:
            if not self._check_tool_available(tool):
                print(f"ERROR: Required tool not found: {tool}")
                return False

        # Check for Conan
        if not self._check_tool_available("conan"):
            print("ERROR: Conan not found. Please install Conan 2.21.0+")
            print("       pip install conan==2.21.0")
            return False

        self.log("Environment validation complete")
        return True

    def _check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available on the system."""
        import shutil
        return shutil.which(tool) is not None

    def discover_consumers(self) -> Dict[str, Dict]:
        """Discover all available consumers and their configurations."""
        self.log("Discovering consumers...")

        consumers = {}
        for consumer_name in self.consumers:
            config = load_consumer_config(consumer_name)
            if config:
                consumers[consumer_name] = config
                self.log(f"Found consumer: {consumer_name}")
            else:
                self.log(f"Consumer config not found: {consumer_name}")

        return consumers

    def validate_consumers(self, consumers: Dict[str, Dict]) -> List[str]:
        """Validate consumer configurations and return issues."""
        self.log("Validating consumer configurations...")

        issues = []
        for name, config in consumers.items():
            # Check required fields
            required_fields = ["name", "packages"]
            for field in required_fields:
                if field not in config:
                    issues.append(f"Consumer {name}: missing required field '{field}'")

            # Check packages exist
            packages = config.get("packages", [])
            if packages is None:
                packages = []
            for package in packages:
                package_dir = Path("packages") / "consumers" / name / package
                if not package_dir.exists():
                    issues.append(f"Consumer {name}: package directory not found: {package}")

        return issues

    def bootstrap_foundation(self) -> bool:
        """Bootstrap foundation packages."""
        self.log("Bootstrapping foundation packages...")

        foundation_packages = [
            "sparetools-base",
            "sparetools-bootstrap",
            "sparetools-shared-dev-tools",
            "sparetools-cpython"
        ]

        for package in foundation_packages:
            self.log(f"Building foundation package: {package}")
            if not self._build_package("foundation", package):
                print(f"ERROR: Failed to build foundation package: {package}")
                return False

        return True

    def bootstrap_consumers(self, consumers: Dict[str, Dict]) -> bool:
        """Bootstrap consumer packages."""
        self.log("Bootstrapping consumer packages...")

        for consumer_name, config in consumers.items():
            self.log(f"Bootstrapping consumer: {consumer_name}")

            packages = config.get("packages", [])
            for package in packages:
                self.log(f"Building consumer package: {consumer_name}/{package}")
                if not self._build_package(f"consumers/{consumer_name}", package):
                    print(f"ERROR: Failed to build consumer package: {consumer_name}/{package}")
                    return False

        return True

    def _build_package(self, package_path: str, package_name: str) -> bool:
        """Build a single package."""
        try:
            import subprocess

            # Change to package directory
            package_dir = Path("packages") / package_path / package_name
            if not package_dir.exists():
                self.log(f"Package directory not found: {package_dir}")
                return False

            os.chdir(package_dir)

            # Create and build package
            cmd = ["conan", "create", ".", "--build=missing"]
            if self.verbose:
                cmd.append("-v")

            result = subprocess.run(cmd, capture_output=not self.verbose)
            success = result.returncode == 0

            if not success and not self.verbose:
                print(f"Build output: {result.stdout.decode()}")
                print(f"Build errors: {result.stderr.decode()}")

            # Return to root directory
            os.chdir(Path(__file__).parent.parent.parent)

            return success

        except Exception as e:
            print(f"ERROR: Exception during package build: {e}")
            return False

    def run_validation(self) -> bool:
        """Run validation suite after bootstrap."""
        self.log("Running validation suite...")

        # Import and run validation scripts
        try:
            # Run basic validation
            self._run_validation_script("validation/audit-conan-recipes.py")
            self._run_validation_script("validation/validate-openssl-compatibility.py")

            return True

        except Exception as e:
            print(f"ERROR: Validation failed: {e}")
            return False

    def _run_validation_script(self, script_path: str) -> None:
        """Run a validation script."""
        script = Path("scripts") / script_path
        if script.exists():
            self.log(f"Running validation: {script_path}")
            os.system(f"python {script}")
        else:
            self.log(f"Validation script not found: {script_path}")

    def generate_summary(self, consumers: Dict[str, Dict], issues: List[str]) -> None:
        """Generate bootstrap summary."""
        print("\n" + "="*60)
        print("BOOTSTRAP SUMMARY")
        print("="*60)

        print(f"Consumers discovered: {len(consumers)}")
        for name in consumers.keys():
            print(f"  ✓ {name}")

        if issues:
            print(f"\nIssues found: {len(issues)}")
            for issue in issues:
                print(f"  ✗ {issue}")
        else:
            print("\n✓ No issues found")

        print("\nNext steps:")
        print("  1. Run 'conan list \"sparetools-*\"' to see all packages")
        print("  2. Use consumer templates: python bootstrap-obd.py --template=<type>")
        print("  3. Run validation: python scripts/validation/audit-conan-recipes.py")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete Bootstrap Script for SpareTools Monorepo"
    )

    parser.add_argument(
        "--consumers",
        nargs="*",
        help="Specific consumers to bootstrap (default: all)"
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip post-bootstrap validation"
    )

    parser.add_argument(
        "--foundation-only",
        action="store_true",
        help="Bootstrap only foundation packages"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Initialize bootstrap orchestrator
    bootstrap = BootstrapOrchestrator(verbose=args.verbose)

    # Validate environment
    if not bootstrap.validate_environment():
        sys.exit(1)

    # Discover consumers
    consumers = bootstrap.discover_consumers()

    # Filter consumers if specified
    if args.consumers:
        consumers = {k: v for k, v in consumers.items() if k in args.consumers}

    # Validate consumers
    issues = bootstrap.validate_consumers(consumers)
    if issues:
        print("Consumer validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("Continuing with available consumers...")

    # Bootstrap foundation
    if not bootstrap.bootstrap_foundation():
        print("ERROR: Foundation bootstrap failed")
        sys.exit(1)

    # Bootstrap consumers (unless foundation-only)
    if not args.foundation_only:
        if not bootstrap.bootstrap_consumers(consumers):
            print("ERROR: Consumer bootstrap failed")
            sys.exit(1)

    # Run validation (unless skipped)
    if not args.skip_validation:
        if not bootstrap.run_validation():
            print("WARNING: Validation failed, but bootstrap completed")

    # Generate summary
    bootstrap.generate_summary(consumers, issues)

    print("\n✅ Bootstrap complete!")


if __name__ == "__main__":
    main()