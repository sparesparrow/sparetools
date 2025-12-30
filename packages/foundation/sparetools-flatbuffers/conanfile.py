from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os


class SparetoolsFlatbuffersConan(ConanFile):
    """SpareTools FlatBuffers - FlatBuffers compiler and runtime for SpareTools ecosystem."""

    name = "sparetools-flatbuffers"
    version = "24.3.26"
    package_type = "application"

    # SpareTools foundation package
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Optional metadata
    license = "Apache-2.0"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/sparetools"
    description = "FlatBuffers compiler and runtime for SpareTools ecosystem"
    topics = ("flatbuffers", "serialization", "compiler", "sparetools", "foundation")

    # Settings for cross-platform builds
    settings = "os", "compiler", "build_type", "arch"

    # Export CMakeLists.txt for building from source if needed
    exports_sources = "CMakeLists.txt"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        # FlatBuffers runtime library - matches our compiler version
        self.requires("flatbuffers/24.3.25")

    def build_requirements(self):
        # Build tools needed for FlatBuffers compilation
        self.tool_requires("cmake/[>=3.25]")
        # Use bundled CPython for any Python build scripts
        self.tool_requires("sparetools-cpython/3.12.7")

    def configure(self):
        # FlatBuffers doesn't need compiler-specific features
        pass

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Package the flatc compiler binary from the FlatBuffers library
        flatc_path = None

        # Find flatc in the FlatBuffers package
        deps = self.dependencies
        flatbuffers_dep = deps["flatbuffers"]

        # Look for flatc in various locations
        possible_paths = [
            os.path.join(flatbuffers_dep.package_folder, "bin", "flatc"),
            os.path.join(flatbuffers_dep.package_folder, "bin", "flatc.exe"),
            os.path.join(flatbuffers_dep.package_folder, "tools", "flatc"),
            os.path.join(flatbuffers_dep.package_folder, "tools", "flatc.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                flatc_path = path
                break

        if flatc_path:
            # Copy flatc binary to our package
            copy(self, os.path.basename(flatc_path),
                 src=os.path.dirname(flatc_path),
                 dst=os.path.join(self.package_folder, "bin"),
                 keep_path=False)

            # Make it executable on Unix-like systems
            if self.settings.os != "Windows":
                os.chmod(os.path.join(self.package_folder, "bin", "flatc"), 0o755)

        # Copy any additional FlatBuffers tools or resources
        copy(self, "*",
             src=os.path.join(flatbuffers_dep.package_folder, "bin"),
             dst=os.path.join(self.package_folder, "bin"))

        # Copy FlatBuffers headers for convenience
        if os.path.exists(os.path.join(flatbuffers_dep.package_folder, "include")):
            copy(self, "*.h",
                 src=os.path.join(flatbuffers_dep.package_folder, "include"),
                 dst=os.path.join(self.package_folder, "include"))

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Make flatc available in PATH
        bin_path = os.path.join(self.package_folder, "bin")
        self.buildenv_info.append_path("PATH", bin_path)
        self.runenv_info.append_path("PATH", bin_path)

        # Define flatc executable path for consumers
        flatc_exe = "flatc.exe" if self.settings.os == "Windows" else "flatc"
        flatc_path = os.path.join(bin_path, flatc_exe)
        self.conf_info.define("user.flatbuffers:flatc", flatc_path)

        # Version information
        self.cpp_info.defines = [f"SPARETOOLS_FLATBUFFERS_VERSION={self.version}"]

        # Include FlatBuffers headers if packaged
        if os.path.exists(os.path.join(self.package_folder, "include")):
            self.cpp_info.includedirs = ["include"]
        else:
            # Forward includes from the flatbuffers dependency
            self.cpp_info.requires = ["flatbuffers::flatbuffers"]

    def package_id(self):
        # Package ID should be platform-specific for the flatc binary
        # but we can clear build_type since flatc works the same in debug/release
        self.info.clear()

    def validate(self):
        # Ensure FlatBuffers dependency is available
        if not self.dependencies.get("flatbuffers"):
            raise ConanException("FlatBuffers dependency not found")

        # Note: package_folder validation moved to package_info to avoid None errors