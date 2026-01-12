# SpareTools Python Scripts

Runtime Python utility modules for SpareTools projects.

## Overview

This package provides reusable Python utility modules used across the SpareTools ecosystem. It's designed to be used with bundled CPython (`sparetools-cpython`) for build-time scripting in Conan recipes.

## Modules

- **fs**: Filesystem operations (symlinks, zero-copy deployment, directory management)
- **proc**: Process management (command execution, process monitoring)
- **net**: Networking utilities (socket operations, port checking)
- **scm**: Source control management (Git operations, GitHub API)
- **logging**: Structured logging with ANSI color support
- **security**: Security scanning (Trivy, SBOM generation)
- **gui**: GUI utilities (Tkinter helpers, crash observer)
- **util**: Internal utilities (command execution, process helpers)

## Usage

### In Conan Recipes (Build-Time)

```python
from conan import ConanFile

class MyProjectConan(ConanFile):
    def build_requirements(self):
        # Bundled Python interpreter
        self.tool_requires("sparetools-cpython/3.12.8")

        # Runtime utility scripts
        self.tool_requires("sparetools-python-scripts/1.0.0")

    def generate(self):
        # Import utilities (PYTHONPATH set automatically)
        from sparetools.util.execute_command import execute_command
        from sparetools.fs import find_file

        # Find bundled Python
        python_exe = self._get_bundled_python()

        # Run script with bundled Python
        execute_command([python_exe, "my_script.py"])

    def _get_bundled_python(self):
        from pathlib import Path
        for dep in self.dependencies.build.values():
            if "cpython" in dep.ref.name:
                return Path(dep.package_folder) / "bin" / "python3.12"
        raise RuntimeError("Bundled cpython not found")
```

### Module Examples

**Filesystem Operations:**
```python
from sparetools.fs import create_zero_copy_environment, ensure_directory_exists

create_zero_copy_environment(source_dir, target_dir)
ensure_directory_exists(my_dir)
```

**Command Execution:**
```python
from sparetools.util.execute_command import execute_command

exit_code, output = execute_command(
    ["python", "script.py", "arg1"],
    print_command=True
)
```

**Git Operations:**
```python
from sparetools.scm.git import GitHandler

git = GitHandler("/path/to/repo")
git.update_submodules()
branches = git.get_remote_branches()
```

## Package Info

- **Type**: `application` (Conan package type)
- **Version**: 1.0.0
- **License**: Apache-2.0
- **Dependencies**: None (optional dependencies gracefully degraded)

## PYTHONPATH

This package automatically sets PYTHONPATH in both:
- `buildenv_info`: For use in generate(), build() methods
- `runenv_info`: For runtime execution with bundled Python

## Companion Packages

Use this package alongside:
- **sparetools-base**: Recipe helpers (SpareToolsSecurityMixin, SpareToolsVersions)
- **sparetools-cpython**: Bundled CPython interpreter for build-time scripting

## Migration from sparetools-base

If you previously used `sparetools-base` for runtime imports, update your conanfile:

```python
# OLD (sparetools-base/2.0.3)
python_requires = "sparetools-base/2.0.3"
# Runtime imports didn't work reliably

# NEW (split architecture)
python_requires = "sparetools-base/2.0.4"  # Recipe helpers only
python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

def build_requirements(self):
    self.tool_requires("sparetools-cpython/3.12.8")
    self.tool_requires("sparetools-python-scripts/1.0.0")  # Runtime imports
```

## Development

To test locally:
```bash
cd packages/foundation/sparetools-python-scripts
conan create . --version=1.0.0
```

## Support

For issues or questions, please contact the SpareTools team.
