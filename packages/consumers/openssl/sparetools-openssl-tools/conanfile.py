import os
import sys
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.scm import Git

class SpareToolsOpenSSLToolsConan(ConanFile):
    """OpenSSL build tools, profiles, and utilities for SpareTools ecosystem."""

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    name = "sparetools-openssl-tools"
    version = '1.0.0'
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    description = "OpenSSL build tools, profiles, and utilities for SpareTools ecosystem"
    topics = ("openssl", "build-tools", "profiles", "cryptography")

    # Sources are cloned from upstream repository
    exports_sources = ()

    def source(self):
        """Clone upstream OpenSSL Tools repository"""
        git = Git(self)
        git.clone("https://github.com/sparesparrow/openssl-tools.git", target="upstream")

    def layout(self):
        """Set source folder to upstream repository"""
        from conan.tools.layout import basic_layout
        basic_layout(self, src_folder="upstream")

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