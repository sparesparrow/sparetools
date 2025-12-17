#!/usr/bin/env python3
"""
Android Consumer Validation Script

Validates the ClipHist Android consumer package for:
- Android SDK/NDK requirements
- Gradle configuration
- Dependencies
- Security requirements
- Build configuration
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class AndroidConsumerValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dir = project_root / "app"
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating ClipHist Android Consumer...")

        checks = [
            self._check_android_structure,
            self._check_gradle_files,
            self._check_manifest,
            self._check_dependencies,
            self._check_security_config,
            self._check_build_config,
            self._check_native_code,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"Validation check failed: {e}")

        self._report_results()
        return len(self.errors) == 0

    def _check_android_structure(self):
        """Check Android project structure."""
        required_dirs = [
            "app/src/main/java/com/sparesparrow/cliphist",
            "app/src/main/res",
            "app/src/main/res/values",
            "app/src/main/res/drawable",
            "app/src/main/res/layout",
            "gradle/wrapper"
        ]

        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                self.errors.append(f"Missing required directory: {dir_path}")

        required_files = [
            "build.gradle.kts",
            "settings.gradle.kts",
            "gradle.properties",
            "app/build.gradle.kts",
            "app/src/main/AndroidManifest.xml",
            "app/proguard-rules.pro",
            "gradle/wrapper/gradle-wrapper.properties"
        ]

        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.errors.append(f"Missing required file: {file_path}")

    def _check_gradle_files(self):
        """Check Gradle configuration files."""
        # Check root build.gradle.kts
        build_gradle = self.project_root / "build.gradle.kts"
        if build_gradle.exists():
            content = build_gradle.read_text()
            required_plugins = ["com.android.application", "org.jetbrains.kotlin.android"]
            for plugin in required_plugins:
                if plugin not in content:
                    self.errors.append(f"Missing required plugin in root build.gradle.kts: {plugin}")

        # Check app build.gradle.kts
        app_build_gradle = self.app_dir / "build.gradle.kts"
        if app_build_gradle.exists():
            content = app_build_gradle.read_text()
            if "compose" not in content:
                self.warnings.append("Jetpack Compose not detected in app build.gradle.kts")

            if "hilt" not in content:
                self.warnings.append("Hilt not detected in app build.gradle.kts")

            if "room" not in content:
                self.warnings.append("Room not detected in app build.gradle.kts")

    def _check_manifest(self):
        """Check AndroidManifest.xml."""
        manifest = self.app_dir / "src/main/AndroidManifest.xml"
        if manifest.exists():
            content = manifest.read_text()
            required_permissions = ["INTERNET", "ACCESS_NETWORK_STATE"]
            for permission in required_permissions:
                if f"android.permission.{permission}" not in content:
                    self.warnings.append(f"Missing recommended permission: {permission}")

            if "ClipHistApplication" not in content:
                self.errors.append("ClipHistApplication not properly configured in manifest")

            if "MainActivity" not in content:
                self.errors.append("MainActivity not properly configured in manifest")

    def _check_dependencies(self):
        """Check critical dependencies."""
        app_build_gradle = self.app_dir / "build.gradle.kts"
        if app_build_gradle.exists():
            content = app_build_gradle.read_text()

            critical_deps = [
                "androidx.core:core-ktx",
                "androidx.compose",
                "androidx.room",
                "com.google.dagger:hilt-android",
                "net.zetetic:android-database-sqlcipher"
            ]

            for dep in critical_deps:
                if dep not in content:
                    self.errors.append(f"Missing critical dependency: {dep}")

    def _check_security_config(self):
        """Check security-related configuration."""
        manifest = self.app_dir / "src/main/AndroidManifest.xml"
        if manifest.exists():
            content = manifest.read_text()
            if 'android:allowBackup="true"' in content:
                self.warnings.append("Backup is enabled - ensure sensitive data is properly encrypted")

        # Check for SQLCipher usage
        app_build_gradle = self.app_dir / "build.gradle.kts"
        if app_build_gradle.exists():
            content = app_build_gradle.read_text()
            if "sqlcipher" not in content:
                self.errors.append("SQLCipher dependency not found - encryption requirement not met")

    def _check_build_config(self):
        """Check build configuration."""
        app_build_gradle = self.app_dir / "build.gradle.kts"
        if app_build_gradle.exists():
            content = app_build_gradle.read_text()

            # Check SDK versions
            if "minSdk = 21" not in content:
                self.errors.append("Minimum SDK should be 21 for broader compatibility")

            if "targetSdk = 34" not in content:
                self.warnings.append("Target SDK should be 34 for latest features")

            if "compileSdk = 34" not in content:
                self.warnings.append("Compile SDK should be 34")

    def _check_native_code(self):
        """Check native code configuration."""
        cmake_lists = self.project_root / "CMakeLists.txt"
        if cmake_lists.exists():
            content = cmake_lists.read_text()
            if "sqlcipher" not in content:
                self.warnings.append("SQLCipher not configured in CMakeLists.txt")

        native_lib = self.project_root / "src/main/cpp/native-lib.cpp"
        if native_lib.exists():
            content = native_lib.read_text()
            if "encryptData" not in content:
                self.warnings.append("Native encryption functions not implemented")

    def _report_results(self):
        """Report validation results."""
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")


def main():
    """Main validation entry point."""
    project_root = Path(__file__).parent
    validator = AndroidConsumerValidator(project_root)

    if validator.validate():
        print("\n🎉 ClipHist Android consumer validation successful!")
        return 0
    else:
        print("\n💥 ClipHist Android consumer validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())