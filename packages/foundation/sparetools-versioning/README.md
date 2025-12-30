# SpareTools Versioning Package

Git-based versioning utilities for Conan packages.

## Features

- **Git-to-Conan Collector**: Automatically build Conan packages from git tags/branches
- **Version Tracking**: Track package usage and prevent duplicate builds
- **Git Handler**: Repository operations for versioning workflows
- **Conan Version Management**: Utilities for package version extraction and sorting

## Usage

### In conanfile.py

```python
from conan import ConanFile
import os

class MyPackageConan(ConanFile):
    name = "my-package"
    # Use CONAN_BUILD_VERSION from environment, fallback to static version
    version = os.environ.get('CONAN_BUILD_VERSION', '1.0.0')
    
    # ... rest of conanfile
```

### Git-to-Conan Collector

```python
from sparetools_versioning.versioning import GitToConanCollector
from sparetools_versioning.versioning.git_to_conan_collector import Options

options = Options()
options.git_path = '/path/to/repo'
options.skipped_names_yaml_file = 'skipped.yaml'
options.conanfile_path = 'conanfile.py'
options.package_name = 'my-package'
options.parse_tags = True
options.remote_name = 'cloudsmith'

collector = GitToConanCollector(options)
collector.run()
```

### Command Line

```bash
python -m sparetools_versioning.versioning.git_to_conan_collector \
    --gitPath /path/to/repo \
    --skippedNamesYaml skipped.yaml \
    --conanfilePath conanfile.py \
    --packageName my-package \
    --Tags \
    --remote cloudsmith
```

## Versioning Rules

1. **Git-based versioning**: Versions are derived from git tags/branches via `CONAN_BUILD_VERSION`
2. **Version format**: `{branch_name}_{timestamp}_{commit_sha}` or raw tag/branch name
3. **Version increment**: Every change to a branch should result in a new version
4. **Version tracking**: YAML skip list prevents reprocessing of already-built versions
5. **Pull request validation**: PRs with same conanfile version should fail or auto-increment

## Dependencies

- `sparetools-base/2.0.3` - Foundation utilities
- `GitPython` - Git operations (optional, falls back to git commands)
- `PyYAML` - YAML file handling (optional)

## Integration

This package should be used as a `python_requires` dependency:

```python
python_requires = "sparetools-versioning/1.0.0"
```
