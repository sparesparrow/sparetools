# SpareTools FS Tools

Filesystem operations and utilities for SpareTools projects.

## Features

- **Symlink Management**: Zero-copy pattern for dependency linking
- **File Operations**: Safe file copying, removal, and metadata retrieval
- **Directory Operations**: Creation, removal, and validation
- **Path Resolution**: Profile path resolution and executable finding
- **Search Utilities**: File pattern matching and existence checking

## Usage

```python
from sparetools_fs_tools import (
    symlink_with_check,
    ensure_directory_exists,
    get_file_metadata,
    find_executable_in_path
)

# Create zero-copy symlink
created = symlink_with_check("/cache/package", "./TOOLS/package")

# Ensure directory exists
dir_path = ensure_directory_exists("./build/artifacts")

# Get file information
metadata = get_file_metadata("config.yml")

# Find executable in PATH
python_path = find_executable_in_path("python3")
```

## Conan Package

```bash
conan install sparetools-fs-tools/1.0.0@
```

## Zero-Copy Pattern

This package implements the NGA aerospace project's zero-copy dependency management pattern:

- Dependencies downloaded once to Conan cache
- Workspaces use OS symlinks pointing to cache
- No intermediate copies during consumption
- Massive disk space savings for large workspaces