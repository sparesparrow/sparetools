# SpareTools Package Build and Upload Guide

## Overview

This guide explains how to build all SpareTools packages and upload them to Cloudsmith and GitHub Packages.

## Prerequisites

### Required Tools
- **Conan 2.21.0+**: Package manager
  ```bash
  pip install conan==2.21.0
  ```

- **Python 3.12+**: For build scripts

### Required Credentials

#### Cloudsmith
1. Create account at https://cloudsmith.io
2. Create a repository: `sparesparrow-conan/openssl-conan`
3. Generate API key from Cloudsmith dashboard
4. Set environment variable:
   ```bash
   export CLOUDSMITH_API_KEY=your_cloudsmith_api_key
   ```

#### GitHub Packages
1. Generate a Personal Access Token (PAT) with `write:packages` permission
2. Set environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

   Or in GitHub Actions, use `${{ secrets.GITHUB_TOKEN }}`

## Building Packages

### Option 1: Build All Packages (Recommended)

```bash
cd dev-tools/sparetools
./create_all_packages.sh
```

This will build all packages in dependency order:
- Foundation packages (recipe-base, base, cpython, test-harness, shared-dev-tools, bootstrap)
- Embedded packages (hal-sunton, embedded)
- Schema packages (sparetools-protocols)
- Consumer packages (obd-sim, mia, mcp packages, esp32 packages)

**Note**: `sparetools-cpython` can take 5-30 minutes to build as it compiles Python from source.

### Option 2: Build Using Python Script

```bash
cd dev-tools/sparetools
python3 scripts/build_and_upload_packages.py
```

This provides more detailed logging and error handling.

### Option 3: Build Individual Packages

```bash
cd dev-tools/sparetools/packages/foundation/sparetools-base
conan create . --user sparetools --channel stable --build=missing
```

## Uploading Packages

### Upload to Cloudsmith

1. **Authenticate**:
   ```bash
   conan remote login sparesparrow-conan sparesparrow --password "$CLOUDSMITH_API_KEY"
   ```

2. **Upload packages**:
   ```bash
   conan upload "sparetools-*/*" -r sparesparrow-conan --confirm
   conan upload "sparetools-protocols/*" -r sparesparrow-conan --confirm
   ```

### Upload to GitHub Packages

1. **Authenticate**:
   ```bash
   conan remote login github-packages <username> --password "$GITHUB_TOKEN"
   ```

2. **Upload packages**:
   ```bash
   conan upload "sparetools-*/*" -r github-packages --confirm
   conan upload "sparetools-protocols/*" -r github-packages --confirm
   ```

### Automated Upload (All-in-One)

```bash
cd dev-tools/sparetools
./build_and_upload_all.sh
```

Or using Python script:
```bash
python3 scripts/build_and_upload_packages.py
```

## Package List

### Foundation Packages
- `sparetools-recipe-base/2.0.3` - Base recipe classes
- `sparetools-base/2.0.3` - Core utilities
- `sparetools-cpython/3.12.7` - Python environment (takes 5-30 min)
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Development tools
- `sparetools-bootstrap/2.0.0` - Bootstrap scripts

### Embedded Packages
- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer
- `sparetools-embedded/1.0.0` - Embedded utilities

### Schema Packages
- `sparetools-protocols/1.0.1` - FlatBuffers schemas

### Consumer Packages
- `sparetools-obd-sim/2.0.3` - OBD-II simulator
- `sparetools-cliphist-android/1.0.0` - Android clipboard history
- `sparetools-openssl/3.3.2` - OpenSSL integration
- `sparetools-openssl-tools/2.0.0` - OpenSSL tools
- `sparetools-mia/2.0.0` - MIA IoT platform
- `sparetools-mcp-orchestrator/2.0.3` - MCP orchestrator
- `sparetools-tinymcp/2.0.0` - TinyMCP integration
- `sparetools-mcpserver-cpp/2.0.0` - MCP C++ server
- `sparetools-bpm-detector/0.1.0` - ESP32 BPM detector
- `sparetools-nucleus/0.1.0` - NucleusESP32 firmware

## Verification

### List Built Packages
```bash
conan list "sparetools-*"
conan list "sparetools-protocols/*"
```

### Verify Upload to Cloudsmith
```bash
conan search "sparetools-*" -r sparesparrow-conan
```

### Verify Upload to GitHub Packages
```bash
conan search "sparetools-*" -r github-packages
```

## Installation from Remotes

### From Cloudsmith
```bash
# Add remote
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force

# Install package
conan install --requires=sparetools-base/2.0.3 -r sparesparrow-conan
```

### From GitHub Packages
```bash
# Add remote
conan remote add github-packages \
  https://maven.pkg.github.com/sparesparrow/sparetools \
  --force

# Authenticate
conan remote login github-packages <username> --password <token>

# Install package
conan install --requires=sparetools-base/2.0.3 -r github-packages
```

## Troubleshooting

### Build Failures
- Check that all dependencies are available
- Ensure Conan profile is correctly configured: `conan profile detect --force`
- Check build logs in `build_upload.log`

### Upload Failures
- Verify credentials are set: `echo $CLOUDSMITH_API_KEY` and `echo $GITHUB_TOKEN`
- Check remote configuration: `conan remote list`
- Verify authentication: `conan remote list-users`

### Long Build Times
- `sparetools-cpython` takes 5-30 minutes (compiles Python from source)
- Other packages typically build in seconds to minutes
- Use `--build=missing` to only build missing packages

## Scripts Available

1. **`create_all_packages.sh`**: Simple bash script to build all packages
2. **`build_and_upload_all.sh`**: Comprehensive bash script for build + upload
3. **`scripts/build_and_upload_packages.py`**: Python script with better error handling

## Next Steps

After packages are built and uploaded:

1. **Test Installation**: Install packages from remotes to verify
2. **Update Documentation**: Update README files with new versions
3. **Create Release**: Tag the repository with version number
4. **Announce**: Notify users of new package versions

## Support

For issues or questions:
- Check build logs: `build_upload.log`
- Review upload reports: `BUILD_UPLOAD_REPORT.json`
- Check Conan cache: `conan cache path <package-name>/<version>`