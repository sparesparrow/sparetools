import os
import sys
from conan import ConanFile
from conan.tools.files import copy

# Import base class from shared scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../scripts'))
from recipe_base import ConsumerPackageConan


class SparetoolsOBDSimConan(ConsumerPackageConan):
    name = "sparetools-obd-sim"
    version = "2.0.0"
    package_type = "python-require"
    description = "OBD-II simulation tooling packaged for SpareTools and MIA"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Declare consumer context
    consumer_domain = "automotive"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.0"
    tool_requires = "sparetools-cpython/3.12.7"

    exports_sources = "sparetools_obd/**"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        self.cpp_info.libs = []
        # Conan 2.x API: Use buildenv_info for build-time Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
