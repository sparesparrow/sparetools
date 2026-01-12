import os
import tempfile
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run


class SpareToolsFsToolsTestConan(ConanFile):
    name = 'fs-tools-test'
    version = '1.0.0'
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
                from sparetools_fs_tools import core

                # Test basic file operations
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir = Path(tmpdir)

                    # Test directory creation
                    test_dir = tmpdir / "test_dir"
                    result = core.ensure_directory_exists(test_dir)
                    assert result.exists()
                    assert result.is_dir()

                    # Test file creation and metadata
                    test_file = test_dir / "test.txt"
                    test_file.write_text("test content")
                    metadata = core.get_file_metadata(test_file)
                    assert metadata["is_file"] is True
                    assert metadata["size"] > 0

                    # Test symlink creation
                    link_file = tmpdir / "link.txt"
                    created = core.symlink_with_check(test_file, link_file, target_is_directory=False)
                    assert created is True
                    assert link_file.exists()
                    assert link_file.is_symlink()

                    print("✓ All filesystem tests passed!")

            except ImportError as e:
                self.output.error(f"Import error: {e}")
                raise
            except Exception as e:
                self.output.error(f"Test failed: {e}")
                raise