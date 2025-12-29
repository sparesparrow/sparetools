from conan import ConanFile
from conan.tools.files import copy

class SparetoolsEmbeddedConan(ConanFile):
    name = "sparetools-embedded"
    version = "1.0.0"
    package_type = "python-require"
    description = "Embedded systems testing extensions for SpareTools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Require test framework and base utilities
    python_requires = "sparetools-base/2.0.3"
    requires = "sparetools-test-framework/1.0.0"

    # Additional dependencies for embedded testing
    tool_requires = "sparetools-cpython/3.12.7"

    exports_sources = "sparetools_embedded/**/*.py"

    def package(self):
        copy(self, "**/*.py", src=self.source_folder,
             dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)