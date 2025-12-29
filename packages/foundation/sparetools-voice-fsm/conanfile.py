from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy

class SparetoolsVoiceFsmConan(ConanFile):
    name = "sparetools-voice-fsm"
    version = "1.0.0"
    package_type = "library"
    description = "Voice control finite state machine using Boost.SML"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    settings = "os", "compiler", "build_type", "arch"

    # Dependencies
    requires = "boost/1.83.0"
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    exports_sources = "include/*", "src/*", "CMakeLists.txt"

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
        copy(self, "*.hpp", src="include", dst="include", keep_path=True)
        copy(self, "*.h", src="include", dst="include", keep_path=True)
        copy(self, "*.lib", src="build", dst="lib", keep_path=False)
        copy(self, "*.a", src="build", dst="lib", keep_path=False)
        copy(self, "*.so", src="build", dst="lib", keep_path=False)
        copy(self, "*.dylib", src="build", dst="lib", keep_path=False)
        copy(self, "*.dll", src="build", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["voice_control_fsm"]
        self.cpp_info.includedirs = ["include"]