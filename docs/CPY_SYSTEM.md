# SpareTools CPY (Copy-on-demand) System

The CPY system provides zero-copy development environments for consumer projects by maintaining a central `~/CPY/` directory with symlinks to SpareTools packages in the Conan cache. Consumer projects create symlinks from their `_Build/SOURCE/EXTERNAL_DEPENDENCIES/` directory to the central CPY location, following the OMS project pattern.

## Overview

Traditional dependency management versions external packages (e.g., `sparetools-base/2.0.3`), but this creates maintenance overhead and version conflicts. The CPY system instead:

1. Installs packages to the local Conan cache
2. Creates symlinks from consumer project directories to cache packages
3. Consumer projects reference symlinked packages without versioning

## Architecture

```
Conan Cache (.conan2/p/)
├── b/spareXXX/        # sparetools-base/2.0.3
├── b/spareYYY/        # sparetools-embedded/1.0.0
└── ...

Central CPY (~/CPY/packages/)
├── foundation/
│   ├── sparetools-base -> ~/.conan2/p/b/spareXXX/
│   └── sparetools-cpython -> ~/.conan2/p/b/spareYYY/
├── embedded/
│   ├── sparetools-embedded -> ~/.conan2/p/b/spareAAA/
│   └── sparetools-flatbuffers -> ~/.conan2/p/b/spareBBB/
├── mcp/
│   └── sparetools-mcp-core -> ~/.conan2/p/b/spareCCC/
└── consumers/
    ├── sparetools-mia -> ~/.conan2/p/b/spareDDD/
    └── sparetools-bpm -> ~/.conan2/p/b/spareEEE/

Consumer Project _Build/SOURCE/EXTERNAL_DEPENDENCIES/
├── foundation/sparetools-base -> ~/CPY/packages/foundation/sparetools-base
├── embedded/sparetools-embedded -> ~/CPY/packages/embedded/sparetools-embedded
└── consumers/sparetools-mia -> ~/CPY/packages/consumers/sparetools-mia
```

## Setup Process

### 1. Install Packages to Cache

```bash
# Install required SpareTools packages
conan install --requires=sparetools-base/2.0.3 --build=missing
conan install --requires=sparetools-embedded/1.0.0 --build=missing
conan install --tool-requires=sparetools-cpython/3.12.7 --build=missing
```

### 2. Create CPY Directory

```bash
# Create CPY directory in consumer project
mkdir -p ~/projects/consumer/CPY

# Create metadata file
cat > ~/projects/consumer/CPY/.cpy-metadata << EOF
{
  "name": "consumer",
  "packages": {
    "sparetools-base": "$(conan cache path sparetools-base/2.0.3)",
    "sparetools-embedded": "$(conan cache path sparetools-embedded/1.0.0)"
  }
}
EOF
```

### 3. Create Symlinks

```bash
cd ~/projects/consumer/CPY

# Create symlinks to Conan cache
ln -sf $(conan cache path sparetools-base/2.0.3) sparetools-base
ln -sf $(conan cache path sparetools-embedded/1.0.0) sparetools-embedded
ln -sf $(conan cache path sparetools-cpython/3.12.7) sparetools-cpython
```

### 4. Configure Build System

Consumer projects should be configured to use the CPY symlinks rather than versioned Cloudsmith packages. The build system resolves symlinks at build time.

## Current Implementations

### Central CPY Directory
```
~/CPY/packages/
├── foundation/
│   ├── sparetools-base -> ~/.conan2/p/b/spareXXX/
│   ├── sparetools-cpython -> ~/.conan2/p/b/spareYYY/
│   └── sparetools-bootstrap -> ~/.conan2/p/b/spareZZZ/
├── embedded/
│   ├── sparetools-embedded -> ~/.conan2/p/b/spareAAA/
│   ├── sparetools-flatbuffers -> ~/.conan2/p/b/spareBBB/
│   └── sparetools-hal-sunton -> ~/.conan2/p/b/spareCCC/
├── mcp/
│   ├── sparetools-mcp-core -> ~/.conan2/p/b/spareDDD/
│   └── sparetools-mcp-orchestrator -> ~/.conan2/p/b/spareEEE/
└── consumers/
    ├── sparetools-mia -> ~/.conan2/p/b/spareFFF/
    └── sparetools-bpm -> ~/.conan2/p/b/spareGGG/
```

