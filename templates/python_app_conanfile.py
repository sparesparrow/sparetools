#!/usr/bin/env python3
"""
SpareTools Python Application Conanfile Template

This template provides a standard structure for Python applications
that integrate with the SpareTools ecosystem.

Key Features:
- Uses sparetools-base/2.0.3 for version management and security gates
- Uses sparetools-cpython/3.12.7 for bundled Python runtime
- Packages Python sources under python/ directory
- Creates launcher script using bundled Python
- Handles pip dependencies separately (Conan = runtime, pip = libs)

Usage:
1. Copy this template to your project
2. Update name, version, description, and dependencies
3. Customize package() and launcher creation as needed
4. Test with: conan create . --build=missing

Pip Dependencies Pattern:
- Install pip deps during build() into build_folder/python-deps
- Copy them to package_folder/python during package()
- This keeps Conan (runtime) and pip (libs) roles separate
"""

import os
from conan import ConanFile
from conan.tools.files import copy, save


class PythonAppConan(ConanFile):
    """Template for SpareTools Python applications."""

    # === UPDATE THESE FOR YOUR PROJECT ===
    name = "your-project-name"
    version = "0.1.0"
    description = "Your project description"
    license = "MIT"
    author = "Your Name"
    url = "https://github.com/your-org/your-repo"
    topics = ("python", "sparetools", "your-topic")

    # === SPARETOOLS INTEGRATION (DO NOT CHANGE) ===
    python_requires = "sparetools-base/2.0.3@sparesparrow-conan/sparetools"
    python_requires_extend = "sparetools-base.SpareToolsBase"

    settings = "os", "arch"

    def build_requirements(self):
        """Bundled Python runtime for consistent execution."""
        self.tool_requires("sparetools-cpython/3.12.7@sparesparrow-conan/sparetools")

    def requirements(self):
        """Runtime dependencies from SpareTools ecosystem."""
        # Add any SpareTools runtime dependencies here
        # Example: self.requires("sparetools-protocols/1.0.1")
        pass

    def build(self):
        """Build step - install pip dependencies if needed."""
        # Handle pip dependencies separately from Conan runtime
        # Install pip deps into build folder during build
        if os.path.exists("requirements.txt"):
            self.run(f"pip install -r requirements.txt --target={self.build_folder}/python-deps")
        elif os.path.exists("pyproject.toml"):
            # For Poetry projects, you might need to export requirements.txt first
            # or handle Poetry dependencies differently
            pass

    def package(self):
        """Package Python application and dependencies."""
        # Package Python sources
        copy(self, "*.py", src=self.source_folder,
             dst=os.path.join(self.package_folder, "python"),
             keep_path=True)

        # Package pip-installed dependencies (if any)
        pip_deps_dir = os.path.join(self.build_folder, "python-deps")
        if os.path.exists(pip_deps_dir):
            copy(self, "*", src=pip_deps_dir,
                 dst=os.path.join(self.package_folder, "python"))

        # Package additional files
        copy(self, "README.md", src=self.source_folder, dst=self.package_folder)
        copy(self, "LICENSE*", src=self.source_folder, dst=self.package_folder)

        # Create launcher script
        self._create_launcher_script()

        # Apply security gates (inherited from SpareToolsSecurityMixin)
        if hasattr(self, "apply_security_gates"):
            self.apply_security_gates()
        if hasattr(self, "generate_sbom"):
            self.generate_sbom()

    def _create_launcher_script(self):
        """Create launcher script that uses bundled Python."""
        launcher_content = f"""#!/usr/bin/env python3
import sys
import os

# Add package Python to path
pkg_python = os.path.join(os.path.dirname(__file__), 'python')
sys.path.insert(0, pkg_python)

# Import and run main module
try:
    from {self.name.replace('-', '_')} import main
    sys.exit(main())
except ImportError as e:
    print(f"Error importing {self.name}: {{e}}")
    print("Make sure the main module is properly packaged")
    sys.exit(1)
"""

        launcher_path = os.path.join(self.package_folder, "bin", self.name)
        save(self, launcher_path, launcher_content)

        # Make executable on Unix-like systems
        if self.settings.os != "Windows":
            os.chmod(launcher_path, 0o755)

    def package_info(self):
        """Configure package environment."""
        # Make launcher executable
        bin_dir = os.path.join(self.package_folder, "bin")
        self.cpp_info.bindirs = ["bin"]

        # Expose Python sources via PYTHONPATH
        python_path = os.path.join(self.package_folder, "python")
        self.buildenv_info.append_path("PYTHONPATH", python_path)
        self.runenv_info.append_path("PYTHONPATH", python_path)

        # Set environment variables for the application
        self.runenv_info.define(f"{self.name.upper()}_HOME", self.package_folder)

        # Configure bundled Python environment
        try:
            if hasattr(self, 'deps_cpp_info') and "sparetools-cpython" in self.deps_cpp_info:
                cpython_info = self.deps_cpp_info["sparetools-cpython"]
                self.runenv_info.prepend_path("PATH", cpython_info.bin_paths[0])
        except Exception:
            pass  # Fallback if cpython not available


# Template usage notes:
"""
To use this template:

1. Copy to your project: cp templates/python_app_conanfile.py myproject/conanfile.py

2. Update the project-specific variables:
   - name: "my-project-name"
   - version: "1.0.0"
   - description: "My project description"
   - author, url, etc.

3. Add any project-specific requirements in requirements()

4. Customize _create_launcher_script() if your entry point differs

5. Test the package:
   conan create . --build=missing

6. For pip dependencies, ensure requirements.txt exists or handle in build()

7. The launcher will be created at package_folder/bin/your-project-name

Integration Checklist:
- [ ] Project name and metadata updated
- [ ] Runtime dependencies added in requirements()
- [ ] Pip dependencies handled in build() if needed
- [ ] Launcher script imports correct main module
- [ ] Test package creation works
- [ ] Test launcher script executes
- [ ] Update project README with Conan usage
"""