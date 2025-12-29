import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.cmake import CMakeToolchain, CMakeDeps
from conan.tools.layout import basic_layout

class SparetoolsPyConan(ConanFile):
    name = "sparetools-py"
    version = "1.0.0"
    package_type = "application"

    # Python package with protocol tools and test harness
    python_requires = "sparetools-base/2.0.0"
    tool_requires = "sparetools-cpython/3.12.7"

    exports_sources = "setup.py", "sparetools/*", "README.md"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        # Protocol schemas for Python decoding
        self.requires("sparesparrow-protocols/1.0.0")

        # FlatBuffers for Python protocol handling
        self.requires("flatbuffers/24.3.25")

    def build(self):
        # Build Python package - typically just copy files
        # Could add C extensions if needed
        pass

    def package(self):
        # Copy Python package files
        copy(self, "setup.py", src=self.source_folder, dst=self.package_folder)
        copy(self, "sparetools/**/*.py", src=self.source_folder, dst=self.package_folder)
        copy(self, "README.md", src=self.source_folder, dst=self.package_folder)

        # Copy any built extensions if they exist
        copy(self, "*.so", src=self.source_folder, dst=os.path.join(self.package_folder, "sparetools"))
        copy(self, "*.pyd", src=self.source_folder, dst=os.path.join(self.package_folder, "sparetools"))

    def package_info(self):
        # Set up Python environment
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)

        # Console scripts
        self.runenv_info.define("SPARETOOLS_PY_PACKAGE_DIR", self.package_folder)

    def package_id(self):
        # Python packages are typically platform-independent
        # unless they contain native extensions
        self.info.clear()
