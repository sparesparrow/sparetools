#!/usr/bin/env python3
"""
NucleusESP32 Migration Script

Migrates the standalone nucleus-esp32 repository to use the SpareTools
consumer package structure following OMS patterns.

This script:
1. Copies application code to consumer package (if needed)
2. Updates conanfile.py to reference consumer package
3. Creates migration documentation
"""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_nucleus_esp32():
    """Migrate nucleus-esp32 to SpareTools consumer structure."""

    # Paths
    sparetools_root = Path(__file__).parent.parent
    consumer_package = sparetools_root / "packages/consumers/esp32/sparetools-nucleus"
    source_repo = Path("../../embedded-systems/nucleus-esp32")

    logger.info("🚀 Starting NucleusESP32 migration...")

    # Ensure source exists
    if not source_repo.exists():
        raise FileNotFoundError(f"Source repository not found: {source_repo}")

    # Check if consumer package already has code
    if not (consumer_package / "src").exists() or not list((consumer_package / "src").glob("*")):
        logger.info("📁 Consumer package appears empty, copying application source code...")

        # Create consumer package directories
        (consumer_package / "src").mkdir(parents=True, exist_ok=True)
        (consumer_package / "include").mkdir(parents=True, exist_ok=True)
        (consumer_package / "test").mkdir(parents=True, exist_ok=True)
        (consumer_package / "test_harness").mkdir(parents=True, exist_ok=True)

        # Copy application source code
        if (source_repo / "src").exists():
            for file_path in (source_repo / "src").rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_repo / "src")
                    dest_path = consumer_package / "src" / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"✅ Copied {relative_path}")

        # Copy include/ directory
        if (source_repo / "include").exists():
            for file_path in (source_repo / "include").rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_repo / "include")
                    dest_path = consumer_package / "include" / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"✅ Copied include/{relative_path}")

        # Copy test files
        if (source_repo / "test").exists():
            for file_path in (source_repo / "test").rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_repo / "test")
                    dest_path = consumer_package / "test" / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"✅ Copied test/{relative_path}")

        # Copy test_harness files
        if (source_repo / "test_harness").exists():
            for file_path in (source_repo / "test_harness").rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_repo / "test_harness")
                    dest_path = consumer_package / "test_harness" / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"✅ Copied test_harness/{relative_path}")

        # Copy PlatformIO configuration
        if (source_repo / "platformio.ini").exists():
            shutil.copy2(source_repo / "platformio.ini", consumer_package / "platformio.ini")
            logger.info("✅ Copied platformio.ini")

        # Copy CMakeLists.txt if it exists
        if (source_repo / "CMakeLists.txt").exists():
            shutil.copy2(source_repo / "CMakeLists.txt", consumer_package / "CMakeLists.txt")
            logger.info("✅ Copied CMakeLists.txt")

    else:
        logger.info("📁 Consumer package already contains source code, skipping copy")

    # Update the original repository's conanfile.py to reference the consumer package
    conanfile_path = source_repo / "conanfile.py"
    if conanfile_path.exists():
        logger.info("📝 Updating conanfile.py to reference consumer package...")

        new_conanfile_content = '''from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
import os


class NucleusESP32Conan(ConanFile):
    """NucleusESP32 Conan package - references SpareTools consumer implementation."""

    name = "nucleus-esp32"
    version = "0.1.0"
    package_type = "application"

    # Reference SpareTools consumer package
    python_requires = "sparetools-base/2.0.3"

    license = "MIT"
    author = "NucleusESP32 Team"
    url = "https://github.com/sparesparrow/NucleusESP32"
    description = "ESP32-based multi-tool device firmware (SpareTools consumer)"
    topics = ("esp32", "embedded", "rf", "nfc", "iot", "sparetools", "consumer")

    settings = "os", "compiler", "build_type", "arch"

    # Options for NucleusESP32-specific features
    options = {
        "with_display": [True, False],
        "with_crypto": [True, False],
        "with_secure_boot": [True, False],
        "target_board": ["esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6"],
    }
    default_options = {
        "with_display": True,
        "with_crypto": True,
        "with_secure_boot": False,
        "target_board": "esp32s3",
    }

    def layout(self):
        basic_layout(self)

    def requirements(self):
        """Reference the SpareTools consumer package."""
        self.requires("sparetools-nucleus/0.1.0")

        # Configure consumer options based on our options
        self.options["sparetools-nucleus"].with_display = self.options.with_display
        self.options["sparetools-nucleus"].with_crypto = self.options.with_crypto
        self.options["sparetools-nucleus"].with_secure_boot = self.options.with_secure_boot
        self.options["sparetools-nucleus"].target_board = self.options.target_board

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = []
'''
        with open(conanfile_path, 'w') as f:
            f.write(new_conanfile_content)

        logger.info("✅ Updated conanfile.py")

    # Create migration documentation
    migration_doc = consumer_package / "MIGRATION.md"
    if not migration_doc.exists():
        with open(migration_doc, 'w') as f:
            f.write("""# NucleusESP32 Migration to SpareTools

## Overview

The NucleusESP32 repository has been migrated to the SpareTools consumer package structure following OMS repository separation patterns.

## What Changed

### Before (Standalone Repository)
```
nucleus-esp32/
├── src/           # Application code
├── include/       # Headers
├── test/          # Test files
├── test_harness/  # Test utilities
├── conanfile.py   # Direct dependencies
└── platformio.ini # Build configuration
```

### After (Consumer Package Structure)
```
sparetools/packages/consumers/esp32/sparetools-nucleus/
├── conanfile.py       # Consumer package definition
├── CMakeLists.txt     # Host testing configuration
├── platformio.ini     # ESP32 build configuration
├── src/              # Application code (migrated)
├── include/          # Headers (migrated)
├── test/             # Test files (migrated)
└── test_harness/     # Test utilities (migrated)

nucleus-esp32/ (original repo)
└── conanfile.py      # Now references consumer package
```

## Benefits

1. **Dependency Management**: Uses SpareTools foundation packages
2. **Shared Components**: Hardware abstraction layers, crypto suites
3. **CI/CD Integration**: Reusable workflows and templates
4. **Consistency**: Follows OMS patterns across all projects

## Building

### Option 1: Use Consumer Package Directly
```bash
# From SpareTools root
cd packages/consumers/esp32/sparetools-nucleus
conan install . --profile=esp32_sunton_v3.prof
platformio run -e esp32s3
```

### Option 2: Use Original Repository (References Consumer)
```bash
# From nucleus-esp32 directory
conan install . --profile=esp32_sunton_v3.prof
# This will pull in the consumer package and its dependencies
platformio run -e esp32s3
```

## Development Workflow

1. **Make Code Changes**: Edit files in consumer package
2. **Run Tests**: Use SpareTools testing infrastructure
3. **Build Firmware**: Use PlatformIO with Conan dependencies
4. **Version Updates**: Update versions in SpareTools central configuration

## Dependencies

- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer
- `sparetools-crypto-suite/1.0.0` - Cryptography components
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Build tools
""")

        logger.info(f"✅ Created migration documentation: {migration_doc}")

    # Update the original repository's README
    original_readme = source_repo / "README.md"
    if original_readme.exists():
        with open(original_readme, 'a') as f:
            f.write("""

## Migration Notice

⚠️ **This repository has been migrated to SpareTools consumer package structure.**

The application code has been moved to:
`dev-tools/sparetools/packages/consumers/esp32/sparetools-nucleus/`

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
platformio run -e esp32s3
```
""")

        logger.info("✅ Updated original repository README")

    logger.info("🎉 NucleusESP32 migration completed!")
    logger.info(f"Consumer package: {consumer_package}")
    logger.info("Original repository updated to reference consumer package")


def main():
    try:
        migrate_nucleus_esp32()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()