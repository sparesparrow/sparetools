#!/usr/bin/env python3
"""
Matrix Generator for SpareTools CI/CD

Generates build matrices for GitHub Actions based on consumer configurations
and platform requirements.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config


class MatrixGenerator:
    """Generates CI/CD build matrices from consumer configurations."""

    def __init__(self):
        self.consumers = {}
        self.matrix = {"include": []}

    def load_consumer_configs(self, consumer_names: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Load consumer configurations.

        Args:
            consumer_names: Specific consumers to load, or None for all

        Returns:
            Dictionary of consumer configurations
        """
        consumers_to_load = consumer_names or [
            "openssl", "mia", "mcp", "android", "audio", "automotive"
        ]

        configs = {}
        for consumer_name in consumers_to_load:
            config = load_consumer_config(consumer_name)
            if config:
                configs[consumer_name] = config

        return configs

    def generate_build_matrix(self, consumer_names: Optional[List[str]] = None,
                            platforms: Optional[List[str]] = None,
                            include_foundation: bool = True) -> Dict[str, Any]:
        """Generate build matrix for all consumers.

        Args:
            consumer_names: Specific consumers to include
            platforms: Platforms to target (linux, macos, windows)
            include_foundation: Whether to include foundation packages

        Returns:
            GitHub Actions matrix dictionary
        """
        configs = self.load_consumer_configs(consumer_names)
        matrix = {"include": []}

        # Add foundation packages if requested
        if include_foundation:
            foundation_packages = [
                {"consumer": "foundation", "package": "sparetools-base"},
                {"consumer": "foundation", "package": "sparetools-bootstrap"},
                {"consumer": "foundation", "package": "sparetools-shared-dev-tools"},
                {"consumer": "foundation", "package": "sparetools-cpython"},
            ]

            for package in foundation_packages:
                # Foundation packages run on all platforms
                for os_name in platforms or ["ubuntu-latest", "macos-latest", "windows-latest"]:
                    matrix["include"].append({
                        "consumer": package["consumer"],
                        "package": package["package"],
                        "os": os_name,
                        "runs-on": os_name,
                        "type": "foundation"
                    })

        # Add consumer packages
        for consumer_name, config in configs.items():
            packages = config.get("packages", [])
            supported_platforms = config.get("platforms", {})

            for package in packages:
                # Generate platform combinations
                platform_configs = self._generate_platform_configs(
                    consumer_name, package, supported_platforms, platforms
                )
                matrix["include"].extend(platform_configs)

        return matrix

    def _generate_platform_configs(self, consumer_name: str, package_name: str,
                                 supported_platforms: Dict[str, List[str]],
                                 target_platforms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate platform configurations for a package.

        Args:
            consumer_name: Name of the consumer
            package_name: Name of the package
            supported_platforms: Platforms supported by the consumer
            target_platforms: Target platforms for this build

        Returns:
            List of platform configurations
        """
        configs = []

        # Default platforms if not specified
        if not target_platforms:
            target_platforms = ["ubuntu-latest", "macos-latest", "windows-latest"]

        # Convert supported platforms to GitHub runner names
        platform_mapping = {
            "linux": ["ubuntu-latest"],
            "macos": ["macos-latest"],
            "windows": ["windows-latest"],
            "ubuntu-latest": ["ubuntu-latest"],
            "macos-latest": ["macos-latest"],
            "windows-latest": ["windows-latest"]
        }

        for target_platform in target_platforms:
            # Check if this platform is supported
            platform_supported = False

            for supported_os, arches in supported_platforms.items():
                if supported_os in platform_mapping and target_platform in platform_mapping[supported_os]:
                    platform_supported = True
                    break

            # If no specific platforms defined, assume all are supported
            if not supported_platforms or platform_supported:
                configs.append({
                    "consumer": consumer_name,
                    "package": package_name,
                    "os": target_platform,
                    "runs-on": target_platform,
                    "type": "consumer"
                })

        return configs

    def generate_security_matrix(self, consumer_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate security scanning matrix.

        Args:
            consumer_names: Consumers to include in security scans

        Returns:
            Security scanning matrix
        """
        configs = self.load_consumer_configs(consumer_names)
        matrix = {"include": []}

        # Security scans run on Ubuntu (most comprehensive scanner support)
        scan_platform = "ubuntu-latest"

        # Foundation security scans
        foundation_scans = [
            {"target": "foundation", "scan_type": "container", "tool": "trivy"},
            {"target": "foundation", "scan_type": "dependencies", "tool": "syft"},
            {"target": "foundation", "scan_type": "secrets", "tool": "gitleaks"},
        ]

        for scan in foundation_scans:
            matrix["include"].append({
                "target": scan["target"],
                "scan_type": scan["scan_type"],
                "tool": scan["tool"],
                "os": scan_platform,
                "runs-on": scan_platform,
                "type": "security"
            })

        # Consumer security scans
        for consumer_name, config in configs.items():
            packages = config.get("packages", [])

            for package in packages:
                matrix["include"].append({
                    "consumer": consumer_name,
                    "package": package,
                    "scan_type": "package",
                    "tool": "trivy",
                    "os": scan_platform,
                    "runs-on": scan_platform,
                    "type": "security"
                })

        return matrix

    def generate_integration_matrix(self, consumer_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate integration testing matrix.

        Args:
            consumer_names: Consumers to include in integration tests

        Returns:
            Integration testing matrix
        """
        configs = self.load_consumer_configs(consumer_names)
        matrix = {"include": []}

        # Integration tests run on multiple platforms
        platforms = ["ubuntu-latest", "macos-latest", "windows-latest"]

        for platform in platforms:
            # Cross-consumer integration tests
            if len(configs) > 1:
                matrix["include"].append({
                    "test_type": "cross-consumer",
                    "consumers": list(configs.keys()),
                    "os": platform,
                    "runs-on": platform,
                    "type": "integration"
                })

            # Individual consumer integration tests
            for consumer_name, config in configs.items():
                packages = config.get("packages", [])

                if len(packages) > 1:  # Only if consumer has multiple packages
                    matrix["include"].append({
                        "test_type": "intra-consumer",
                        "consumer": consumer_name,
                        "packages": packages,
                        "os": platform,
                        "runs-on": platform,
                        "type": "integration"
                    })

        return matrix

    def export_matrix(self, matrix: Dict[str, Any], output_file: str = "matrix.json",
                     format: str = "json") -> str:
        """Export matrix to file.

        Args:
            matrix: Matrix to export
            output_file: Output filename
            format: Export format ('json', 'yaml')

        Returns:
            Path to exported file
        """
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(matrix, f, indent=2)
        elif format == "yaml":
            with open(output_file, 'w') as f:
                yaml.dump(matrix, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Matrix exported to {output_file}")
        return output_file

    def print_matrix_summary(self, matrix: Dict[str, Any]) -> None:
        """Print summary of generated matrix.

        Args:
            matrix: Matrix to summarize
        """
        jobs = matrix.get("include", [])

        print("Matrix Summary:")
        print(f"  Total jobs: {len(jobs)}")

        # Group by type
        types = {}
        consumers = {}
        platforms = {}

        for job in jobs:
            job_type = job.get("type", "unknown")
            types[job_type] = types.get(job_type, 0) + 1

            consumer = job.get("consumer", "unknown")
            consumers[consumer] = consumers.get(consumer, 0) + 1

            platform = job.get("os", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1

        print("  By type:"        for job_type, count in types.items():
            print(f"    {job_type}: {count}")

        print("  By consumer:"        for consumer, count in consumers.items():
            print(f"    {consumer}: {count}")

        print("  By platform:"        for platform, count in platforms.items():
            print(f"    {platform}: {count}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate CI/CD build matrices for SpareTools"
    )

    parser.add_argument(
        "--consumers",
        nargs="*",
        help="Specific consumers to include"
    )

    parser.add_argument(
        "--platforms",
        nargs="*",
        default=["ubuntu-latest", "macos-latest", "windows-latest"],
        help="Target platforms"
    )

    parser.add_argument(
        "--matrix-type",
        choices=["build", "security", "integration"],
        default="build",
        help="Type of matrix to generate"
    )

    parser.add_argument(
        "--output", "-o",
        default="matrix.json",
        help="Output file"
    )

    parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="Output format"
    )

    parser.add_argument(
        "--no-foundation",
        action="store_true",
        help="Exclude foundation packages"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print matrix summary"
    )

    args = parser.parse_args()

    generator = MatrixGenerator()

    if args.matrix_type == "build":
        matrix = generator.generate_build_matrix(
            consumer_names=args.consumers,
            platforms=args.platforms,
            include_foundation=not args.no_foundation
        )
    elif args.matrix_type == "security":
        matrix = generator.generate_security_matrix(args.consumers)
    elif args.matrix_type == "integration":
        matrix = generator.generate_integration_matrix(args.consumers)

    # Export matrix
    output_file = generator.export_matrix(matrix, args.output, args.format)

    # Print summary if requested
    if args.summary:
        generator.print_matrix_summary(matrix)

    print(f"Matrix generated and saved to: {output_file}")


if __name__ == "__main__":
    main()