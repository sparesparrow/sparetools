"""
Build Orchestrator for OpenSSL packages
Coordinates multi-phase build process and CMake integration
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class BuildPhase:
    """Represents a build phase"""
    name: str
    description: str
    required: bool = True


@dataclass
class BuildConfig:
    """Build configuration container"""
    source_dir: Path
    build_dir: Path
    install_dir: Path
    fips_enabled: bool = False
    shared_libs: bool = False
    cross_compiling: bool = False


class BuildOrchestrator:
    """
    Orchestrates the OpenSSL build process across multiple phases

    Phases:
    1. Preparation - Source setup and dependency checks
    2. Configuration - CMake/configure script execution
    3. Build - Compilation and linking
    4. Test - Unit and integration tests
    5. FIPS Validation - FIPS compliance checks
    6. Installation - Package installation and verification
    """

    def __init__(self, config: BuildConfig):
        self.config = config
        self.phases = [
            BuildPhase("preparation", "Source setup and dependency validation"),
            BuildPhase("configuration", "CMake/configure script execution"),
            BuildPhase("build", "Compilation and linking"),
            BuildPhase("test", "Unit and integration tests"),
            BuildPhase("fips_validation", "FIPS compliance validation", required=False),
            BuildPhase("installation", "Package installation and verification"),
        ]

    def execute_build(self) -> bool:
        """
        Execute the complete build process

        Returns:
            True if build successful, False otherwise
        """
        print(f"Starting OpenSSL build in {self.config.build_dir}")

        for phase in self.phases:
            print(f"Executing phase: {phase.name} - {phase.description}")

            try:
                success = getattr(self, f"_execute_{phase.name}_phase")()
                if not success and phase.required:
                    print(f"Required phase {phase.name} failed")
                    return False
                elif not success:
                    print(f"Optional phase {phase.name} failed, continuing")
            except Exception as e:
                if phase.required:
                    print(f"Phase {phase.name} failed with error: {e}")
                    return False
                else:
                    print(f"Optional phase {phase.name} failed with error: {e}, continuing")

        print("Build completed successfully")
        return True

    def _execute_preparation_phase(self) -> bool:
        """Prepare build environment"""
        try:
            # Create build directory
            self.config.build_dir.mkdir(parents=True, exist_ok=True)

            # Validate source directory
            if not self.config.source_dir.exists():
                print(f"Source directory does not exist: {self.config.source_dir}")
                return False

            # Check for required files
            required_files = ["CMakeLists.txt", "configure.py"]
            for file in required_files:
                if not (self.config.source_dir / file).exists():
                    print(f"Required file missing: {file}")
                    return False

            return True
        except Exception as e:
            print(f"Preparation phase failed: {e}")
            return False

    def _execute_configuration_phase(self) -> bool:
        """Execute configuration phase"""
        try:
            # This would typically run CMake or configure scripts
            # For now, just validate the build directory is ready
            cmake_cache = self.config.build_dir / "CMakeCache.txt"
            if cmake_cache.exists():
                print("CMake cache already exists, skipping configuration")
                return True

            # In a real implementation, this would run:
            # cmake -S {source_dir} -B {build_dir} -DCMAKE_INSTALL_PREFIX={install_dir}
            print("Configuration phase completed (stub implementation)")
            return True
        except Exception as e:
            print(f"Configuration phase failed: {e}")
            return False

    def _execute_build_phase(self) -> bool:
        """Execute build phase"""
        try:
            # In a real implementation, this would run:
            # cmake --build {build_dir} --parallel
            print("Build phase completed (stub implementation)")
            return True
        except Exception as e:
            print(f"Build phase failed: {e}")
            return False

    def _execute_test_phase(self) -> bool:
        """Execute test phase"""
        try:
            # In a real implementation, this would run:
            # ctest --test-dir {build_dir}
            print("Test phase completed (stub implementation)")
            return True
        except Exception as e:
            print(f"Test phase failed: {e}")
            return False

    def _execute_fips_validation_phase(self) -> bool:
        """Execute FIPS validation phase"""
        if not self.config.fips_enabled:
            print("FIPS validation skipped (FIPS not enabled)")
            return True

        try:
            # Import FIPS validator
            from .fips_validator import FIPSValidator

            validator = FIPSValidator()
            return validator.validate_build(self.config)
        except Exception as e:
            print(f"FIPS validation failed: {e}")
            return False

    def _execute_installation_phase(self) -> bool:
        """Execute installation phase"""
        try:
            # In a real implementation, this would run:
            # cmake --install {build_dir}
            print("Installation phase completed (stub implementation)")
            return True
        except Exception as e:
            print(f"Installation phase failed: {e}")
            return False

    def get_build_status(self) -> Dict[str, Any]:
        """Get current build status"""
        return {
            "source_dir": str(self.config.source_dir),
            "build_dir": str(self.config.build_dir),
            "install_dir": str(self.config.install_dir),
            "fips_enabled": self.config.fips_enabled,
            "shared_libs": self.config.shared_libs,
            "cross_compiling": self.config.cross_compiling,
            "phases": [phase.name for phase in self.phases]
        }