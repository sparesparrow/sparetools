import os
import sys
from conan import ConanFile
from conan.tools.files import copy

class SpareToolsBootstrapConan(ConanFile):
    name = "sparetools-bootstrap"
    version = "2.0.3"
    package_type = "python-require"
    description = "Bootstrap utilities for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    # CRITICAL FIX: Add missing foundation dependency
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    
    exports_sources = "bootstrap/**", "scripts/**"
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.sh", src=self.source_folder, dst=self.package_folder, keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        self.cpp_info.libs = []
        # Conan 2.x API: Use buildenv_info for build-time Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)