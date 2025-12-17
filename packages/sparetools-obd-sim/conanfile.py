from conan import ConanFile
from conan.tools.files import copy


class SparetoolsOBDSimConan(ConanFile):
    name = "sparetools-obd-sim"
    version = "2.0.0"
    package_type = "python-require"
    description = "OBD-II simulation tooling packaged for SpareTools and MIA"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    python_requires = "sparetools-base/2.0.0"
    tool_requires = "sparetools-cpython/3.12.7"

    exports_sources = "sparetools_obd/**"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = []
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
