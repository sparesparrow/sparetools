from conan import ConanFile
from conan.tools.files import copy

class SparetoolsTestFrameworkConan(ConanFile):
    name = "sparetools-test-framework"
    version = "1.0.1"
    package_type = "python-require"
    description = "Core test framework components for SpareTools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Require bundled Python and base utilities
    tool_requires = "sparetools-cpython/3.12.7"
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    exports_sources = [
        "core/**/*.py",
        "test_environments/**/*.py",
        "test_framework/**/*.py",
        "cli/**/*.py",
        "migration/**/*.py"
    ]

    def package(self):
        copy(self, "**/*.py", src=self.source_folder,
             dst=self.package_folder, keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)

        # Add CLI entry point
        self.buildenv_info.define("SPARETOOLS_CLI", f"{self.package_folder}/cli/main.py")