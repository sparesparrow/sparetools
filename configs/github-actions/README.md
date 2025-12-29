# SpareTools Shared CI/CD Workflows

This directory contains reusable GitHub Actions workflows that can be called from consumer repositories. These workflows provide consistent CI/CD across the SpareTools ecosystem.

## Available Workflows

### ESP32 Build (`esp32-build-reusable.yml`)

Reusable workflow for building ESP32 firmware projects with SpareTools integration.

**Inputs:**
- `conan_packages`: Comma-separated list of Conan packages (default: `sparesparrow-protocols/1.0.0,sparetools-embedded/1.0.0`)
- `board_type`: ESP32 board type (default: `esp32dev`)
- `environment`: PlatformIO environment name (default: `esp32dev`)
- `run_tests`: Whether to run unit tests (default: `true`)

**Secrets:**
- `CLOUDSMITH_API_KEY`: Optional, for accessing private packages

**Usage in consumer repository:**
```yaml
# .github/workflows/build.yml
name: ESP32 Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    uses: sparesparrow/sparetools/.github/workflows/esp32-build-reusable.yml@main
    with:
      conan_packages: "sparesparrow-protocols/1.0.0,sparetools-embedded/1.0.0"
      board_type: "esp32-s3-devkitc-1"
      environment: "esp32-s3-devkitc-1"
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### Android Build (`android-build-reusable.yml`)

Reusable workflow for building Android applications with SpareTools integration.

**Inputs:**
- `conan_packages`: Comma-separated list of Conan packages
- `android_api_level`: Android API level (default: `28`)
- `build_tools_version`: Android build tools version (default: `30.0.3`)
- `run_tests`: Whether to run unit tests (default: `true`)

**Usage:**
```yaml
# .github/workflows/android-build.yml
name: Android Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    uses: sparesparrow/sparetools/.github/workflows/android-build-reusable.yml@main
    with:
      conan_packages: "sparesparrow-protocols/1.0.0,sparetools-embedded/1.0.0"
      android_api_level: "29"
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### Conan Package Publishing (`conan-publish-reusable.yml`)

Reusable workflow for publishing Conan packages to Cloudsmith.

**Inputs:**
- `package_path`: Path to package directory (required)
- `package_name`: Package name (required)
- `package_version`: Package version (required)
- `remote_name`: Conan remote name (default: `sparesparrow-conan`)
- `dry_run`: Perform dry run only (default: `false`)

**Secrets:**
- `CLOUDSMITH_API_KEY`: Required for publishing

**Usage:**
```yaml
# .github/workflows/publish.yml
name: Publish Package

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    uses: sparesparrow/sparetools/.github/workflows/conan-publish-reusable.yml@main
    with:
      package_path: "packages/my-package"
      package_name: "my-package"
      package_version: "1.0.0"
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

## Setup Requirements

### Consumer Repository Setup

1. **Create workflow directory:**
   ```bash
   mkdir -p .github/workflows
   ```

2. **Add workflow files** as shown in the examples above.

3. **Set up secrets** in repository settings:
   - Go to Settings → Secrets and variables → Actions
   - Add `CLOUDSMITH_API_KEY` if accessing private packages

### Conan Remote Configuration

The workflows automatically configure these Conan remotes:
- `conancenter`: Official ConanCenter packages
- `sparesparrow-conan`: SpareTools Cloudsmith repository

## Caching Strategy

The workflows implement intelligent caching:

- **PlatformIO dependencies**: Cached by `platformio.ini` hash
- **Conan packages**: Cached by dependency file hashes
- **Gradle dependencies**: Cached by Gradle file hashes

## Error Handling

- **Automatic retries** for transient failures
- **Detailed logging** for debugging
- **Artifact uploads** for build and test results
- **Conditional execution** based on success/failure

## Integration with SpareTools Templates

These workflows are designed to work seamlessly with:

- **ESP32 Cookiecutter template**: Pre-configured PlatformIO setup
- **Android template**: Pre-configured Gradle setup
- **Conan packages**: Automatic dependency resolution

## Troubleshooting

### Common Issues

**Conan remote authentication fails:**
- Ensure `CLOUDSMITH_API_KEY` secret is set
- Check that the API key has publish permissions

**PlatformIO build fails:**
- Verify `platformio.ini` configuration
- Check that Conan packages are available

**Android build fails:**
- Ensure correct API level and build tools version
- Verify Gradle wrapper permissions

### Debugging

Enable debug logging by adding to workflow:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Enable debug logging
        run: echo "ACTIONS_RUNNER_DEBUG=true" >> $GITHUB_ENV
```

## Contributing

When adding new workflows:

1. Follow naming convention: `{type}-reusable.yml`
2. Include comprehensive input documentation
3. Add usage examples
4. Test with consumer repositories
5. Update this documentation

## Support

- **Workflow Issues**: [SpareTools Issues](https://github.com/sparesparrow/sparetools/issues)
- **Documentation**: [SpareTools Wiki](https://github.com/sparesparrow/sparetools/wiki)
- **Conan**: [Conan Documentation](https://docs.conan.io/)



