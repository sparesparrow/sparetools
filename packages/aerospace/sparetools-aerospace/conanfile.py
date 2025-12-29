from conan import ConanFile
from conan.tools.files import copy

class SparetoolsAerospaceConan(ConanFile):
    name = "sparetools-aerospace"
    version = "1.0.0"
    package_type = "python-require"
    description = "Aerospace domain extensions for SpareTools (migrated from ngapy)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Require test framework and base utilities
    python_requires = "sparetools-base/2.0.3"
    requires = "sparetools-test-framework/1.0.0"

    exports_sources = "sparetools_aerospace/**/*.py"

    def package(self):
        copy(self, "**/*.py", src=self.source_folder,
             dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)