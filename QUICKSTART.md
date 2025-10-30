# SpareTools Quick Start

## Installation

### 1. Add Cloudsmith Remote (One-time)

```bash
conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
```

Or use the legacy Cloudsmith URL:
```bash
conan remote add cloudsmith https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/index.json
```

### 2. Install SpareTools CPython

```bash
# Download and deploy
conan install --requires=sparetools-cpython/3.12.7 -r sparesparrow-conan --deployer=full_deploy

# Activate environment
source full_deploy/host/sparetools-cpython/3.12.7/*/activate.sh

# Verify
python3 --version  # Should show: Python 3.12.7
python --version   # Should also work
```

### 3. Use in Your Project

```python
# In your conanfile.py
from conan import ConanFile

class MyOpenSSLProject(ConanFile):
    python_requires = "sparetools-base/1.0.0"
    tool_requires = "sparetools-cpython/3.12.7"
    
    def build(self):
        # Access zero-copy utilities
        base = self.python_requires["sparetools-base"].module
        base.create_zero_copy_environment(
            self,
            "sparetools-cpython",
            "./TOOLS/python"
        )
```

## Zero-Copy Pattern

SpareTools uses the NGA aerospace pattern:
- Artifacts live in **ONE** Conan cache location
- Your projects symlink to cache (no copies)
- **80% disk space savings**
- Ultra-fast project setup

## Troubleshooting

### Q: "python command not found"
```bash
# Make sure you sourced activate.sh
source full_deploy/host/sparetools-cpython/3.12.7/*/activate.sh

# Or set PATH manually
export PATH="full_deploy/host/sparetools-cpython/3.12.7/*/bin:$PATH"
```

### Q: "Package not found"
```bash
# Make sure remote is added
conan remote list | grep sparesparrow-conan

# If missing, add it:
conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
```

### Q: "Recipe not found in remote"
```bash
# Try searching for the package
conan search 'sparetools-*' -r sparesparrow-conan

# Verify your Conan version (requires 2.x)
conan --version  # Should be 2.21.0+
```

## Next: OpenSSL

Coming soon:
- `sparetools-openssl/3.4.0` - Prebuilt OpenSSL with FIPS
- `sparetools-conan/2.21.0` - Prebuilt Conan itself

See: https://github.com/sparesparrow/sparetools
