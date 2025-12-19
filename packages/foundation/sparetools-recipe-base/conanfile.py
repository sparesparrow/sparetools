from conan import ConanFile
from conan.tools.files import copy


class SpareToolsRecipeBaseConan(ConanFile):
    name = "sparetools-recipe-base"
    version = "2.0.0"
    package_type = "python-require"
    description = "Base classes for SpareTools layered architecture recipes"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    exports_sources = "*.py"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = []
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)