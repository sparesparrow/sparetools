#!/usr/bin/env python3
"""
Validate Consumer Integration

Comprehensive validation script that ensures all consumers in the SpareTools
monorepo work correctly together and follow the layered architecture.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set


class ConsumerIntegrationValidator:
    def __init__(self, monorepo_root: Path):
        self.monorepo_root = monorepo_root
        self.errors = []
        self.warnings = []
        self.consumers = {}
        self.foundations = {}

    def validate(self) -> bool:
        """Run all integration validation checks."""
        print("🔗 Validating SpareTools consumer integration...")

        checks = [
            self._discover_packages,
            self._validate_layered_architecture,
            self._validate_dependency_graph,
            self._validate_consumer_configs,
            self._validate_cross_consumer_compatibility,
            self._validate_build_systems,
        ]

        for check in checks:
            try:
                check()
                print(f"✅ {check.__name__} passed")
            except Exception as e:
                self.errors.append(f"{check.__name__} failed: {e}")
                print(f"❌ {check.__name__} failed: {e}")

        self._report_results()
        return len(self.errors) == 0

    def _discover_packages(self):
        """Discover all packages in the monorepo."""
        packages_dir = self.monorepo_root / "packages"

        # Discover foundation packages
        foundation_dir = packages_dir / "foundation"
        if foundation_dir.exists():
            for pkg_dir in foundation_dir.iterdir():
                if pkg_dir.is_dir() and (pkg_dir / "conanfile.py").exists():
                    self.foundations[pkg_dir.name] = {
                        "path": pkg_dir,
                        "type": "foundation"
                    }

        # Discover consumer packages
        consumers_dir = packages_dir / "consumers"
        if consumers_dir.exists():
            for consumer_type_dir in consumers_dir.iterdir():
                if consumer_type_dir.is_dir():
                    for pkg_dir in consumer_type_dir.iterdir():
                        if pkg_dir.is_dir() and (pkg_dir / "conanfile.py").exists():
                            self.consumers[pkg_dir.name] = {
                                "path": pkg_dir,
                                "type": consumer_type_dir.name,
                                "platform": consumer_type_dir.name
                            }

        print(f"  📦 Found {len(self.foundations)} foundation packages")
        print(f"  📱 Found {len(self.consumers)} consumer packages")

    def _validate_layered_architecture(self):
        """Validate that the layered architecture is properly implemented."""
        # Check that foundation and consumers directories exist
        foundation_dir = self.monorepo_root / "packages" / "foundation"
        consumers_dir = self.monorepo_root / "packages" / "consumers"

        if not foundation_dir.exists():
            raise Exception("Foundation layer directory missing")

        if not consumers_dir.exists():
            raise Exception("Consumers layer directory missing")

        # Check that deprecated directory is separate
        deprecated_dir = self.monorepo_root / "packages" / "deprecated"
        if deprecated_dir.exists():
            self.warnings.append("Deprecated packages should be migrated to new structure")

        # Validate foundation packages don't depend on consumers
        for foundation_name, foundation_info in self.foundations.items():
            conanfile = foundation_info["path"] / "conanfile.py"
            content = conanfile.read_text()

            # Foundation packages should not have python_requires pointing to consumers
            for consumer_name in self.consumers.keys():
                if f"sparetools-{consumer_name}" in content:
                    raise Exception(f"Foundation package {foundation_name} depends on consumer {consumer_name}")

    def _validate_dependency_graph(self):
        """Validate the dependency graph between layers."""
        # Check that consumers depend on foundation packages
        consumer_dependencies = {}

        for consumer_name, consumer_info in self.consumers.items():
            conanfile = consumer_info["path"] / "conanfile.py"
            content = conanfile.read_text()

            deps = []
            if "python_requires" in content:
                # Extract python_requires
                lines = content.split('\n')
                in_python_requires = False
                for line in lines:
                    line = line.strip()
                    if line.startswith('python_requires'):
                        in_python_requires = True
                        if '=' in line:
                            # Single line
                            deps.extend(self._extract_package_names(line))
                            break
                        continue
                    elif in_python_requires and line.startswith(')'):
                        break
                    elif in_python_requires and line.strip():
                        deps.extend(self._extract_package_names(line))

            consumer_dependencies[consumer_name] = deps

            # Validate that consumers depend on at least one foundation package
            foundation_deps = [dep for dep in deps if dep in self.foundations or dep.startswith('sparetools-base')]
            if not foundation_deps:
                self.warnings.append(f"Consumer {consumer_name} has no foundation dependencies")

        print(f"  🔗 Dependency graph validated: {consumer_dependencies}")

    def _extract_package_names(self, line: str) -> List[str]:
        """Extract package names from a python_requires line."""
        packages = []
        # Remove quotes and split by comma
        line = line.replace('"', '').replace("'", '').strip()
        if ',' in line:
            parts = line.split(',')
        else:
            parts = [line]

        for part in parts:
            part = part.strip()
            if '/' in part:
                # Extract package name before version
                pkg_name = part.split('/')[0].strip()
                packages.append(pkg_name)

        return packages

    def _validate_consumer_configs(self):
        """Validate consumer configuration files."""
        for consumer_name, consumer_info in self.consumers.items():
            config_file = consumer_info["path"] / ".consumer.yaml"
            if not config_file.exists():
                self.errors.append(f"Consumer {consumer_name} missing .consumer.yaml")
                continue

            try:
                import yaml
                with open(config_file) as f:
                    config = yaml.safe_load(f)

                required_keys = ['name', 'version', 'type', 'platform']
                for key in required_keys:
                    if key not in config:
                        self.errors.append(f"Consumer {consumer_name} config missing key: {key}")

                # Validate config matches directory structure
                if config.get('name') != consumer_name:
                    self.errors.append(f"Consumer {consumer_name} config name mismatch")

                if config.get('platform') != consumer_info['platform']:
                    self.errors.append(f"Consumer {consumer_name} platform mismatch")

            except ImportError:
                self.warnings.append("PyYAML not available for config validation")
            except Exception as e:
                self.errors.append(f"Consumer {consumer_name} config validation failed: {e}")

    def _validate_cross_consumer_compatibility(self):
        """Validate that consumers can coexist."""
        # Check for naming conflicts
        all_names = set(self.foundations.keys()) | set(self.consumers.keys())
        if len(all_names) != len(self.foundations) + len(self.consumers):
            self.errors.append("Package naming conflicts detected")

        # Check that all consumers use the same base classes
        base_classes_used = {}
        for consumer_name, consumer_info in self.consumers.items():
            conanfile = consumer_info["path"] / "conanfile.py"
            content = conanfile.read_text()

            if "SpareToolsConsumerBase" in content:
                base_classes_used[consumer_name] = "SpareToolsConsumerBase"
            else:
                base_classes_used[consumer_name] = "custom"

        # Warn if not all consumers use the standard base class
        standard_count = sum(1 for cls in base_classes_used.values() if cls == "SpareToolsConsumerBase")
        if standard_count != len(self.consumers):
            self.warnings.append(f"Only {standard_count}/{len(self.consumers)} consumers use SpareToolsConsumerBase")

    def _validate_build_systems(self):
        """Validate build system compatibility."""
        build_systems = {}

        for consumer_name, consumer_info in self.consumers.items():
            config_file = consumer_info["path"] / ".consumer.yaml"
            if config_file.exists():
                try:
                    import yaml
                    with open(config_file) as f:
                        config = yaml.safe_load(f)

                    build_system = config.get('build', {}).get('system')
                    if build_system:
                        build_systems[consumer_name] = build_system

                        # Validate build system files exist
                        if build_system == 'gradle':
                            gradle_files = ['build.gradle.kts', 'settings.gradle.kts']
                            for gradle_file in gradle_files:
                                if not (consumer_info["path"] / gradle_file).exists():
                                    self.errors.append(f"Consumer {consumer_name} missing Gradle file: {gradle_file}")

                except ImportError:
                    pass  # PyYAML not available

        print(f"  🔧 Build systems: {build_systems}")

    def _report_results(self):
        """Report validation results."""
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} integration errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} integration warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All consumer integration checks passed!")


def main():
    """Main integration validation entry point."""
    monorepo_root = Path(__file__).parent
    validator = ConsumerIntegrationValidator(monorepo_root)

    if validator.validate():
        print("\n🎉 SpareTools consumer integration validation successful!")
        return 0
    else:
        print("\n💥 SpareTools consumer integration validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())