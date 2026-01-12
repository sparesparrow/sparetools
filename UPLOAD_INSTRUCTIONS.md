# Package Upload Instructions

## Current Status

✅ **Packages Built and Ready for Upload:**

### Foundation Packages
- `sparetools-recipe-base/2.0.3`
- `sparetools-base/2.0.3`
- `sparetools-cpython/3.12.7` ⚠️ (see note below)
- `sparetools-test-harness/2.0.3`
- `sparetools-shared-dev-tools/2.0.3`
- `sparetools-bootstrap/2.0.3`

### Embedded Packages
- `sparetools-hal-sunton/1.0.0`
- `sparetools-embedded/1.0.0`

### Schema Packages
- `sparetools-protocols/1.0.1`

### Consumer Packages
- `sparetools-obd-sim/2.0.3`
- `sparetools-cliphist-android/1.0.0`
- `sparetools-openssl/3.3.2`
- `sparetools-openssl-tools/2.0.0`
- `sparetools-mia/2.0.0`
- `sparetools-mcp-orchestrator/2.0.3`
- `sparetools-tinymcp/2.0.0`
- `sparetools-mcpserver-cpp/2.0.0`
- `sparetools-bpm-detector/0.1.0`
- `sparetools-nucleus/0.1.0`

## About sparetools-cpython

**Current Package**: `sparetools-cpython/3.12.7`

**Options**:
1. **Keep current name** - Custom build with OpenSSL support
2. **Use standard package** - Use `cpython/3.12.7` from ConanCenter instead
3. **Rename package** - Change to just `cpython` (would require updating all dependencies)

**Recommendation**: Keep `sparetools-cpython` as it provides:
- Custom OpenSSL integration
- Cloudsmith CLI bundled
- Zero-copy architecture
- SpareTools-specific optimizations

If you prefer using standard `cpython/3.12.7` from ConanCenter:
```bash
# Update dependencies to use:
# cpython/3.12.7@  (from ConanCenter)
# Instead of:
# sparetools-cpython/3.12.7
```

## Upload to Cloudsmith

### Prerequisites
```bash
export CLOUDSMITH_API_KEY=your_api_key
```

### Upload Command
```bash
cd dev-tools/sparetools
./upload_all_packages.sh --cloudsmith-only
```

Or manually:
```bash
# Authenticate
conan remote login sparesparrow-conan sparesparrow --password "$CLOUDSMITH_API_KEY"

# Upload packages
conan upload "sparetools-*/*" -r sparesparrow-conan --confirm
conan upload "sparetools-protocols/*" -r sparesparrow-conan --confirm
```

## Upload to GitHub Packages

### Prerequisites
```bash
export GITHUB_TOKEN=your_github_token
```

### Upload Command
```bash
cd dev-tools/sparetools
./upload_all_packages.sh --github-only
```

Or manually:
```bash
# Authenticate
conan remote login github-packages <username> --password "$GITHUB_TOKEN"

# Upload packages
conan upload "sparetools-*/*" -r github-packages --confirm
conan upload "sparetools-protocols/*" -r github-packages --confirm
```

## Upload to Both

```bash
cd dev-tools/sparetools
./upload_all_packages.sh
```

## Verification

### Check Cloudsmith
```bash
conan search "sparetools-*" -r sparesparrow-conan
```

### Check GitHub Packages
```bash
conan search "sparetools-*" -r github-packages
```

## Package Count

Total packages ready for upload: **22 packages**

- Foundation: 6 packages
- Embedded: 2 packages  
- Schemas: 1 package
- Consumers: 13 packages