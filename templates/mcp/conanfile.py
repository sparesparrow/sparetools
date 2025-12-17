from conan import ConanFile
from conan.tools.files import copy
from conan.tools.python import PythonDeps
import os

class {{class_name}}McpServer(ConanFile):
    name = "{{project_name}}"
    version = "{{version}}"
    description = "{{project_description}}"
    license = "{{license}}"
    author = "{{author}}"
    url = "{{repository_url}}"
    topics = ("mcp", "server", "ai", "assistant", "{{topic1}}", "{{topic2}}")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/{{base_version}}"

    # Tool requirements - hermetic Python environment
    tool_requires = (
        "sparetools-cpython/{{cpython_version}}",
    )

    # Runtime dependencies
    requires = (
        "sparetools-openssl/{{openssl_version}}",
    )

    # Options
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tests": [True, False],
        "with_docker": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tests": True,
        "with_docker": False,
    }

    # Settings
    settings = "os", "compiler", "build_type", "arch"

    # Source files to export
    exports_sources = (
        "pyproject.toml",
        "src/*",
        "scripts/*",
        "docker/*",
        "requirements*.txt",
    )

    def configure(self):
        # OpenSSL settings
        self.options["sparetools-openssl/*"].shared = self.options.shared
        self.options["sparetools-openssl/*"].fPIC = self.options.fPIC

    def requirements(self):
        # Additional MCP-related dependencies
        # These would be added as needed for specific MCP functionality
        pass

    def layout(self):
        # Use Python layout
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = "build/conan"

    def generate(self):
        # Generate Python dependencies
        py_deps = PythonDeps(self)
        py_deps.generate()

    def build(self):
        # Build Python package
        self.run("python -m pip install -e .")

    def package(self):
        # Package Python source
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"))
        copy(self, "pyproject.toml", self.source_folder, self.package_folder)

        # Package scripts
        copy(self, "*.py", os.path.join(self.source_folder, "scripts"),
             os.path.join(self.package_folder, "bin"), keep_path=False)

        # Package Docker files if enabled
        if self.options.with_docker:
            copy(self, "*", os.path.join(self.source_folder, "docker"),
                 os.path.join(self.package_folder, "docker"))

    def package_info(self):
        # Set Python path
        self.conf_info["user.cpython:site_packages"] = os.path.join(self.package_folder, "src")

        # Set environment variables for consumers
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "src"))

        # Add scripts to PATH
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def package_id(self):
        # Package ID should be platform-independent for Python packages
        # unless they contain compiled extensions
        pass