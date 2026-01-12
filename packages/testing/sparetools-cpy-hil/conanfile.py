import os
from conan import ConanFile
from conan.tools.files import copy
from conan.errors import ConanException


class SpareToolsCpyHilConan(ConanFile):
    """CPY HIL (Hardware-in-Loop) Testing Environment"""

    name = "sparetools-cpy-hil"
    version = "1.0.0"
    package_type = "application"
    description = "HIL testing environment for Lennox firmware (pytest, python-can, pyserial, etc.)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Use SpareTools base utilities (Conan 2.x pattern)
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # HIL testing packages (based on testing_approaches.txt requirements)
    _hil_packages = [
        "pytest==8.0.0",           # Test framework
        "pytest-timeout==2.2.0",   # Timeout support
        "python-can==4.3.1",       # RSBus/CAN testing (CAN 2.0B, 29-bit identifiers)
        "pyserial==3.5",           # A2L UART testing (4800 bps, CRC-16)
        "pyyaml==6.0.1",           # Requirements traceability
        "hypothesis==6.98.0",      # Property-based testing for safety invariants
        "pandas==2.2.0",           # Data analysis and reporting
        "crcmod==1.7",             # ANSI IBM CRC-16 validation for A2L
        "behave==1.2.6",           # BDD/Gherkin testing matching ES-1856
    ]

    def requirements(self):
        """Require CPython environment"""
        self.requires("sparetools-cpython/3.12.7")

    def build(self):
        """Install HIL packages to isolated site-packages using pip"""

        # Get CPython from dependency
        cpython_dep = self.dependencies["sparetools-cpython"]
        cpython_folder = cpython_dep.package_folder

        python_bin = os.path.join(cpython_folder, "bin", "python3")
        if not os.path.exists(python_bin):
            python_bin = os.path.join(cpython_folder, "bin", "python3.12")

        if not os.path.exists(python_bin):
            raise ConanException(f"Python executable not found: {python_bin}")

        # Create clean Python environment
        import copy
        python_env = copy.copy(os.environ)
        python_env["PYTHONHOME"] = cpython_folder
        python_env["PYTHONPATH"] = os.path.join(cpython_folder, "lib", "python3.12")
        if "LD_LIBRARY_PATH" in python_env:
            python_env["LD_LIBRARY_PATH"] = os.path.join(cpython_folder, "lib")

        # Create isolated site-packages directory
        site_packages = os.path.join(self.build_folder, "lib", "python3.12", "site-packages")
        os.makedirs(site_packages, exist_ok=True)

        self.output.info("=" * 60)
        self.output.info("Installing HIL testing packages")
        self.output.info("=" * 60)

        # Install each package to isolated site-packages
        import subprocess
        for package in self._hil_packages:
            self.output.info(f"📦 Installing {package}...")
            result = subprocess.run(
                [python_bin, "-m", "pip", "install", f"--target={site_packages}", package, "--no-warn-script-location"],
                env=python_env,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.output.error(f"Failed to install {package}: {result.stderr}")
                raise ConanException(f"Failed to install {package}")

        self.output.success(f"✅ All HIL packages installed to: {site_packages}")

    def package(self):
        """Package the installed site-packages"""

        # Copy the entire lib directory (preserving structure)
        copy(self, "*",
             src=os.path.join(self.build_folder, "lib"),
             dst=os.path.join(self.package_folder, "lib"),
             keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Expose HIL site-packages via PYTHONPATH"""

        # Path to HIL site-packages
        site_packages = os.path.join(self.package_folder, "lib", "python3.12", "site-packages")

        # Prepend to PYTHONPATH (higher priority than base)
        self.runenv_info.prepend_path("PYTHONPATH", site_packages)

        # Configuration info for downstream consumers
        self.conf_info.define("user.cpy-hil:site_packages", site_packages)
        self.conf_info.define("user.cpy-hil:packages", ",".join(self._hil_packages))
