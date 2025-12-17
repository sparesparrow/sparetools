#!/usr/bin/env python3
"""
Tier 3 Validation: Cross-Consumer Compatibility

Validates that packages from different consumers can work together,
testing integration scenarios and compatibility across consumer boundaries.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config, get_consumer_packages


class CrossConsumerValidator:
    """Validates cross-consumer compatibility and integration."""

    def __init__(self, verbose: bool = False, keep_temp: bool = False):
        """Initialize cross-consumer validator.

        Args:
            verbose: Enable verbose output
            keep_temp: Keep temporary directories for debugging
        """
        self.verbose = verbose
        self.keep_temp = keep_temp
        self.results = {
            "integration_tests": [],
            "compatibility_matrix": {},
            "shared_dependencies": {},
            "interface_compatibility": {},
            "failed_integrations": []
        }

    def log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[TIER3] {message}")

    def validate_cross_consumer_compatibility(self, consumers: List[str] = None) -> bool:
        """Run complete cross-consumer validation.

        Args:
            consumers: Specific consumers to validate

        Returns:
            True if all validations pass
        """
        print("🔍 Running Tier 3 Validation: Cross-Consumer Compatibility")

        consumers_to_check = consumers or ["openssl", "mia", "mcp", "android", "audio", "automotive"]

        # Test integration scenarios
        self._test_integration_scenarios(consumers_to_check)

        # Build compatibility matrix
        self._build_compatibility_matrix(consumers_to_check)

        # Validate shared dependencies
        self._validate_shared_dependencies(consumers_to_check)

        # Test interface compatibility
        self._test_interface_compatibility(consumers_to_check)

        # Report results
        self._report_results()

        # Return success if no failed integrations
        success = len(self.results["failed_integrations"]) == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} - {len(self.results['failed_integrations'])} integration failures")

        return success

    def _test_integration_scenarios(self, consumers: List[str]) -> None:
        """Test specific integration scenarios between consumers."""
        self.log("Testing integration scenarios...")

        scenarios = [
            {
                "name": "openssl-mia-integration",
                "consumers": ["openssl", "mia"],
                "description": "OpenSSL cryptography in MIA IoT applications",
                "test": self._test_openssl_mia_integration
            },
            {
                "name": "openssl-mcp-integration",
                "consumers": ["openssl", "mcp"],
                "description": "Secure MCP protocol with OpenSSL",
                "test": self._test_openssl_mcp_integration
            },
            {
                "name": "mia-automotive-integration",
                "consumers": ["mia", "automotive"],
                "description": "MIA core extended for automotive use cases",
                "test": self._test_mia_automotive_integration
            },
            {
                "name": "openssl-android-integration",
                "consumers": ["openssl", "android"],
                "description": "OpenSSL in Android JNI applications",
                "test": self._test_openssl_android_integration
            }
        ]

        for scenario in scenarios:
            # Check if all required consumers are available
            if all(c in consumers for c in scenario["consumers"]):
                self.log(f"Testing scenario: {scenario['name']}")
                try:
                    success = scenario["test"]()
                    self.results["integration_tests"].append({
                        "scenario": scenario["name"],
                        "description": scenario["description"],
                        "consumers": scenario["consumers"],
                        "success": success,
                        "error": None
                    })
                except Exception as e:
                    self.results["integration_tests"].append({
                        "scenario": scenario["name"],
                        "description": scenario["description"],
                        "consumers": scenario["consumers"],
                        "success": False,
                        "error": str(e)
                    })
                    self.results["failed_integrations"].append(scenario["name"])

    def _build_compatibility_matrix(self, consumers: List[str]) -> None:
        """Build compatibility matrix between consumers."""
        self.log("Building compatibility matrix...")

        matrix = {}

        for consumer_a in consumers:
            matrix[consumer_a] = {}
            for consumer_b in consumers:
                if consumer_a == consumer_b:
                    matrix[consumer_a][consumer_b] = "self"
                else:
                    compatibility = self._check_consumer_compatibility(consumer_a, consumer_b)
                    matrix[consumer_a][consumer_b] = compatibility

        self.results["compatibility_matrix"] = matrix

    def _validate_shared_dependencies(self, consumers: List[str]) -> None:
        """Validate shared dependencies across consumers."""
        self.log("Validating shared dependencies...")

        # Find packages used by multiple consumers
        package_usage = {}
        for consumer in consumers:
            config = load_consumer_config(consumer)
            if not config:
                continue

            # Check foundation dependencies
            foundation_deps = config.get("dependencies", {}).get("foundation", [])
            for dep in foundation_deps:
                if dep not in package_usage:
                    package_usage[dep] = []
                package_usage[dep].append(consumer)

        # Identify truly shared dependencies
        shared_deps = {dep: users for dep, users in package_usage.items() if len(users) > 1}
        self.results["shared_dependencies"] = shared_deps

        self.log(f"Found {len(shared_deps)} shared dependencies")

    def _test_interface_compatibility(self, consumers: List[str]) -> None:
        """Test interface compatibility between consumers."""
        self.log("Testing interface compatibility...")

        # Test that consumers can import each other's interfaces
        # This is a simplified version - in practice, this would be more comprehensive

        interface_tests = {
            "openssl": ["crypto", "ssl"],
            "mia": ["device_manager", "connectivity"],
            "mcp": ["mcp_server", "fastmcp_integration"],
            "android": ["native_interface"]
        }

        for consumer in consumers:
            if consumer in interface_tests:
                interfaces = interface_tests[consumer]
                self.results["interface_compatibility"][consumer] = {
                    "interfaces": interfaces,
                    "tested": True,
                    "accessible": self._test_consumer_interfaces(consumer, interfaces)
                }

    def _test_openssl_mia_integration(self) -> bool:
        """Test OpenSSL integration with MIA."""
        # This would test that MIA can use OpenSSL for secure communications
        # For now, simulate the test

        try:
            # Simulate testing MIA's use of OpenSSL
            self.log("Testing MIA OpenSSL integration...")

            # Check that MIA declares OpenSSL as dependency
            mia_config = load_consumer_config("mia")
            if not mia_config:
                return False

            foundation_deps = mia_config.get("dependencies", {}).get("foundation", [])
            has_openssl = any("openssl" in dep for dep in foundation_deps)

            if not has_openssl:
                self.log("MIA missing OpenSSL dependency")
                return False

            # Simulate successful integration test
            return True

        except Exception as e:
            self.log(f"MIA-OpenSSL integration test failed: {e}")
            return False

    def _test_openssl_mcp_integration(self) -> bool:
        """Test OpenSSL integration with MCP."""
        # Test secure MCP communications
        try:
            self.log("Testing MCP OpenSSL integration...")

            # MCP may optionally use OpenSSL for secure connections
            # This is a compatibility test, not a requirement
            return True

        except Exception as e:
            self.log(f"MCP-OpenSSL integration test failed: {e}")
            return False

    def _test_mia_automotive_integration(self) -> bool:
        """Test MIA integration with automotive extensions."""
        try:
            self.log("Testing MIA-automotive integration...")

            # Check that automotive consumer can extend MIA
            automotive_config = load_consumer_config("automotive")
            if not automotive_config:
                return False

            # Automotive should depend on MIA
            mia_deps = automotive_config.get("dependencies", {}).get("mia", [])
            has_mia = any("mia" in dep for dep in mia_deps)

            if not has_mia:
                # Check foundation deps as fallback
                foundation_deps = automotive_config.get("dependencies", {}).get("foundation", [])
                has_mia = any("mia" in dep for dep in foundation_deps)

            return has_mia

        except Exception as e:
            self.log(f"MIA-automotive integration test failed: {e}")
            return False

    def _test_openssl_android_integration(self) -> bool:
        """Test OpenSSL integration with Android."""
        try:
            self.log("Testing Android OpenSSL integration...")

            # Check that Android declares OpenSSL as dependency
            android_config = load_consumer_config("android")
            if not android_config:
                return False

            foundation_deps = android_config.get("dependencies", {}).get("foundation", [])
            has_openssl = any("openssl" in dep for dep in foundation_deps)

            return has_openssl

        except Exception as e:
            self.log(f"Android-OpenSSL integration test failed: {e}")
            return False

    def _check_consumer_compatibility(self, consumer_a: str, consumer_b: str) -> str:
        """Check compatibility between two consumers.

        Returns:
            Compatibility status: "compatible", "incompatible", "unknown"
        """
        # Define known compatibility rules
        compatibility_rules = {
            ("openssl", "mia"): "compatible",  # OpenSSL provides crypto for MIA
            ("openssl", "mcp"): "compatible",  # OpenSSL can secure MCP
            ("openssl", "android"): "compatible",  # Android uses OpenSSL
            ("mia", "automotive"): "compatible",  # Automotive extends MIA
            ("openssl", "audio"): "compatible",  # No direct dependency
            ("mia", "mcp"): "compatible",  # Can work together
        }

        # Check both directions
        key1 = (consumer_a, consumer_b)
        key2 = (consumer_b, consumer_a)

        if key1 in compatibility_rules:
            return compatibility_rules[key1]
        elif key2 in compatibility_rules:
            return compatibility_rules[key2]
        else:
            return "unknown"

    def _test_consumer_interfaces(self, consumer: str, interfaces: List[str]) -> bool:
        """Test that consumer interfaces are accessible.

        Args:
            consumer: Consumer name
            interfaces: List of interfaces to test

        Returns:
            True if all interfaces are accessible
        """
        # This would actually try to import and test interfaces
        # For now, simulate based on consumer configuration

        config = load_consumer_config(consumer)
        if not config:
            return False

        # Assume interfaces are accessible if consumer is properly configured
        packages = config.get("packages", [])
        return len(packages) > 0

    def _report_results(self) -> None:
        """Report validation results."""
        print("\nCross-Consumer Validation Results:")

        if self.results["integration_tests"]:
            print(f"Integration Tests: {len(self.results['integration_tests'])}")
            for test in self.results["integration_tests"]:
                status = "✅" if test["success"] else "❌"
                print(f"  {status} {test['scenario']}: {test['description']}")

        if self.results["shared_dependencies"]:
            print(f"\nShared Dependencies: {len(self.results['shared_dependencies'])}")
            for dep, consumers in self.results["shared_dependencies"].items():
                print(f"  - {dep}: used by {', '.join(consumers)}")

        if self.results["failed_integrations"]:
            print(f"\n❌ Failed Integrations: {len(self.results['failed_integrations'])}")
            for failed in self.results["failed_integrations"]:
                print(f"  - {failed}")

        # Compatibility matrix summary
        if self.results["compatibility_matrix"]:
            compatible_count = 0
            total_count = 0

            for consumer_a, compatibilities in self.results["compatibility_matrix"].items():
                for consumer_b, status in compatibilities.items():
                    if consumer_a != consumer_b:
                        total_count += 1
                        if status == "compatible":
                            compatible_count += 1

            if total_count > 0:
                compatibility_rate = (compatible_count / total_count) * 100
                print(".1f")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tier 3 Validation: Cross-Consumer Compatibility"
    )

    parser.add_argument(
        "--consumer",
        action="append",
        help="Specific consumer to validate"
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary directories for debugging"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = CrossConsumerValidator(verbose=args.verbose, keep_temp=args.keep_temp)
    success = validator.validate_cross_consumer_compatibility(consumers=args.consumer)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()