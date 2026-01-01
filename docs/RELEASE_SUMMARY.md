# Release Summary - January 1, 2026

## 🎉 Releases Created

### 1. mcp-prompts v3.12.6

**Repository**: https://github.com/sparesparrow/mcp-prompts  
**Tag**: `v3.12.6`  
**Status**: ✅ Tagged and pushed

**What's Included**:
- ESP32 embedded development prompts (6 atomic prompts)
- Self-improving learning loop implementation
- Meta-workflow for ESP32 full bringup
- Knowledge reusability mapping
- GitHub Packages publishing workflow

**Publishing** (via GitHub Actions):
- ✅ npm: `@sparesparrow/mcp-prompts@3.12.6`
- ✅ GitHub Packages: `@sparesparrow/mcp-prompts@3.12.6`
- ✅ Cloudsmith: `mcp-prompts@3.12.6`
- ✅ Docker: `ghcr.io/sparesparrow/mcp-prompts:3.12.6`

**Workflow**: `.github/workflows/release.yml`

### 2. sparetools v2.0.4

**Repository**: https://github.com/sparesparrow/sparetools  
**Tag**: `v2.0.4`  
**Status**: ✅ Tagged and pushed

**What's Included**:
- MCP prompts integration from GitHub repo
- Cloudsmith artifacts upload workflow
- ESP32 BPM prompts package
- Updated mcp-prompts Conan package (v3.12.6)

**Publishing** (via GitHub Actions):
- ✅ Cloudsmith: All Conan packages
- ✅ Artifacts: Firmware, tools, MCP servers
- ✅ GitHub Release: Automatic on tag push

**Workflow**: `.github/workflows/release.yml` and `.github/workflows/upload-artifacts-to-cloudsmith.yml`

### 3. esp32-bpm-detector v0.1.1

**Repository**: https://github.com/sparesparrow/esp32-bpm-detector  
**Tag**: `v0.1.1`  
**Status**: ✅ Tagged and pushed

**What's Included**:
- Updated conanfile.py with prompts package dependency
- MCP prompts integration
- ESP32 BPM detector firmware

**Publishing**:
- ✅ GitHub Release: Automatic on tag push
- ⏳ Firmware artifacts: Upload via sparetools script

## 📦 Package Availability

### npm
```bash
npm install @sparesparrow/mcp-prompts@3.12.6
```

### GitHub Packages
```bash
npm install @sparesparrow/mcp-prompts@3.12.6 --registry https://npm.pkg.github.com
```

### Cloudsmith
```bash
# Conan packages
conan install sparetools-mcp-prompts/3.12.6@sparesparrow/stable -r sparetools

# Raw artifacts
cloudsmith download raw sparesparrow-conan/sparetools --name "mcp-prompts" --version "3.12.6"
```

### Docker
```bash
docker pull ghcr.io/sparesparrow/mcp-prompts:3.12.6
```

## 🔄 Release Workflows

### mcp-prompts
- **Trigger**: Push tag `v*` or manual workflow dispatch
- **Actions**:
  1. Publish to npm
  2. Publish to GitHub Packages
  3. Upload to Cloudsmith
  4. Build and push Docker image
  5. Create GitHub release

### sparetools
- **Trigger**: Push tag `v*` or manual workflow dispatch
- **Actions**:
  1. Build all Conan packages
  2. Publish to Cloudsmith
  3. Upload artifacts (firmware, tools, MCP servers)
  4. Create GitHub release

### esp32-bpm-detector
- **Trigger**: Push tag `v*`
- **Actions**:
  1. Create GitHub release
  2. (Manual) Upload firmware artifacts via sparetools script

## 📋 Next Steps

### For mcp-prompts
1. ✅ Tag pushed - GitHub Actions will automatically publish
2. Monitor workflow: https://github.com/sparesparrow/mcp-prompts/actions
3. Verify publications:
   - npm: https://www.npmjs.com/package/@sparesparrow/mcp-prompts
   - GitHub Packages: https://github.com/sparesparrow/mcp-prompts/packages
   - Cloudsmith: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/
   - Docker: https://github.com/sparesparrow/mcp-prompts/pkgs/container/mcp-prompts

### For sparetools
1. ✅ Tag pushed - GitHub Actions will automatically build and publish
2. Monitor workflow: https://github.com/sparesparrow/sparetools/actions
3. Verify packages on Cloudsmith

### For esp32-bpm-detector
1. ✅ Tag pushed - GitHub release will be created
2. Build firmware: `pio run --environment esp32-s3-release`
3. Upload artifacts: `cd sparetools && ./scripts/upload_artifacts_to_cloudsmith.sh firmware v0.1.1`

## 🔗 Release Links

- **mcp-prompts v3.12.6**: https://github.com/sparesparrow/mcp-prompts/releases/tag/v3.12.6
- **sparetools v2.0.4**: https://github.com/sparesparrow/sparetools/releases/tag/v2.0.4
- **esp32-bpm-detector v0.1.1**: https://github.com/sparesparrow/esp32-bpm-detector/releases/tag/v0.1.1

## ✅ Status

All releases have been:
- ✅ Version bumped
- ✅ Committed
- ✅ Tagged
- ✅ Pushed to GitHub
- ⏳ Publishing workflows triggered (GitHub Actions)

Monitor the GitHub Actions workflows to confirm successful publication to all platforms.