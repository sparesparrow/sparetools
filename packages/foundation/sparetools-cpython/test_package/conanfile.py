from conan import ConanFile
from conan.tools.build import can_run
import os


class SparetoolsCPythonTestConan(ConanFile):
    name = 'cpython-test'
    version = '1.0.0'
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            # Test 1: Python executable exists and is runnable
            python_bin = os.path.join(self.dependencies["sparetools-cpython"].package_folder,
                                     "bin",
                                     "python.exe" if self.settings.os == "Windows" else "python3")

            # Fallback to python3.12 if python3 doesn't exist
            if not os.path.exists(python_bin):
                python_bin = os.path.join(self.dependencies["sparetools-cpython"].package_folder,
                                         "bin",
                                         "python.exe" if self.settings.os == "Windows" else "python3.12")

            if not os.path.exists(python_bin):
                raise Exception(f"Python binary not found at expected locations")

            self.output.info(f"Found Python at: {python_bin}")

            # Test 2: Python version check
            self.run(f'"{python_bin}" --version', env="conanrun")

            # Test 3: Python can import sys and print
            self.run(f'"{python_bin}" -c "import sys; print(f\'Python {{sys.version}}\');"', env="conanrun")

            # Test 4: Verify standard library is available
            self.run(f'"{python_bin}" -c "import json, os, sys; print(\'Standard library OK\');"', env="conanrun")

            # Test 5: Check PYTHONHOME environment variable is set
            self.output.info("Testing environment variables...")
            self.run(f'"{python_bin}" -c "import os; print(f\'PYTHONHOME={{os.environ.get(\\\"PYTHONHOME\\\", \\\"NOT SET\\\")}}\')"', env="conanrun")

            self.output.success("All CPython tests passed!")
