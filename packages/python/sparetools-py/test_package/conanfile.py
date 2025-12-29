import os
from conan import ConanFile

class SparetoolsPyTestConan(ConanFile):

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.tool_requires("sparetools-cpython/3.12.7")

    def test(self):
        # Run Python tests
        python_exe = self.conf.get("user.cpython:executable", "python3")

        # Import and test the Python package
        import subprocess
        result = subprocess.run([
            python_exe, "-c",
            f"""
import sys
sys.path.insert(0, r'{self.dependencies["sparetools-py"].package_folder}')
try:
    import sparetools
    print('✓ sparetools package imported successfully')
    print(f'✓ Version: {{sparetools.__version__}}')

    # Test basic imports
    from sparetools.bpm_decoder import BPMDecoder
    from sparetools.test_harness import ProtocolTestHarness
    from sparetools.conan_helpers import ConanHelper

    print('✓ All modules imported successfully')

    # Test BPMDecoder instantiation
    decoder = BPMDecoder()
    print('✓ BPMDecoder created successfully')

    # Test ProtocolTestHarness instantiation
    harness = ProtocolTestHarness()
    print('✓ ProtocolTestHarness created successfully')

    print('🎉 All Python package tests passed!')

except Exception as e:
    print(f'❌ Test failed: {{e}}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
            """
        ], capture_output=True, text=True)

        if result.returncode != 0:
            self.output.error(f"Python package test failed: {result.stderr}")
            raise Exception(f"Test failed with exit code {result.returncode}")

        self.output.info("Python package test output:")
        self.output.info(result.stdout)
