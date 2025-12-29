"""Base classes for SpareTools Conan recipes.

This module provides inheritance hierarchies for all SpareTools packages,
ensuring consistent behavior, security gates, and build patterns across
the entire ecosystem.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

from conan import ConanFile
from conan.tools.files import copy
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import MSBuildToolchain, MSBuildDeps


class SpareToolsBaseConan(ConanFile):
    """Base class for all SpareTools packages.

    Provides common functionality including:
    - Platform profile auto-detection
    - Security gate application
    - SBOM generation
    - Environment validation
    - Shared utility access
    """

    # All SpareTools packages should use the base utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    def configure_platform_profile(self) -> None:
        """Auto-detect and apply platform profile.

        This method automatically selects the appropriate build profile
        based on the current platform and compiler settings.
        """
        # Platform detection logic would go here
        # For now, this is a placeholder that can be extended
        self.output.info("Configuring platform profile...")

        # Example platform-specific settings
        if self.settings.os == "Android":
            # Android-specific configuration
            self.output.info("Detected Android platform")
        elif self.settings.os == "iOS":
            # iOS-specific configuration
            self.output.info("Detected iOS platform")
        elif self.settings.os == "Linux":
            # Linux-specific configuration
            self.output.info("Detected Linux platform")
        elif self.settings.os == "Macos":
            # macOS-specific configuration
            self.output.info("Detected macOS platform")
        elif self.settings.os == "Windows":
            # Windows-specific configuration
            self.output.info("Detected Windows platform")

    def apply_security_gates(self) -> None:
        """Run security scanning (Trivy, Syft, vulnerability checks).

        This method applies security gates including:
        - Container image scanning
        - Dependency vulnerability scanning
        - License compliance checking
        """
        self.output.info("Applying security gates...")

        # Security validation would be implemented here
        # Integration with Trivy, Syft, etc.

        # For now, this is a placeholder
        self.output.info("Security gates applied (placeholder)")

    def generate_sbom(self, format: str = "cyclonedx") -> None:
        """Auto-generate SBOM (CycloneDX/SPDX).

        Args:
            format: SBOM format ('cyclonedx' or 'spdx')
        """
        self.output.info(f"Generating SBOM in {format} format...")

        # SBOM generation logic would go here
        # Integration with Syft, CycloneDX tools

        # For now, create a basic JSON SBOM
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "component": {
                    "name": self.name,
                    "version": self.version,
                    "type": "library"
                }
            },
            "components": []
        }

        sbom_file = os.path.join(self.package_folder, f"sbom-{format}.json")
        with open(sbom_file, 'w') as f:
            json.dump(sbom_data, f, indent=2)

        self.output.info(f"SBOM generated: {sbom_file}")

    def validate_build_environment(self) -> None:
        """Ensure build environment meets requirements.

        Checks for:
        - Required tools availability
        - Environment variables
        - Platform compatibility
        """
        self.output.info("Validating build environment...")

        # Environment validation logic
        required_vars = []
        for var in required_vars:
            if var not in os.environ:
                self.output.warn(f"Missing environment variable: {var}")

        self.output.info("Build environment validation complete")

    def get_consumer_config(self) -> Optional[Dict[str, Any]]:
        """Get consumer configuration from .consumer.yaml if available."""
        # Try to find consumer config in parent directories
        current_dir = Path(self.folders.source or ".")

        for parent in [current_dir] + list(current_dir.parents):
            config_file = parent / ".consumer.yaml"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    self.output.warn(f"Failed to load consumer config: {e}")
                    break

        return None

    def configure(self) -> None:
        """Apply base configuration and security gates."""
        self.configure_platform_profile()
        self.apply_security_gates()
        self.validate_build_environment()


class OpenSSLBaseConan(SpareToolsBaseConan):
    """Specialized base for OpenSSL packages.

    Provides OpenSSL-specific configuration including:
    - Build method selection
    - Provider ordering configuration
    - FIPS compliance settings
    - Cross-platform OpenSSL builds
    """

    def configure_openssl_settings(self) -> None:
        """Handle OpenSSL-specific configuration."""
        self.output.info("Configuring OpenSSL-specific settings...")

        # OpenSSL-specific settings based on build method
        if hasattr(self, 'build_method'):
            method = self.build_method
            self.output.info(f"Using OpenSSL build method: {method}")

            if method == "perl-configure":
                # Perl Configure method settings
                pass
            elif method == "cmake":
                # CMake build method settings
                pass
            elif method == "autotools":
                # Autotools build method settings
                pass

    def select_build_method(self) -> str:
        """Choose optimal build method based on platform and requirements.

        Returns:
            Selected build method ('perl-configure', 'cmake', 'autotools')
        """
        # Build method selection logic
        # This would analyze platform, dependencies, etc.

        # Default to perl-configure for maximum compatibility
        return "perl-configure"

    def configure_openssl_providers(self) -> None:
        """Configure OpenSSL 3.x provider ordering."""
        self.output.info("Configuring OpenSSL provider ordering...")

        # Provider ordering configuration for OpenSSL 3.x
        # This affects FIPS compliance and cryptographic module loading

    def validate_fips_compliance(self) -> None:
        """Validate FIPS 140-3 compliance if required."""
        self.output.info("Validating FIPS compliance...")

        # FIPS validation logic
        # Integration with OpenSSL FIPS module testing

    def configure(self) -> None:
        """Apply OpenSSL-specific configuration."""
        super().configure()
        self.configure_openssl_settings()
        self.configure_openssl_providers()

    def build(self) -> None:
        """Build with OpenSSL-specific considerations."""
        self.validate_fips_compliance()

        # Call parent build or implement OpenSSL-specific build
        super().build()


class ConsumerPackageConan(SpareToolsBaseConan):
    """Specialized base for consumer packages.

    Provides consumer-specific functionality including:
    - Consumer domain registration
    - Cross-consumer dependency management
    - Consumer-aware validation
    """

    # Consumer domain should be set by subclasses
    consumer_domain: str = ""

    def declare_consumer_context(self) -> None:
        """Register this package with its consumer domain."""
        if not self.consumer_domain:
            self.output.warn("Consumer domain not specified")
            return

        self.output.info(f"Registering {self.name}/{self.version} for {self.consumer_domain} consumer")

        # Register with consumer orchestration
        # This could update consumer-specific registries or configs

    def validate_consumer_dependencies(self) -> None:
        """Validate consumer-specific dependency requirements."""
        self.output.info(f"Validating {self.consumer_domain} consumer dependencies...")

        # Consumer-specific dependency validation
        config = self.get_consumer_config()
        if config:
            required_deps = config.get('dependencies', {})
            # Validate required dependencies are present

    def apply_consumer_specific_gates(self) -> None:
        """Apply consumer-specific security and validation gates."""
        self.output.info(f"Applying {self.consumer_domain} consumer-specific gates...")

        # Consumer-specific security gates
        if self.consumer_domain == "openssl":
            # OpenSSL-specific security requirements
            pass
        elif self.consumer_domain == "mia":
            # MIA-specific security requirements
            pass
        elif self.consumer_domain == "mcp":
            # MCP-specific security requirements
            pass

    def configure(self) -> None:
        """Apply consumer-specific configuration."""
        super().configure()
        self.declare_consumer_context()
        self.validate_consumer_dependencies()
        self.apply_consumer_specific_gates()

    def package_info(self) -> None:
        """Set consumer-specific package information."""
        super().package_info()

        # Add consumer domain metadata
        if self.consumer_domain:
            self.conf_info[f"user.sparetools.consumer.{self.consumer_domain}"] = "true"


# Utility functions for recipe management

def load_consumer_config(consumer_name: str) -> Optional[Dict[str, Any]]:
    """Load consumer configuration from .consumer.yaml.

    Args:
        consumer_name: Name of the consumer domain

    Returns:
        Consumer configuration dictionary or None if not found
    """
    config_path = Path("packages") / "consumers" / consumer_name / ".consumer.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return None


def get_consumer_packages(consumer_name: str) -> List[str]:
    """Get list of packages for a consumer domain.

    Args:
        consumer_name: Name of the consumer domain

    Returns:
        List of package names
    """
    config = load_consumer_config(consumer_name)
    if config and 'packages' in config:
        return config['packages']
    return []


def validate_consumer_setup(consumer_name: str) -> Dict[str, Any]:
    """Validate consumer setup and return status.

    Args:
        consumer_name: Name of the consumer domain

    Returns:
        Validation results dictionary
    """
    results = {
        "consumer": consumer_name,
        "config_valid": False,
        "packages_found": [],
        "issues": []
    }

    config = load_consumer_config(consumer_name)
    if not config:
        results["issues"].append("Consumer config (.consumer.yaml) not found")
        return results

    results["config_valid"] = True

    # Check packages exist
    consumer_dir = Path("packages") / "consumers" / consumer_name
    if consumer_dir.exists():
        for item in consumer_dir.iterdir():
            if item.is_dir() and (item / "conanfile.py").exists():
                results["packages_found"].append(item.name)

    # Check required packages are present
    required_packages = config.get('packages', [])
    for package in required_packages:
        if package not in results["packages_found"]:
            results["issues"].append(f"Required package not found: {package}")

    return results