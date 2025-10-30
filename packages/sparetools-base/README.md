# sparetools-base

Foundation python_requires package for SpareTools ecosystem.

## Features

- **Zero-copy symlink utilities** - NGA aerospace pattern
- **Security gates** - Trivy, Syft, FIPS validation
- **Conan extensions** - Custom helpers and tools

## Usage
from conan import ConanFileclass MyProject(ConanFile):
python_requires = "sparetools-base/1.0.0"def build(self):
    # Access utilities
    base = self.python_requires["sparetools-base"].module
    base.create_zero_copy_environment(self, "openssl", "./DEPS/openssl")
## Export
cd packages/sparetools-base
conan export . --version=1.0.0


