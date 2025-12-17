from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy
import os

class {{class_name}}(ConanFile):
    name = "{{project_name}}"
    version = "{{version}}"
    description = "{{project_description}}"
    license = "{{license}}"
    author = "{{author}}"
    url = "{{repository_url}}"
    topics = ("{{topic1}}", "{{topic2}}")

    # Optional python_requires for shared utilities
    python_requires = "sparetools-base/{{base_version}}"

    # Dependencies
    {% if requires %}
    requires = (
    {% for req in requires %}
        "{{req}}",
    {% endfor %}
    )
    {% endif %}

    # Tool requirements
    {% if tool_requires %}
    tool_requires = (
    {% for tool in tool_requires %}
        "{{tool}}",
    {% endfor %}
    )
    {% endif %}

    # Options
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # Settings
    settings = "os", "compiler", "build_type", "arch"

    # Source and build directories
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # Add any additional requirements here
        pass

    def generate(self):
        # Generate build files
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Copy headers
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*.hpp", self.source_folder, os.path.join(self.package_folder, "include"), keep_path=False)

        # Copy libraries
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["{{project_name}}"]

        # Set environment variables if needed
        # self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))