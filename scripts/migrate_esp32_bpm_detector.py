#!/usr/bin/env python3
"""
ESP32 BPM Detector Migration Script

Migrates the standalone esp32-bpm-detector repository to use the SpareTools
consumer package structure following OMS patterns.

This script:
1. Copies application code to consumer package
2. Updates conanfile.txt to reference consumer package
3. Creates migration documentation
"""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_bpm_detector():
    """Migrate esp32-bpm-detector to SpareTools consumer structure."""

    # Paths
    sparetools_root = Path(__file__).parent.parent
    consumer_package = sparetools_root / "packages/consumers/esp32/sparetools-bpm-detector"
    source_repo = Path("../../embedded-systems/esp32-bpm-detector")

    logger.info("🚀 Starting ESP32 BPM Detector migration...")

    # Ensure source exists
    if not source_repo.exists():
        raise FileNotFoundError(f"Source repository not found: {source_repo}")

    # Create consumer package directories
    (consumer_package / "src").mkdir(parents=True, exist_ok=True)
    (consumer_package / "include").mkdir(parents=True, exist_ok=True)
    (consumer_package / "test").mkdir(parents=True, exist_ok=True)
    (consumer_package / "scripts").mkdir(parents=True, exist_ok=True)

    # Copy application source code
    logger.info("📁 Copying application source code...")

    # Copy src/ directory
    if (source_repo / "src").exists():
        for file_path in (source_repo / "src").rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_repo / "src")
                dest_path = consumer_package / "src" / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                logger.info(f"✅ Copied {relative_path}")

    # Copy include/ directory (if it exists)
    if (source_repo / "include").exists():
        for file_path in (source_repo / "include").rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_repo / "include")
                dest_path = consumer_package / "include" / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                logger.info(f"✅ Copied include/{relative_path}")

    # Copy test files
    if (source_repo / "tests").exists():
        for file_path in (source_repo / "tests").rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_repo / "tests")
                dest_path = consumer_package / "test" / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                logger.info(f"✅ Copied test/{relative_path}")

    # Copy scripts
    if (source_repo / "scripts").exists():
        for file_path in (source_repo / "scripts").rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_repo / "scripts")
                dest_path = consumer_package / "scripts" / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                logger.info(f"✅ Copied scripts/{relative_path}")

    # Copy PlatformIO configuration
    if (source_repo / "platformio.ini").exists():
        shutil.copy2(source_repo / "platformio.ini", consumer_package / "platformio.ini")
        logger.info("✅ Copied platformio.ini")

    # Copy CMakeLists.txt if it exists
    if (source_repo / "CMakeLists.txt").exists():
        shutil.copy2(source_repo / "CMakeLists.txt", consumer_package / "CMakeLists.txt")
        logger.info("✅ Copied CMakeLists.txt")

    # Update the original repository's conanfile.txt to reference the consumer package
    conanfile_path = source_repo / "conanfile.txt"
    if conanfile_path.exists():
        logger.info("📝 Updating conanfile.txt to reference consumer package...")

        new_conanfile_content = """[requires]
sparetools-bpm-detector/0.1.0

[options]
sparetools-bpm-detector/*:with_display=True
sparetools-bpm-detector/*:with_networking=True
sparetools-bpm-detector/*:with_websocket=True
sparetools-bpm-detector/*:with_audio_calibration=True
sparetools-bpm-detector/*:target_board=esp32s3

[generators]
CMakeDeps
"""
        with open(conanfile_path, 'w') as f:
            f.write(new_conanfile_content)

        logger.info("✅ Updated conanfile.txt")

    # Create migration documentation
    migration_doc = consumer_package / "MIGRATION.md"
    with open(migration_doc, 'w') as f:
        f.write("""# ESP32 BPM Detector Migration to SpareTools

## Overview

The ESP32 BPM Detector has been migrated to the SpareTools consumer package structure following OMS repository separation patterns.

## What Changed

### Before (Standalone Repository)
```
esp32-bpm-detector/
├── src/           # Application code
├── include/       # Headers
├── tests/         # Test files
├── scripts/       # Build scripts
├── conanfile.txt  # Direct dependencies
└── platformio.ini # Build configuration
```

### After (Consumer Package Structure)
```
sparetools/packages/consumers/esp32/sparetools-bpm-detector/
├── conanfile.py       # Consumer package definition
├── CMakeLists.txt     # Host testing configuration
├── platformio.ini     # ESP32 build configuration
├── src/              # Application code (migrated)
├── include/          # Headers (migrated)
├── test/             # Test files (migrated)
└── scripts/          # Build scripts (migrated)

esp32-bpm-detector/ (original repo)
└── conanfile.txt     # Now references consumer package
```

## Benefits

1. **Dependency Management**: Uses SpareTools foundation packages
2. **Shared Schemas**: FlatBuffers schemas from sparetools-protocols
3. **CI/CD Integration**: Reusable workflows and templates
4. **Consistency**: Follows OMS patterns across all projects

## Building

### Option 1: Use Consumer Package Directly
```bash
# From SpareTools root
cd packages/consumers/esp32/sparetools-bpm-detector
conan install . --profile=esp32_sunton_v3.prof
platformio run -e esp32-s3
```

### Option 2: Use Original Repository (References Consumer)
```bash
# From esp32-bpm-detector directory
conan install . --profile=esp32_sunton_v3.prof
# This will pull in the consumer package and its dependencies
platformio run -e esp32-s3
```

## Development Workflow

1. **Make Code Changes**: Edit files in consumer package
2. **Run Tests**: Use SpareTools testing infrastructure
3. **Build Firmware**: Use PlatformIO with Conan dependencies
4. **Version Updates**: Update versions in SpareTools central configuration

## Dependencies

- `sparetools-protocols/1.0.1` - FlatBuffers schemas
- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Build tools
""")

    logger.info(f"✅ Created migration documentation: {migration_doc}")

    # Create a README update for the original repository
    original_readme = source_repo / "README.md"
    if original_readme.exists():
        with open(original_readme, 'a') as f:
            f.write("""

## Migration Notice

⚠️ **This repository has been migrated to SpareTools consumer package structure.**

The application code has been moved to:
`dev-tools/sparetools/packages/consumers/esp32/sparetools-bpm-detector/`

This repository now serves as a thin wrapper that references the consumer package.

### Development
Please make code changes in the SpareTools consumer package and use this repository for:
- CI/CD workflows
- Issue tracking
- Release management

### Building
```bash
# This now uses the consumer package
conan install . --profile=esp32_sunton_v3.prof
platformio run -e esp32-s3
```
""")

        logger.info("✅ Updated original repository README")

    logger.info("🎉 ESP32 BPM Detector migration completed!")
    logger.info(f"Consumer package: {consumer_package}")
    logger.info("Original repository updated to reference consumer package")


def main():
    try:
        migrate_bpm_detector()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()