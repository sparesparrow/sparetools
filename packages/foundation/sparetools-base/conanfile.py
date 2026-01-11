from conan import ConanFile
import yaml
import os
from pathlib import Path


def _load_versions():
    """Load versions from versions.yaml file"""
    versions_file = Path(__file__).parent.parent.parent.parent / "versions.yaml"
    if versions_file.exists():
        try:
            with open(versions_file, 'r') as f:
                data = yaml.safe_load(f)
                # Flatten the nested structure
                versions = {}
                for category, packages in data.items():
                    if isinstance(packages, dict):
                        versions.update(packages)
                return versions
        except Exception:
            pass
    # Fallback to hardcoded versions if file not found or parsing fails
    return {
        "cpython": "3.12.8",
        "python-scripts": "1.0.0",
        "test-harness": "2.0.0",
        "gtest": "1.14.0",
        "shared-dev-tools": "2.0.0",
        "bootstrap": "2.0.0",
        "openssl": "3.3.2",
        "lvgl": "8.3.11",
        "test": "1.0.0"
    }


class SpareToolsVersions:
    """Centralized version management for SpareTools ecosystem"""
    versions = _load_versions()

    # Convenience accessors for common packages
    SPARETOOLS_BASE = "2.0.4"
    SPARETOOLS_CPYTHON = versions.get("cpython", "3.12.8")
    SPARETOOLS_PYTHON_SCRIPTS = versions.get("python-scripts", "1.0.0")
    SPARETOOLS_OPENSSL = versions.get("openssl", "3.3.2")


class SpareToolsSecurityMixin:
    """Mixin providing security gate and SBOM generation methods.

    Packages that call apply_security_gates() or generate_sbom() should
    inherit from this mixin class to get the method implementations.
    """

    def apply_security_gates(self) -> None:
        """Run security scanning (placeholder for Trivy, Syft integration)."""
        self.output.info("🔒 Applying security gates...")
        # TODO: Integrate actual Trivy/Syft scanning
        # Example integration points:
        # - trivy fs --scanners vuln,secret,config .
        # - syft packages . -o json
        self.output.info("✅ Security gates passed (placeholder)")

    def generate_sbom(self, format: str = "cyclonedx") -> None:
        """Generate SBOM in specified format.

        Args:
            format: SBOM format - 'cyclonedx', 'spdx', or 'syft-json'
        """
        self.output.info(f"📋 Generating SBOM in {format} format...")
        # TODO: Integrate actual SBOM generation
        # Example integration points:
        # - syft packages . -o cyclonedx-json > sbom.json
        # - cyclonedx-py environment > sbom.xml
        self.output.info("✅ SBOM generated (placeholder)")


class SpareToolsBaseConan(ConanFile, SpareToolsSecurityMixin):
    name = "sparetools-base"
    # Use CONAN_BUILD_VERSION from environment (set by git-to-conan collector)
    # Fallback to static version for local development
    version = os.environ.get('CONAN_BUILD_VERSION', '2.0.4')
    package_type = "python-require"
    description = "Recipe helpers for SpareTools Conan packages"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Minimal exports - only conanfile (exclude sparetools/ runtime modules)
    exports_sources = ("conanfile.py", "README.md", "!sparetools/**")

    def package(self):
        # No need to copy anything - python_requires uses source directly
        pass

    def package_info(self):
        # Python-requires don't need package_info
        pass
