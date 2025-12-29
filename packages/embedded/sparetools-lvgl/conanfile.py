import os
from conan import ConanFile
from conan.tools.files import copy

class SpareToolsLvglConan(ConanFile):
    name = "lvgl"
    version = "8.3.11"
    package_type = "header-library"
    description = "Light and Versatile Graphics Library configuration for embedded systems"
    license = "MIT"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("graphics", "embedded", "gui", "display", "lvgl")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Export the header file
    exports_sources = "include/lv_conf.h"

    def package(self):
        # For header-only package, just copy the configuration header
        copy(self, "lv_conf.h", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=False)

    def package_info(self):
        # Provide basic LVGL defines for compatibility
        self.cpp_info.defines = [
            "LVGL_VERSION_MAJOR=8",
            "LVGL_VERSION_MINOR=3",
            "LVGL_VERSION_PATCH=11",
            "LVGL_VERSION_INFO=\"\""
        ]

        # Include directories
        self.cpp_info.includedirs = ["include"]