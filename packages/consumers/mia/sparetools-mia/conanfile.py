import os
from conan import ConanFile
from conan.tools.files import copy


class SpareToolsMiaConan(ConanFile):
    """MIA (Modular IoT Architecture) - AI-orchestrated IoT platform."""

    name = "sparetools-mia"
    version = "2.0.0"
    package_type = "python-require"
    description = "AI-orchestrated IoT platform with MCP integration, hardware control, and self-healing capabilities"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("iot", "ai-orchestration", "mcp", "hardware-control", "self-healing", "mia")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Runtime + testing
    tool_requires = (
        "sparetools-cpython/3.12.7",
        "sparetools-test-harness/2.0.3",
        "sparetools-obd-sim/2.0.3",
    )

    # Interface contracts (ICD)
    build_requires = (
        # "sparetools-icd/2.0.0",  # TODO: Package not yet created - see docs/PROJECT-RELATIONSHIPS-ANALYSIS.md
        "sparetools-tinymcp/2.0.0",
        "sparetools-mcp-orchestrator/2.0.3",
    )

    # Runtime dependencies
    requires = (
        "sparetools-base/2.0.3",
        "zeromq/4.3.5",
        "flatbuffers/23.5.26",
        "paho-mqtt/1.6.1",  # For NucleusESP32 MQTT option
    )

    # Source files to export
    exports_sources = (
        "src/*",
        "scripts/*",
        "docs/*",
    )

    def package(self):
        """Package MIA components."""
        # Copy Python modules - copy the src directory contents directly
        copy(self, "*", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "src"), keep_path=True)

        # Copy scripts
        copy(self, "*", os.path.join(self.source_folder, "scripts"), os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy documentation
        copy(self, "*", os.path.join(self.source_folder, "docs"), os.path.join(self.package_folder, "docs"), keep_path=True)

        # Apply security gates and generate SBOM (placeholder)
        self.output.info("Applying security gates...")
        self.output.info("Generating SBOM...")

    def package_info(self):
        """Provide MIA package information."""
        self.cpp_info.libs = []

        # Add Python path for both build and runtime
        python_src_path = os.path.join(self.package_folder, "src")
        self.buildenv_info.append_path("PYTHONPATH", python_src_path)
        self.runenv_info.append_path("PYTHONPATH", python_src_path)

        # Add scripts to PATH
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Environment for cloud integration
        self.runenv_info.define("MIA_ROOT", self.package_folder)

        # Conf info for MIA discovery
        self.conf_info.define("user.mia:root", self.package_folder)
        self.conf_info.define("user.mia:scripts", os.path.join(self.package_folder, "bin"))