from conan import ConanFile
from pathlib import Path
import sys


class SparetoolsTestHarnessTestConan(ConanFile):
    """
    Test package for sparetools-test-harness python_requires.

    Validates that the test harness loads correctly and provides
    ngapy-compatible verification methods.
    """
    test_type = "explicit"
    python_requires = "sparetools-test-harness/[>=2.0.0]"

    def test(self):
        # Test 1: Verify python_requires loaded successfully
        try:
            test_harness_ref = self.python_requires["sparetools-test-harness"]
            self.output.success("✅ sparetools-test-harness loaded as python_requires")
            self.output.info(f"   Reference: {test_harness_ref}")
        except Exception as e:
            raise Exception(f"Failed to load sparetools-test-harness: {e}")

        # Test 2: Import and validate SpareToolsTestHarness class
        try:
            harness_module_path = self.python_requires["sparetools-test-harness"].module_folder
            sys.path.insert(0, harness_module_path)

            from sparetools_test_harness import SpareToolsTestHarness, ThLogger, VerificationMethods
            self.output.success("✅ Successfully imported SpareToolsTestHarness classes")
        except ImportError as e:
            raise Exception(f"Failed to import test harness classes: {e}")

        # Test 3: Validate ngapy-compatible API
        try:
            th = SpareToolsTestHarness()

            # Test basic verification methods
            result1 = th.verify(2 + 2, 4, "Basic arithmetic", test_num=1)
            result2 = th.verify_tol(3.14159, 3.14, 0.01, "Pi approximation", test_num=2)
            result3 = th.verify_range(5, 1, 10, "Value in range", test_num=3)
            result4 = th.verify_ne(5, 3, "Not equal check", test_num=4)
            result5 = th.verify_string("hello", "hello", "String equality", test_num=5)

            if all([result1, result2, result3, result4, result5]):
                self.output.success("✅ All ngapy-compatible verification methods work")
            else:
                raise Exception("Some verification methods failed")

        except Exception as e:
            raise Exception(f"Failed to validate ngapy-compatible API: {e}")

        # Test 4: Validate logging and reporting
        try:
            summary = th.get_summary()
            self.output.success("✅ Test summary generation works")
            self.output.info(f"   Summary: {summary}")

            # Test JUnit report generation
            test_results_dir = Path(self.build_folder) / "test-results"
            test_results_dir.mkdir(exist_ok=True)
            junit_file = test_results_dir / "test_report.xml"
            th.generate_junit_report(str(junit_file))

            if junit_file.exists():
                self.output.success("✅ JUnit XML report generation works")
            else:
                raise Exception("JUnit report file was not created")

        except Exception as e:
            raise Exception(f"Failed to validate logging and reporting: {e}")

        # Test 5: Validate pytest integration
        try:
            from sparetools_test_harness.pytest_plugin import PytestTestHarness
            self.output.success("✅ Pytest integration classes available")
        except ImportError as e:
            raise Exception(f"Failed to import pytest integration: {e}")

        self.output.success("✅ Test harness package validation complete!")
        self.output.info("")
        self.output.info("Validated functionality:")
        self.output.info("  - python_requires loading")
        self.output.info("  - ngapy-compatible API methods")
        self.output.info("  - Structured logging and JUnit XML output")
        self.output.info("  - Pytest integration support")
        self.output.info("  - Test summary generation")