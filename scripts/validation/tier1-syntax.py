#!/usr/bin/env python3
"""
Tier 1 Validation: Syntax and Basic File Validation

This script performs basic validation of all SpareTools packages:
- Python syntax validation
- Conan recipe syntax
- Basic file structure validation
- Import validation

Usage:
    python scripts/validation/tier1-syntax.py [--consumer CONSUMER]
"""

import ast
import os
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import get_consumer_packages


class SyntaxValidator:
    """Validates syntax and basic file structure."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "python_files": [],
            "conan_files": [],
            "errors": [],
            "warnings": []
        }

    def log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[TIER1] {message}")

    def validate_python_file(self, file_path: Path) -> bool:
        """Validate Python file syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Parse AST
            ast.parse(source, filename=str(file_path))
            self.results["python_files"].append(str(file_path))
            return True

        except SyntaxError as e:
            self.results["errors"].append(
                f"Python syntax error in {file_path}: {e}"
            )
            return False
        except UnicodeDecodeError:
            self.results["warnings"].append(
                f"Cannot read {file_path} as UTF-8"
            )
            return False
        except Exception as e:
            self.results["errors"].append(
                f"Error validating {file_path}: {e}"
            )
            return False

    def validate_conan_file(self, file_path: Path) -> bool:
        """Validate Conan recipe file."""
        try:
            # Basic Python syntax check first
            if not self.validate_python_file(file_path):
                return False

            # Try to import the module to check for basic issues
            spec = importlib.util.spec_from_file_location("conanfile", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for required ConanFile class
                if not hasattr(module, 'ConanFile'):
                    self.results["warnings"].append(
                        f"No ConanFile class in {file_path}"
                    )
                else:
                    self.results["conan_files"].append(str(file_path))

                return True

        except Exception as e:
            self.results["errors"].append(
                f"Error validating Conan file {file_path}: {e}"
            )
            return False

    def validate_package_directory(self, package_dir: Path) -> None:
        """Validate a package directory."""
        self.log(f"Validating package: {package_dir}")

        # Check for conanfile.py
        conanfile = package_dir / "conanfile.py"
        if conanfile.exists():
            self.validate_conan_file(conanfile)
        else:
            self.results["warnings"].append(
                f"No conanfile.py in {package_dir}"
            )

        # Check for Python files
        for py_file in package_dir.rglob("*.py"):
            if py_file.name != "conanfile.py":  # Already validated
                self.validate_python_file(py_file)

        # Check for test directory
        test_dir = package_dir / "test"
        if not test_dir.exists():
            self.results["warnings"].append(
                f"No test directory in {package_dir}"
            )

    def validate_consumer(self, consumer_name: str) -> None:
        """Validate all packages in a consumer."""
        self.log(f"Validating consumer: {consumer_name}")

        packages = get_consumer_packages(consumer_name)

        if not packages:
            self.results["warnings"].append(
                f"No packages found for consumer {consumer_name}"
            )
            return

        for package in packages:
            package_dir = Path("packages") / "consumers" / consumer_name / package
            if package_dir.exists():
                self.validate_package_directory(package_dir)
            else:
                self.results["errors"].append(
                    f"Package directory not found: {package_dir}"
                )

    def validate_foundation(self) -> None:
        """Validate foundation packages."""
        self.log("Validating foundation packages")

        foundation_packages = [
            "sparetools-base",
            "sparetools-bootstrap",
            "sparetools-shared-dev-tools",
            "sparetools-cpython"
        ]

        for package in foundation_packages:
            package_dir = Path("packages") / "foundation" / package
            if package_dir.exists():
                self.validate_package_directory(package_dir)
            else:
                self.results["warnings"].append(
                    f"Foundation package not found: {package_dir}"
                )

    def run_validation(self, consumers: List[str] = None) -> bool:
        """Run complete validation."""
        print("🔍 Running Tier 1 Validation: Syntax and Basic File Validation")
        print("=" * 60)

        # Validate foundation
        self.validate_foundation()

        # Validate consumers
        consumers_to_check = consumers or ["openssl", "mia", "mcp", "android", "audio", "automotive"]
        for consumer in consumers_to_check:
            self.validate_consumer(consumer)

        # Report results
        print("
Validation Results:")
        print(f"  Python files validated: {len(self.results['python_files'])}")
        print(f"  Conan files validated: {len(self.results['conan_files'])}")
        print(f"  Errors: {len(self.results['errors'])}")
        print(f"  Warnings: {len(self.results['warnings'])}")

        if self.results["errors"]:
            print("\n❌ Errors:")
            for error in self.results["errors"]:
                print(f"  {error}")

        if self.results["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in self.results["warnings"]:
                print(f"  {warning}")

        success = len(self.results["errors"]) == 0
        if success:
            print("\n✅ Tier 1 validation passed!")
        else:
            print(f"\n❌ Tier 1 validation failed with {len(self.results['errors'])} errors")

        return success


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tier 1 Validation: Syntax and Basic File Validation"
    )

    parser.add_argument(
        "--consumer",
        action="append",
        help="Specific consumer to validate"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = SyntaxValidator(verbose=args.verbose)
    success = validator.run_validation(consumers=args.consumer)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()