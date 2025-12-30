from conan import ConanFile
from conan.tools.files import copy
from pathlib import Path


class SpareToolsFsToolsConan(ConanFile):
    name = "sparetools-fs-tools"
    version = "1.0.1"
    description = "Filesystem operations and utilities"
    license = "MIT"
    author = "SpareTools Team"

    python_requires = "sparetools-recipe-base/1.0.0"

    exports_sources = "src/*", "test_package/*"

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.frameworks = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        # Mark as Python-only package
        self.cpp_info.set_property("pkg_config_name", None)

        # Python package info
        self.conf_info.define("user.sparetools-fs-tools:pythonpath", self.package_folder)

    def package(self):
        copy(self, "*.py", self.source_folder, self.package_folder, keep_path=False)

    def package_id(self):
        # Pure Python package - no compiler dependencies
        self.info.clear()