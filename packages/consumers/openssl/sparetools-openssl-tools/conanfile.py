import os
import sys
from conan import ConanFile
from conan.tools.files import copy

# Import base class from shared scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../scripts'))
from recipe_base import ConsumerPackageConan


class SpareToolsOpenSSLToolsConan(ConsumerPackageConan):
    """OpenSSL build tools, profiles, and utilities for SpareTools ecosystem."""

    name = "sparetools-openssl-tools"
    version = "2.0.0"
    package_type = "python-require"
    description = "OpenSSL build tools, profiles, security gates, and utilities"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("openssl", "build-tools", "profiles", "security", "fips")

    # Declare consumer context
    consumer_domain = "openssl"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.0"

    # Source files to export
    exports_sources = (
        "src/*",
        "profiles/*",
        "scripts/*",
        "docs/*",
    )

    def package(self):
        """Package OpenSSL tools and utilities."""
        # Copy Python modules
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"), keep_path=True)

        # Copy profiles
        copy(self, "*", os.path.join(self.source_folder, "profiles"), os.path.join(self.package_folder, "profiles"), keep_path=True)

        # Copy scripts
        copy(self, "*", os.path.join(self.source_folder, "scripts"), os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy documentation
        copy(self, "*", os.path.join(self.source_folder, "docs"), os.path.join(self.package_folder, "docs"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Provide OpenSSL tools information."""
        self.cpp_info.libs = []

        # Add Python path for tools
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "src"))

        # Add scripts to PATH
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Conf info for profile discovery
        self.conf_info.define("user.openssl-tools:profiles", os.path.join(self.package_folder, "profiles"))
        self.conf_info.define("user.openssl-tools:scripts", os.path.join(self.package_folder, "bin"))