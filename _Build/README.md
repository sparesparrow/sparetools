# _Build Directory - Zero-Copy Build Artifacts

This directory contains build artifacts, test results, and symlinks to Conan cache packages following the **zero-copy deployment pattern**.

## 🎯 Purpose

The `_Build` directory centralizes all build-related outputs while leveraging symlinks to avoid duplicating binaries that already exist in the Conan cache (`~/.conan2/`).

## 📂 Structure

```
_Build/
├── openssl-builds/          # OpenSSL build artifacts
│   ├── master/
│   │   ├── vanilla/         # Perl Configure builds
│   │   └── python/          # Python configure.py builds
│   ├── 3.6.0/
│   │   ├── vanilla/
│   │   └── python/
│   ├── orchestration/       # Build orchestration scripts
│   └── logs/                # Build logs
├── conan-cache -> ~/.conan2 # Symlink to Conan cache (zero-copy)
├── packages/                # Symlinks to built packages (zero-copy)
│   ├── sparetools-base -> ~/.conan2/p/.../sparetools-base/p
│   ├── sparetools-cpython -> ~/.conan2/p/.../sparetools-cpython/p
│   ├── sparetools-openssl-tools -> ~/.conan2/p/.../sparetools-openssl-tools/p
│   └── sparetools-openssl -> ~/.conan2/p/.../sparetools-openssl/p
└── README.md (this file)
```

## 🔗 Zero-Copy Symlink Strategy

### Principles

1. **Single Source of Truth**: All built packages live in `~/.conan2/p/` (Conan cache)
2. **No Duplication**: Binaries are accessed via symlinks, not copied
3. **Atomic Updates**: Package upgrades = symlink retargeting
4. **Disk Savings**: 80%+ reduction in disk usage

### Creating Package Symlinks

```bash
# Setup script to create symlinks to Conan packages
cd /home/sparrow/sparetools/_Build

# Create packages directory
mkdir -p packages

# Find latest packages in Conan cache
CONAN_CACHE="$HOME/.conan2"

# Create symlinks to package folders
for pkg in sparetools-base sparetools-cpython sparetools-openssl-tools sparetools-openssl; do
    pkg_path=$(find "$CONAN_CACHE/p" -maxdepth 1 -type d -name "${pkg}*" | sort -V | tail -1)
    if [ -n "$pkg_path" ]; then
        ln -sfn "$pkg_path/p" "packages/$pkg"
        echo "✓ Linked packages/$pkg -> $pkg_path/p"
    fi
done

# Create symlink to Conan cache root
ln -sfn "$CONAN_CACHE" conan-cache
echo "✓ Linked conan-cache -> $CONAN_CACHE"
```

### Verification

```bash
# Check symlinks
ls -la _Build/packages/

# Verify zero duplication
du -sh ~/.conan2/p/b/sparetool*/p/     # Actual disk usage
du -sh _Build/packages/sparetools-*     # Should be tiny (links only)

# Test access
_Build/packages/sparetools-cpython/bin/python3 --version
_Build/packages/sparetools-openssl/bin/openssl version
```

## 📦 OpenSSL Builds

### Build Artifacts Structure

```
openssl-builds/
├── master/               # OpenSSL master branch
│   ├── vanilla/
│   │   ├── install/      # Installation prefix
│   │   │   ├── bin/      # OpenSSL CLI
│   │   │   ├── include/  # Headers
│   │   │   └── lib64/    # Libraries
│   │   └── src/          # Source (git submodule)
│   └── python/
│       └── src/          # Source for Python builds
├── 3.6.0/                # OpenSSL 3.6.0 release
│   ├── vanilla/
│   └── python/
├── orchestration/
│   ├── build_with_python.sh
│   └── validate-builds.sh
└── logs/
    ├── master-vanilla-build.log
    ├── master-python-build.log
    ├── 3.6.0-vanilla-build.log
    └── 3.6.0-python-build.log
```

