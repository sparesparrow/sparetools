from conan import ConanFile
from conan.tools.files import copy
import os

class SparetoolsPythonScriptsConan(ConanFile):
    name = "sparetools-python-scripts"
    version = "1.0.0"
    license = "Apache-2.0"
    description = "Runtime Python utility modules for SpareTools projects"
    author = "SpareTools Team"
    topics = ("utilities", "python", "conan", "tools")

    # This is an APPLICATION package (not python-require)
    package_type = "application"

    # Export only Python modules (exclude test_env, __pycache__)
    exports_sources = (
        "sparetools/**/*.py",
        "README.md",
        "!**/__pycache__",
        "!**/*.pyc",
        "!**/*.pyo",
    )

    def package(self):
        # Copy all sparetools modules to lib/python/
        copy(self, "*.py",
             src=os.path.join(self.source_folder, "sparetools"),
             dst=os.path.join(self.package_folder, "lib", "python", "sparetools"),
             keep_path=True)

    def package_info(self):
        # Set PYTHONPATH for both build-time and runtime use
        pythonpath = os.path.join(self.package_folder, "lib", "python")

        # Build-time: Used in generate(), build() methods
        self.buildenv_info.prepend_path("PYTHONPATH", pythonpath)

        # Runtime: Used when running scripts with bundled cpython
        self.runenv_info.prepend_path("PYTHONPATH", pythonpath)
