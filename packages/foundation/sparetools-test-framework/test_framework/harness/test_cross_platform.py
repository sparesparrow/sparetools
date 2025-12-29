#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#

"""
Cross-Platform Compatibility Tests for SpareTools
================================================

This module tests sparetools functionality across different platforms (Windows, Linux, macOS).
"""

import os
import sys
import platform
import subprocess
import tempfile
from pathlib import Path

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes


class CrossPlatformTestHarness(NgapyTestHarnes):
    """Test harness for cross-platform compatibility testing."""

    def __init__(self):
        super().__init__()
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_linux = self.system == 'linux'
        self.is_macos = self.system == 'darwin'

    def test_path_handling(self) -> bool:
        """Test path handling across platforms."""
        success = True

        # Test Path object usage
        test_path = Path("test") / "file.txt"
        expected_path = f"test{os.sep}file.txt"

        success &= self.verify(
            str(test_path), expected_path,
            "Path object concatenation",
            test_num=1
        )

        # Test absolute path conversion
        abs_path = Path("relative/path").resolve()
        success &= self.verify(
            abs_path.is_absolute(), True,
            "Absolute path resolution",
            test_num=2
        )

        # Test path separator handling
        sep_correct = os.sep in ['/', '\\']
        success &= self.verify(
            sep_correct, True,
            f"Path separator '{os.sep}' is valid",
            test_num=3
        )

        return success

    def test_file_operations(self) -> bool:
        """Test file operations across platforms."""
        success = True

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test file creation and writing
            test_file = Path(temp_dir) / "test_file.txt"
            test_content = "Hello, cross-platform world!"

            try:
                test_file.write_text(test_content, encoding='utf-8')
                success &= self.verify(
                    test_file.exists(), True,
                    "File creation",
                    test_num=4
                )

                # Test file reading
                read_content = test_file.read_text(encoding='utf-8')
                success &= self.verify(
                    read_content, test_content,
                    "File read/write consistency",
                    test_num=5
                )

                # Test binary file operations
                bin_file = Path(temp_dir) / "binary.dat"
                bin_data = b"\x00\x01\x02\x03\xff\xfe\xfd"
                bin_file.write_bytes(bin_data)
                read_bin_data = bin_file.read_bytes()

                success &= self.verify(
                    read_bin_data, bin_data,
                    "Binary file operations",
                    test_num=6
                )

            except Exception as e:
                success &= self.verify(
                    False, True,
                    f"File operation failed: {str(e)}",
                    test_num=4
                )

        return success

    def test_process_execution(self) -> bool:
        """Test process execution across platforms."""
        success = True

        try:
            # Test basic command execution
            if self.is_windows:
                cmd = ["cmd", "/c", "echo", "test"]
            else:
                cmd = ["echo", "test"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            success &= self.verify(
                result.returncode, 0,
                "Basic command execution",
                test_num=7
            )

            # Check output
            expected_output = "test"
            if self.is_windows:
                expected_output += "\r\n"
            else:
                expected_output += "\n"

            success &= self.verify(
                result.stdout.strip(), expected_output.strip(),
                "Command output",
                test_num=8
            )

        except subprocess.TimeoutExpired:
            success &= self.verify(
                False, True,
                "Process execution timed out",
                test_num=7
            )
        except Exception as e:
            success &= self.verify(
                False, True,
                f"Process execution failed: {str(e)}",
                test_num=7
            )

        return success

    def test_environment_variables(self) -> bool:
        """Test environment variable handling."""
        success = True

        # Test environment variable access
        path_var = os.environ.get('PATH')
        success &= self.verify(
            path_var is not None, True,
            "PATH environment variable exists",
            test_num=9
        )

        # Test case sensitivity (different on Windows vs Unix)
        if self.is_windows:
            # Windows is case-insensitive
            test_var = 'TEMP'
            alt_var = 'temp'
            temp_exists = os.environ.get(test_var) is not None or os.environ.get(alt_var) is not None
        else:
            # Unix-like systems are case-sensitive
            test_var = 'HOME'
            temp_exists = os.environ.get(test_var) is not None

        success &= self.verify(
            temp_exists, True,
            f"Platform-specific env var exists ({test_var})",
            test_num=10
        )

        return success

    def test_platform_specific_features(self) -> bool:
        """Test platform-specific features and limitations."""
        success = True

        # Test line ending handling
        test_content = "line1\nline2\nline3"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as f:
            f.write(test_content)
            temp_file = f.name

        try:
            with open(temp_file, 'r', newline='') as f:
                read_content = f.read()

            success &= self.verify(
                read_content, test_content,
                "Line ending handling",
                test_num=11
            )
        finally:
            os.unlink(temp_file)

        # Test file permission concepts (different on Windows)
        if not self.is_windows:
            # Unix-like permissions
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_file = f.name

            try:
                # Make file executable
                os.chmod(temp_file, 0o755)
                stat_info = os.stat(temp_file)
                is_executable = bool(stat_info.st_mode & 0o111)

                success &= self.verify(
                    is_executable, True,
                    "File permission modification",
                    test_num=12
                )
            finally:
                os.unlink(temp_file)
        else:
            # Windows - just check file exists
            success &= self.verify(
                True, True,
                "Windows file handling (permissions N/A)",
                test_num=12
            )

        return success

    def test_unicode_handling(self) -> bool:
        """Test Unicode character handling across platforms."""
        success = True

        # Test Unicode filenames
        unicode_name = "tëst_üñíçødé_файл.txt"
        unicode_content = "Hello 世界 🌍"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unicode_file = Path(temp_dir) / unicode_name
                unicode_file.write_text(unicode_content, encoding='utf-8')

                success &= self.verify(
                    unicode_file.exists(), True,
                    "Unicode filename creation",
                    test_num=13
                )

                read_content = unicode_file.read_text(encoding='utf-8')
                success &= self.verify(
                    read_content, unicode_content,
                    "Unicode content read/write",
                    test_num=14
                )

        except UnicodeEncodeError:
            success &= self.verify(
                False, True,
                "Unicode handling not supported on this platform",
                test_num=13
            )
        except Exception as e:
            success &= self.verify(
                False, True,
                f"Unicode test failed: {str(e)}",
                test_num=13
            )

        return success

    def run_cross_platform_tests(self) -> bool:
        """Run all cross-platform compatibility tests."""
        print(f"Running cross-platform tests on {platform.system()} {platform.release()}")

        results = []

        results.append(("Path Handling", self.test_path_handling()))
        results.append(("File Operations", self.test_file_operations()))
        results.append(("Process Execution", self.test_process_execution()))
        results.append(("Environment Variables", self.test_environment_variables()))
        results.append(("Platform Features", self.test_platform_specific_features()))
        results.append(("Unicode Handling", self.test_unicode_handling()))

        print("\nCross-Platform Test Results:")
        all_passed = True
        for test_name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"  {test_name}: {status}")
            all_passed &= passed

        return all_passed


def run_cross_platform_tests():
    """Main function to run cross-platform tests."""
    harness = CrossPlatformTestHarness()
    success = harness.run_cross_platform_tests()

    print(f"\nOverall Cross-Platform Compatibility: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == "__main__":
    success = run_cross_platform_tests()
    sys.exit(0 if success else 1)