### Build Methods

1. **Vanilla (Perl Configure)**: Production-ready, stable
   - Status: ✅ Works perfectly
   - Used for: Production deployments

2. **Python (configure.py)**: Experimental orchestration
   - Status: ⚠️ OpenSSL 3.6.0+ source issues
   - Used for: Testing, development

## 🔧 Usage

### Access Built OpenSSL

```bash
# Via direct path
/home/sparrow/sparetools/_Build/openssl-builds/3.6.0/vanilla/install/bin/openssl version

# Via symlink to Conan package (when packaged)
/home/sparrow/sparetools/_Build/packages/sparetools-openssl/bin/openssl version
```

### Rebuild from Source

```bash
cd /home/sparrow/sparetools/_Build/openssl-builds/orchestration
./build_with_python.sh 3.6.0   # Build with Python configure.py
```

### Validate Builds

```bash
cd /home/sparrow/sparetools/_Build/openssl-builds/orchestration
./validate-builds.sh
```

## 📊 Disk Usage Comparison

| Approach | Disk Usage | Example |
|----------|-----------|---------|
| **Traditional (copy)** | ~500MB | Copy each package to workspace |
| **Zero-Copy (symlink)** | ~50KB | Symlinks only, binaries in cache |
| **Savings** | **99%** | 450MB saved per workspace |

## 🚀 Integration with Workflows

### Conan Package Workflow

1. **Build package**: `conan create packages/sparetools-openssl --version=3.3.2`
2. **Locate in cache**: `conan cache path sparetools-openssl/3.3.2`
3. **Create symlink**: `ln -s $(conan cache path sparetools-openssl/3.3.2) _Build/packages/sparetools-openssl`
4. **Use directly**: `_Build/packages/sparetools-openssl/bin/openssl`

### CI/CD Workflow

In CI/CD (GitHub Actions), packages are built and cached. The `_Build` directory can be populated with symlinks for artifact archiving without duplicating large binaries.

```yaml
- name: Archive build artifacts (zero-copy)
  run: |
    mkdir -p _Build/packages
    for pkg in sparetools-*; do
      pkg_path=$(conan cache path "$pkg")
      ln -sfn "$pkg_path" "_Build/packages/$pkg"
    done
    
- uses: actions/upload-artifact@v4
  with:
    name: sparetools-packages
    path: _Build/packages/*
    # Note: Symlinks are followed, only metadata is uploaded
```

## 🛠️ Maintenance

### Refresh Symlinks After Package Updates

```bash
# Script: refresh-build-symlinks.sh
cd /home/sparrow/sparetools/_Build/packages

for pkg in sparetools-*; do
    if [ -L "$pkg" ]; then
        rm "$pkg"
    fi
done

# Re-create symlinks
bash ../create-package-symlinks.sh
```

### Clean Build Artifacts

```bash
# Remove old build artifacts (keeps symlinks)
rm -rf _Build/openssl-builds/*/vanilla/install/*
rm -rf _Build/openssl-builds/*/python/install/*

# Clean logs
rm -f _Build/openssl-builds/logs/*.log
```

## 📝 Notes

- **Symlink Compatibility**: Works on Linux, macOS, WSL. Native Windows requires admin rights or developer mode.
- **Git Submodules**: OpenSSL source directories (`src/`) are git submodules - excluded from main repo via `.gitignore`.
- **Backward Compatibility**: Original `test_results/openssl-builds` is a symlink to `_Build/openssl-builds` for compatibility.

## 📚 References

- **Zero-Copy Pattern**: See `CLAUDE.md` section "Zero-Copy Symlink Strategy"
- **Conan Cache**: https://docs.conan.io/2/reference/commands/cache.html
- **Build Scripts**: `_Build/openssl-builds/orchestration/`
- **Validation Report**: `test_results/validation-report.md`

---

**Last Updated**: 2025-10-31  
**SpareTools Version**: 2.0.0
