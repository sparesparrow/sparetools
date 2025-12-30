from conan import ConanFile
from conan.tools.files import copy
import os

class SparetoolsEmbeddedConan(ConanFile):
    name = "sparetools-embedded"
    version = "1.0.1"
    package_type = "library"
    description = "Embedded systems libraries for SpareTools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    options = {"shared": [True, False]}
    default_options = {"shared": False}

    # Require test framework and base utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Runtime dependencies
    requires = "sparetools-test-framework/1.0.0"

    # Additional dependencies for embedded testing
    tool_requires = "sparetools-cpython/3.12.7"

    # Export both Python and C++ sources
    exports_sources = (
        "CMakeLists.txt",
        "include/**/*",
        "src/**/*",
        "sparetools_embedded/**/*.py"
    )

    def build(self):
        # Could build C++ components here if needed
        pass

    def package(self):
        # Package Python modules
        copy(self, "**/*.py", src=self.source_folder,
             dst=self.package_folder, keep_path=True)

        # Package C++ headers
        copy(self, "**/*.h", src=self.source_folder,
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

        # Package C++ sources if needed for header-only usage
        copy(self, "**/*.c", src=self.source_folder,
             dst=os.path.join(self.package_folder, "src"), keep_path=True)
        copy(self, "**/*.cpp", src=self.source_folder,
             dst=os.path.join(self.package_folder, "src"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Expose Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)

        # Expose C++ headers
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.srcdirs = ["src"]