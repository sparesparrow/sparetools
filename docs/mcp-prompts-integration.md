# MCP Prompts Integration with SpareTools

## Overview

This document describes how `mcp-prompts` prompts are versioned, published, and integrated into the SpareTools ecosystem for use in projects like `esp32-bpm-detector`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  mcp-prompts GitHub Repo                                    │
│  (https://github.com/sparesparrow/mcp-prompts)              │
│                                                              │
│  - Source of truth for all prompts                          │
│  - Versioned with git tags (v3.12.5)                        │
│  - Published to GitHub Packages                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Published as npm package
                   │ @sparesparrow/mcp-prompts@3.12.5
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  GitHub Packages                                             │
│  (npm.pkg.github.com/@sparesparrow/mcp-prompts)            │
│                                                              │
│  - npm package with prompts data                            │
│  - Accessible via npm install                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Fetched via git clone in Conan
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  SpareTools Conan Packages                                   │
│                                                              │
│  1. sparetools-mcp-prompts/3.12.6                           │
│     - Full MCP prompts server                                │
│     - Fetches from GitHub repo                               │
│     - Includes all prompts + server                         │
│                                                              │
│  2. sparetools-esp32-bpm-prompts/1.0.0                      │
│     - Aggregated ESP32-specific prompts                     │
│     - Curated for esp32-bpm-detector                        │
│     - Includes:                                              │
│       * ESP32 development prompts (7)                       │
│       * Embedded system prompts (5)                          │
│       * MCP development prompts (1)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Required in conanfile.py
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  esp32-bpm-detector Project                                  │
│                                                              │
│  conanfile.py:                                               │
│    requires = [                                              │
│      "sparetools-esp32-bpm-prompts/1.0.0",                  │
│      ...                                                     │
│    ]                                                         │
│                                                              │
│  Prompts available via:                                     │
│  - $SPARETOOLS_ESP32_BPM_PROMPTS_DIR                        │
│  - $MCP_PROMPTS_PATH                                        │
└─────────────────────────────────────────────────────────────┘
```

## Versioning Strategy

### mcp-prompts GitHub Repo
- **Version**: Semantic versioning (e.g., 3.12.5)
- **Git Tag**: `v3.12.5` (matches package.json version)
- **GitHub Packages**: `@sparesparrow/mcp-prompts@3.12.5`

### SpareTools Conan Packages
- **sparetools-mcp-prompts**: Version matches source (3.12.5) or patch increment (3.12.6)
- **sparetools-esp32-bpm-prompts**: Independent versioning (1.0.0, increments when prompts change)

## Publishing Workflow

### 1. Update Prompts in mcp-prompts Repo

```bash
cd /path/to/mcp-prompts
# Make changes to prompts
git add data/prompts/
git commit -m "feat: Add new ESP32 prompts"
git push origin main
```

### 2. Version and Tag

```bash
# Bump version
npm version patch  # or minor, major

# Create and push tag
git tag v$(node -p "require('./package.json').version")
git push origin --tags
```

### 3. Publish to GitHub Packages

**Option A: Via GitHub Actions (Automatic)**
- Push tag triggers `.github/workflows/publish-github-packages.yml`
- Automatically publishes to GitHub Packages

**Option B: Manual Publishing**
```bash
export GITHUB_TOKEN=your_token
./scripts/publish-to-github-packages.sh
```

### 4. Update SpareTools Packages

```bash
cd /path/to/sparetools

# Update sparetools-mcp-prompts version
# Edit: packages/mcp/sparetools-mcp-prompts/conanfile.py
# Update version to match mcp-prompts tag

# Build and test
conan create packages/mcp/sparetools-mcp-prompts --build=missing

# Publish to Cloudsmith
conan upload sparetools-mcp-prompts/3.12.6@sparesparrow/stable -r sparetools --all
```

## Package Structure

### sparetools-mcp-prompts
```
sparetools-mcp-prompts/
├── conanfile.py          # Fetches from GitHub, packages server
├── app/                   # MCP prompts server application
│   ├── package.json
│   ├── dist/             # Compiled TypeScript
│   └── src/              # TypeScript source
├── data/                   # Prompts data
│   └── prompts/          # All prompts from mcp-prompts repo
├── scripts/               # Utility scripts
└── bin/                   # Launcher scripts
    ├── sparetools-mcp-prompts
    ├── sparetools-mcp-prompts-http
    └── sparetools-mcp-prompts-cli
```

### sparetools-esp32-bpm-prompts
```
sparetools-esp32-bpm-prompts/
├── conanfile.py          # Aggregates ESP32-specific prompts
├── prompts/              # Curated prompts
│   ├── esp32/           # ESP32 development prompts
│   ├── embedded/        # Embedded system prompts
│   ├── mcp-development/ # MCP development prompts
│   └── index.json       # Aggregated index
└── README.md
```

## Usage in Projects

### esp32-bpm-detector

```python
# conanfile.py
requires = [
    "sparetools-esp32-bpm-prompts/1.0.0",
    # ... other dependencies
]
```

After `conan install`:
- Prompts available at: `$SPARETOOLS_ESP32_BPM_PROMPTS_DIR`
- Index file: `$SPARETOOLS_ESP32_BPM_PROMPTS_INDEX`
- MCP path: `$MCP_PROMPTS_PATH`

### MCP Server Configuration

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "mcp-prompts",
      "args": ["start", "--mode", "mcp"],
      "env": {
        "PROMPTS_DIR": "${SPARETOOLS_ESP32_BPM_PROMPTS_DIR}",
        "STORAGE_TYPE": "file"
      }
    }
  }
}
```

## Available Prompts

### ESP32 Development (7 prompts)
1. `esp32-network-ap-mode-configuration` - WiFi AP setup
2. `esp32-platformio-serial-upload-debugging` - Build/upload troubleshooting
3. `esp32-flatbuffers-schema-sync-workflow` - Schema regeneration
4. `esp32-mcp-server-http-api-integration` - HTTP API setup
5. `embedded-esp32-full-bringup-workflow` - Complete setup workflow
6. `esp32-fft-configuration-guide` - FFT optimization guide
7. `esp32-fft-optimization-methodology` - Advanced FFT tuning

### Embedded Systems (5 prompts)
1. `embedded-audio-fft-memory-constraints` - Memory optimization
2. `embedded-device-detection` - Device identification
3. `embedded-firmware-deployment` - Firmware deployment
4. `embedded-jtag-workflow` - JTAG debugging
5. `embedded-serial-debugging` - Serial communication

### MCP Development (1 prompt)
1. `mcp-server-file-storage-index-sync` - Index synchronization

## CI/CD Integration

### GitHub Actions (mcp-prompts)
- **Trigger**: Push tag `v*`
- **Action**: Build and publish to GitHub Packages
- **Workflow**: `.github/workflows/publish-github-packages.yml`

### SpareTools CI/CD
- **Trigger**: Changes to `packages/mcp/sparetools-mcp-prompts/`
- **Action**: Build Conan package, test, publish to Cloudsmith
- **Workflow**: `.github/workflows/publish.yml`

## Troubleshooting

### Prompts Not Found
```bash
# Check environment variables
echo $SPARETOOLS_ESP32_BPM_PROMPTS_DIR
echo $MCP_PROMPTS_PATH

# Verify package installation
conan search sparetools-esp32-bpm-prompts -r sparetools
```

### Version Mismatch
```bash
# Check mcp-prompts version
cd /path/to/mcp-prompts
git describe --tags

# Check Conan package version
conan inspect packages/mcp/sparetools-mcp-prompts/conanfile.py
```

### GitHub Packages Access
```bash
# Configure npm for GitHub Packages
echo "@sparesparrow:registry=https://npm.pkg.github.com" >> .npmrc
echo "//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}" >> .npmrc

# Install from GitHub Packages
npm install @sparesparrow/mcp-prompts@3.12.5
```

## Related Documentation

- [mcp-prompts README](https://github.com/sparesparrow/mcp-prompts)
- [SpareTools MCP Integration](../mcp/README.md)
- [ESP32 BPM Detector](../consumers/esp32/sparetools-bpm-detector/README.md)