### MIA Project
```
~/projects/mia/_Build/SOURCE/EXTERNAL_DEPENDENCIES/
├── foundation/sparetools-base -> ~/CPY/packages/foundation/sparetools-base
├── embedded/sparetools-embedded -> ~/CPY/packages/embedded/sparetools-embedded
└── consumers/sparetools-mia -> ~/CPY/packages/consumers/sparetools-mia
```

### BPM Project
```
~/projects/bpm/_Build/SOURCE/EXTERNAL_DEPENDENCIES/
├── foundation/sparetools-base -> ~/CPY/packages/foundation/sparetools-base
├── embedded/sparetools-embedded -> ~/CPY/packages/embedded/sparetools-embedded
└── consumers/sparetools-bpm -> ~/CPY/packages/consumers/sparetools-bpm
```

## Benefits

### Zero-Copy Development
- No duplication of package files
- Instant updates when cache packages change
- Reduced disk usage

### Simplified Maintenance
- No version management for internal packages
- Automatic updates from local development
- Consistent environments across developers

### Development Workflow
- Local package changes immediately available
- No need to publish to Cloudsmith for testing
- Isolated development without affecting others

## Usage in Consumer Projects

### Conan Configuration

Consumer `conanfile.py` should reference packages by name only:

```python
class ConsumerConan(ConanFile):
    # Use symlinked packages (resolved at build time)
    python_requires = "sparetools-base"
    requires = "sparetools-embedded"

    # Traditional versioned dependencies still OK
    requires = "flatbuffers/23.5.26"
```

### Build Integration

Build scripts should use the symlinked packages in `_Build/SOURCE/EXTERNAL_DEPENDENCIES/`:

```bash
#!/bin/bash
# Restore CPY symlinks
./restore-cpy-symlinks.sh

# Build with symlinked dependencies
conan build .  # Conan resolves symlinks automatically

# Artifacts appear in _Build/SOURCE/EXTERNAL_DEPENDENCIES/
```

## Maintenance

### Updating Packages

```bash
# Update package in cache
conan install --requires=sparetools-base/2.0.4 --build=missing

# Update symlinks
cd ~/projects/consumer/CPY
rm sparetools-base
ln -sf $(conan cache path sparetools-base/2.0.4) sparetools-base

# Update metadata
vim .cpy-metadata  # Update version references
```

### Cleaning Cache

```bash
# Remove unused packages
conan cache clean --temp

# List cache contents
conan cache list

# Remove specific package
conan cache remove "sparetools-base/2.0.3"
```

## Troubleshooting

### Symlink Issues

```bash
# Check symlink targets
ls -la ~/projects/consumer/CPY/

# Recreate broken symlinks
cd ~/projects/consumer/CPY
ln -sf $(conan cache path sparetools-base/2.0.3) sparetools-base
```

### Cache Corruption

```bash
# Clear and rebuild cache
conan cache clean
conan install --requires=sparetools-base/2.0.3 --build=missing
```

### Permission Issues

```bash
# Fix permissions on cache
chmod -R u+rw ~/.conan2/
```

## Integration with CI/CD

CI/CD pipelines should:
1. Install packages to cache first
2. Create CPY symlinks
3. Use symlinked environment for builds
4. Cache the Conan cache directory between runs

Example GitHub Actions:
```yaml
- name: Setup SpareTools CPY
  run: |
    conan install --requires=sparetools-base/2.0.3 --build=missing
    mkdir -p CPY
    cd CPY
    ln -sf $(conan cache path sparetools-base/2.0.3) sparetools-base
```