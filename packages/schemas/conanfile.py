import os
from conan import ConanFile
from conan.tools.files import copy

class ProtocolsConan(ConanFile):
    name = "sparesparrow-protocols"
    version = "1.0.0"
    package_type = "header-library"

    exports_sources = "*.fbs", "CMakeLists.txt"

    def build_requirements(self):
        self.tool_requires("flatbuffers/24.3.25")

    def build(self):
        # Generate C++ headers for all schemas
        import os
        schemas = ["BPM.fbs", "MIA.fbs", "MCP.fbs", "VEHICLE.fbs", "common.fbs"]
        for schema in schemas:
            if os.path.exists(schema):
                self.run(f"flatc --cpp --scoped-enums {schema}")

    def package(self):
        # Copy generated headers and original schemas
        copy(self, "*_generated.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.fbs", src=self.source_folder, dst=os.path.join(self.package_folder, "schemas"))

    def package_info(self):
        # Component per schema (independent versioning)
        self.cpp_info.components["bpm"].includedirs = ["include"]
        self.cpp_info.components["mia"].includedirs = ["include"]
        self.cpp_info.components["mcp"].includedirs = ["include"]
        self.cpp_info.components["vehicle"].includedirs = ["include"]
        self.cpp_info.components["common"].includedirs = ["include"]

        # Clear platform-specific settings for header-only package
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

    def package_id(self):
        # Make package ID platform-independent (typical for header-only)
        self.info.clear()

    def layout(self):
        # Use basic layout
        pass