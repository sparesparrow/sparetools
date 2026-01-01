# Cloudsmith Artifacts Upload Guide

This guide explains how to upload reusable artifacts to Cloudsmith, including firmware binaries, development tools, MCP servers, and built dependencies.

## Overview

The SpareTools project uploads various reusable artifacts to Cloudsmith for easy distribution:

- **Firmware Binaries**: Pre-built ESP32 firmware (.bin, .elf files)
- **Development Tools**: Standalone executables (flatc, conan)
- **MCP Servers**: Pre-packaged MCP server executables
- **Dependencies**: Pre-built Conan packages

## Repository

- **Organization**: `sparesparrow-conan`
- **Repository**: `sparetools`
- **URL**: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/

## Authentication

### Get API Key

1. Go to https://cloudsmith.io/user/settings/api-key/
2. Create a new API key with appropriate permissions
3. Copy the API key

### Set Environment Variable

```bash
export CLOUDSMITH_API_KEY=your_api_key_here
```

## Upload Methods

### 1. GitHub Actions (Automatic)

The workflow `.github/workflows/upload-artifacts-to-cloudsmith.yml` automatically uploads artifacts when:

- A tag is pushed (e.g., `git push origin v1.0.0`)
- Manually triggered via GitHub Actions UI

**Manual Trigger:**
1. Go to Actions → "Upload Artifacts to Cloudsmith"
2. Click "Run workflow"
3. Select artifact type: `all`, `firmware`, `tools`, `mcp-servers`, or `dependencies`
4. Optionally specify version
5. Run workflow

### 2. Local Script (Manual)

Use the upload script for local testing or manual uploads:

```bash
cd /path/to/sparetools

# Upload all artifacts
./scripts/upload_artifacts_to_cloudsmith.sh all

# Upload specific artifact type
./scripts/upload_artifacts_to_cloudsmith.sh firmware
./scripts/upload_artifacts_to_cloudsmith.sh tools
./scripts/upload_artifacts_to_cloudsmith.sh mcp-servers
./scripts/upload_artifacts_to_cloudsmith.sh dependencies

# Specify version
./scripts/upload_artifacts_to_cloudsmith.sh all v1.0.0
```

## Artifact Types

### Firmware Binaries

**Location**: `embedded-systems/esp32-bpm-detector/.pio/build/`

**Artifacts Uploaded**:
- `esp32-bpm-detector-esp32s3-{version}.bin` - ESP32-S3 firmware
- `esp32-bpm-detector-esp32s3-bootloader-{version}.bin` - Bootloader
- `esp32-bpm-detector-esp32s3-partitions-{version}.bin` - Partition table
- `esp32-bpm-detector-esp32s3-{version}.elf` - ELF debug file
- `esp32-bpm-detector-esp32-{version}.bin` - ESP32 firmware
- Similar files for ESP32 variant

**Prerequisites**:
- Build firmware first: `cd esp32-bpm-detector && pio run --environment esp32-s3-release`

**Download**:
```bash
# Using Cloudsmith CLI
cloudsmith download raw sparesparrow-conan/sparetools \
  --name "esp32-bpm-detector-esp32s3-1.0.0.bin" \
  --output firmware.bin
```

### Development Tools

#### FlatBuffers Compiler (flatc)

**Version**: 24.3.25

**Upload**:
- Standalone `flatc` executable

**Download**:
```bash
cloudsmith download raw sparesparrow-conan/sparetools \
  --name "flatc" \
  --version "24.3.25" \
  --output flatc
chmod +x flatc
```

#### Conan Package Manager

**Version**: 2.21.0 (or latest)

**Upload**:
- Standalone Conan distribution as tar.gz

**Download**:
```bash
cloudsmith download raw sparesparrow-conan/sparetools \
  --name "conan-standalone" \
  --version "2.21.0" \
  --output conan-standalone.tar.gz

tar -xzf conan-standalone.tar.gz
./conan-standalone/conan-wrapper.sh --version
```

### MCP Servers

#### MCP Prompts Server

**Upload**:
- Standalone Node.js server package
- Includes all dependencies and launcher script

**Download**:
```bash
cloudsmith download raw sparesparrow-conan/sparetools \
  --name "mcp-prompts-server" \
  --version "3.12.5" \
  --output mcp-prompts-server.tar.gz

tar -xzf mcp-prompts-server.tar.gz
cd mcp-prompts-server
npm install  # If needed
./mcp-prompts-server.sh
```

#### Python MCP Servers

**Available Servers**:
- `esp32-serial-monitor-mcp-server` - ESP32 serial monitoring
- `conan-cloudsmith-mcp-server` - Conan package management
- `android-dev-tools-mcp-server` - Android development tools

**Download**:
```bash
cloudsmith download raw sparesparrow-conan/sparetools \
  --name "esp32-serial-monitor-mcp-server" \
  --version "1.0.0" \
  --output esp32-serial-monitor.tar.gz

tar -xzf esp32-serial-monitor.tar.gz
cd esp32_serial_monitor
pip install -r requirements.txt
python esp32_serial_monitor_mcp_server.py
```

### Dependencies

**Pre-built Conan Packages**:
- `sparetools-flatbuffers/24.3.26`
- `sparetools-cpython/3.12.8`
- Other foundation packages

**Install via Conan**:
```bash
conan remote add sparetools \
  https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/conan/

conan install sparetools-flatbuffers/24.3.26@sparesparrow/stable \
  -r sparetools
```

## Workflow Integration

### CI/CD Pipeline

The upload workflow is integrated into the release process:

1. **Build Phase**: Artifacts are built
2. **Test Phase**: Artifacts are validated
3. **Upload Phase**: Artifacts are uploaded to Cloudsmith
4. **Release Phase**: GitHub release is created with download links

### Versioning

- **Firmware**: Uses git tag version (e.g., `v1.0.0`)
- **Tools**: Uses tool-specific versions (e.g., `24.3.25` for flatc)
- **MCP Servers**: Uses git tag or specified version
- **Dependencies**: Uses Conan package versions

## Troubleshooting

### Authentication Failed

```bash
# Verify API key
echo $CLOUDSMITH_API_KEY

# Test authentication
cloudsmith whoami
```

### Artifact Not Found

- Check artifact name and version
- Verify artifact was uploaded: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/
- Check upload logs in GitHub Actions

### Build Artifacts Missing

- Ensure build completed successfully
- Check build output directories exist
- Verify PlatformIO build for firmware: `.pio/build/`

### Upload Fails

- Check Cloudsmith API quota
- Verify repository permissions
- Check artifact size limits (Cloudsmith has limits)
- Review error messages in logs

## Best Practices

1. **Version Everything**: Always specify versions for artifacts
2. **Test Downloads**: Verify artifacts can be downloaded after upload
3. **Document Artifacts**: Update documentation when adding new artifacts
4. **Tag Releases**: Use git tags to trigger automatic uploads
5. **Clean Up**: Remove old/unused artifacts periodically

## Related Documentation

- [Cloudsmith Documentation](https://help.cloudsmith.io/)
- [Conan Package Publishing](../PACKAGE_BUILD_AND_UPLOAD_GUIDE.md)
- [GitHub Actions Workflows](../.github/workflows/README.md)