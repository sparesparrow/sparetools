import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, download, unzip

class SpareToolsLvglConan(ConanFile):
    name = "lvgl"
    version = "8.3.11"
    package_type = "library"
    description = "Light and Versatile Graphics Library for embedded systems"
    license = "MIT"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("graphics", "embedded", "gui", "display", "lvgl")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Settings and options
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_bmp": [True, False],
        "with_gif": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": False,
        "with_bmp": False,
        "with_gif": False,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def source(self):
        # Download LVGL source from GitHub releases
        lvgl_url = f"https://github.com/lvgl/lvgl/archive/refs/tags/v{self.version}.zip"
        zip_path = f"lvgl-{self.version}.zip"

        self.output.info(f"Downloading LVGL {self.version} from {lvgl_url}")
        download(self, lvgl_url, zip_path)

        # Extract the archive
        unzip(self, zip_path, strip_root=True)

        # Remove the zip file
        os.remove(zip_path)

    def generate(self):
        # Generate CMake toolchain and dependencies
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        # Copy lv_conf.h to the src directory where lv_conf_internal.h expects it
        import shutil
        lv_conf_src = os.path.join(self.source_folder, "include", "lv_conf.h")
        lv_conf_dst = os.path.join(self.source_folder, "src", "lv_conf.h")
        if os.path.exists(lv_conf_src):
            shutil.copy2(lv_conf_src, lv_conf_dst)
            self.output.info("Copied lv_conf.h to src directory")

    def generate(self):
        # Generate CMake toolchain and dependencies
        tc = CMakeToolchain(self)
        tc.variables["LVGL_BUILD_EXAMPLES"] = "OFF"
        tc.variables["LVGL_BUILD_BENCHMARK"] = "OFF"
        tc.variables["LVGL_BUILD_DEMOS"] = "OFF"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy additional header files
        copy(self, "*.h", src=os.path.join(self.source_folder, "src"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

        # Copy lv_conf.h
        copy(self, "lv_conf.h", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["lvgl"]

        # Component definitions
        self.cpp_info.components["core"].libs = ["lvgl"]
        self.cpp_info.components["core"].requires = []

        # Include directories
        self.cpp_info.includedirs = ["include"]

        # Definitions
        self.cpp_info.defines = [
            "LVGL_VERSION_MAJOR=8",
            "LVGL_VERSION_MINOR=3",
            "LVGL_VERSION_PATCH=11",
            "LVGL_VERSION_INFO=\"\""
        ]

        # Compiler flags for embedded systems
        if self.settings.os in ["baremetal", "freertos"] or str(self.settings.os).startswith("esp"):
            self.cpp_info.cflags = ["-Wno-unused-parameter", "-Wno-missing-field-initializers"]
            self.cpp_info.cxxflags = ["-Wno-unused-parameter", "-Wno-missing-field-initializers"]