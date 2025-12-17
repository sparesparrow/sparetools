from conan import ConanFile
from conan.tools.files import copy

class SparetoolsTestHarnessConan(ConanFile):
    name = "sparetools-test-harness"
    version = "2.0.0"
    package_type = "python-require"
    description = "Unified test harness for SpareTools projects (ngapy-style)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Require bundled Python and base utilities
    tool_requires = "sparetools-cpython/3.12.7"
    python_requires = "sparetools-base/2.0.0"

    exports_sources = "sparetools_test_harness/**/*.py"

    def package(self):
        copy(self, "**/*.py", src=self.source_folder,
             dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)