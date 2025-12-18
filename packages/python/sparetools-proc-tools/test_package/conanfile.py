import os
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run


class SpareToolsProcToolsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        # Add the package to PYTHONPATH for testing
        pythonpath = self.dependencies[self.tested_reference_str].cpp_info.get_property("pkg_config_name")
        if pythonpath:
            self.env_info.PYTHONPATH.append(pythonpath)

    def test(self):
        if can_run(self):
            # Import and test basic functionality
            import sys
            sys.path.insert(0, self.dependencies[self.tested_reference_str].package_folder)

            try:
                from sparetools_proc_tools import core

                # Test basic command execution
                code, output = core.execute_command_silently(["echo", "test"])
                assert code == 0
                assert len(output) == 0  # Should be silent

                # Test command with output
                code, output = core.execute_command(
                    ["echo", "hello world"],
                    print_command=False,
                    print_out=False
                )
                assert code == 0

                # Test timeout functionality
                code, output = core.run_command_with_timeout(
                    ["sleep", "1"],
                    timeout=5,
                    print_command=False,
                    print_out=False
                )
                assert code == 0

                # Test command building
                cmd = core.build_command_args("ls", "-la", long=True, human_readable=True)
                assert "ls" in cmd
                assert "-la" in cmd
                assert "--long" in cmd
                assert "--human-readable" in cmd

                print("✓ All process management tests passed!")

            except ImportError as e:
                self.output.error(f"Import error: {e}")
                raise
            except Exception as e:
                self.output.error(f"Test failed: {e}")
                raise