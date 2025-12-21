from conan import ConanFile
from conan.tools.files import copy
import yaml
import os
from pathlib import Path


def _load_versions():
    """Load versions from versions.yaml file"""
    versions_file = Path(__file__).parent.parent.parent.parent / "versions.yaml"
    if versions_file.exists():
        try:
            with open(versions_file, 'r') as f:
                data = yaml.safe_load(f)
                # Flatten the nested structure
                versions = {}
                for category, packages in data.items():
                    if isinstance(packages, dict):
                        versions.update(packages)
                return versions
        except Exception:
            pass
    # Fallback to hardcoded versions if file not found or parsing fails
    return {
        "cpython": "3.12.7",
        "test-harness": "2.0.0",
        "gtest": "1.14.0",
        "shared-dev-tools": "2.0.0",
        "bootstrap": "2.0.0",
        "openssl": "3.3.2",
        "lvgl": "8.3.11",
        "test": "1.0.0"
    }


class SpareToolsVersions:
    """Centralized version management for SpareTools ecosystem"""
    versions = _load_versions()


class SpareToolsBaseConan(ConanFile):
    name = "sparetools-base"
    version = "2.0.3"
    package_type = "python-require"
    description = "Foundation utilities for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    exports_sources = "*.py"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "sparetools/**/*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = []
        # Conan 2.x API: Use buildenv_info for build-time Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
