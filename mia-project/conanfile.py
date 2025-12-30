from conan import ConanFile
from conan.tools.files import copy
import os

class MiaProject(ConanFile):
    name = "mia-project"
    version = "1.0.1"
    description = "{{project_description}}"
    license = "MIT"
    author = "Your Name"
    url = "https://github.com/yourusername/mia-project"
    topics = ("python", "cryptography", "mia", "python")

    # Foundation layer
    python_requires = "sparetools-base/2.0.3"

    # Runtime + testing
    tool_requires = (
        "sparetools-cpython/3.12.7",
        "sparetools-test-harness/2.0.3",
        "sparetools-obd-sim/2.0.0",
    )

    # Interface contracts (ICD)
    build_requires = (
        # "sparetools-icd/2.0.0",  # TODO: Package not yet created - see docs/PROJECT-RELATIONSHIPS-ANALYSIS.md
        "sparetools-tinymcp/2.0.0",
        "sparetools-mcp-orchestrator/2.0.0",
    )

    # Runtime dependencies
    requires = (
        "zeromq/4.3.5",
        "flatbuffers/23.5.26",
        "paho-mqtt/1.6.1",  # For NucleusESP32 MQTT option
        "sparetools-mia/2.0.0",
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
        "with_tests": True,
    }

    # Settings
    settings = "os", "compiler", "build_type", "arch"

    # Source files to export
    exports_sources = (
        "pyproject.toml",
        "src/*",
        "scripts/*",
        "requirements*.txt",
    )

    def configure(self):
        # OpenSSL settings
        self.options["sparetools-openssl/*"].shared = self.options.shared
        self.options["sparetools-openssl/*"].fPIC = self.options.fPIC

    def requirements(self):
        # Additional Python packages can be added here
        pass

    def layout(self):
        # Use Python layout
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = "build/conan"


    def build(self):
        # Build Python package - skip pip install for now
        # self.run("python -m pip install -e .")

        # Build any C extensions if needed
        # self.run("python setup.py build_ext --inplace")
        pass

    def package(self):
        # Package Python source
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"))
        copy(self, "pyproject.toml", self.source_folder, self.package_folder)

        # Package compiled extensions
        copy(self, "*.so", self.build_folder, os.path.join(self.package_folder, "src"), keep_path=False)
        copy(self, "*.pyd", self.build_folder, os.path.join(self.package_folder, "src"), keep_path=False)

    def package_info(self):
        # Set Python path
        self.conf_info.define("user.cpython:site_packages", os.path.join(self.package_folder, "src"))

        # Set environment variables for consumers (Conan 2.x API)
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "src"))

    def package_id(self):
        # Package ID should be platform-independent for Python packages
        # unless they contain compiled extensions
        pass