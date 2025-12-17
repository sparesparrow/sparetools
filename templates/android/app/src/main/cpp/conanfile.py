from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps
import os

class {{class_name}}Native(ConanFile):
    name = "{{project_name}}-native"
    version = "{{version}}"
    description = "Native dependencies for {{project_name}} Android app"
    license = "{{license}}"
    author = "{{author}}"
    url = "{{repository_url}}"
    topics = ("android", "native", "openssl", "sparetools")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/{{base_version}}"

    # Runtime dependencies
    requires = (
        "sparetools-openssl/{{openssl_version}}",
    )

    # Options
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tests": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tests": False,
        "sparetools-openssl/*:shared": False,
        "sparetools-openssl/*:fPIC": True,
    }

    # Settings for Android cross-compilation
    settings = "os", "arch", "compiler", "build_type"

    # Source files to export
    exports_sources = (
        "CMakeLists.txt",
        "native-lib.cpp",
        "test/*",
    )

    def configure(self):
        # Configure for Android
        if self.settings.os == "Android":
            self.options["sparetools-openssl/*"].shared = False
            self.options["sparetools-openssl/*"].no_threads = False

    def layout(self):
        # Use CMake layout
        self.folders.generators = "build"

    def generate(self):
        # Generate CMake files for Android
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_SYSTEM_NAME"] = "Android"
        tc.variables["CMAKE_SYSTEM_VERSION"] = "21"
        tc.variables["CMAKE_ANDROID_ARCH_ABI"] = self.settings.arch
        tc.variables["CMAKE_ANDROID_NDK"] = os.environ.get("ANDROID_NDK_HOME", "")
        tc.variables["ANDROID_PLATFORM"] = "android-21"
        tc.variables["ANDROID_STL"] = "c++_shared"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def package_info(self):
        # Set up library information
        self.cpp_info.libs = ["native-lib"]

        # Add include directories
        self.cpp_info.includedirs = ["include"]

        # Set system libraries for Android
        self.cpp_info.system_libs = ["android", "log"]