import os
import sys
from conan import ConanFile
from conan.tools.files import copy

# Import base class from shared scripts
import pathlib
scripts_dir = pathlib.Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
try:
    from recipe_base import SpareToolsBaseConan
except ImportError:
    # Fallback: define minimal base class if import fails
    class SpareToolsBaseConan(ConanFile):
        pass

class SpareToolsBootstrapConan(SpareToolsBaseConan):
    name = "sparetools-bootstrap"
    version = "2.0.1"
    package_type = "python-require"
    description = "Bootstrap utilities for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    # CRITICAL FIX: Add missing foundation dependency
    python_requires = "sparetools-base/2.0.0"
    
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