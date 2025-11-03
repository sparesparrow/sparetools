#!/usr/bin/env python3
"""
Enhanced Package Creation Script
Creates and validates all OpenSSL modular packages following best practices
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_conan_command(cmd, cwd=None):
    """Run a Conan command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {cmd}")
            return True
        else:
            print(f"❌ {cmd}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {cmd}")
        print(f"Exception: {e}")
        return False


def create_package(package_path, package_name, build=True):
    """Create a specific package"""
    print(f"\n📦 Creating package: {package_name}")
    print("=" * 50)

    # Change to package directory
    os.chdir(package_path)

    # Clean previous builds
    run_conan_command("conan cache clean --source")

    # Install dependencies
    if not run_conan_command("conan install . --build=missing"):
        return False

    # Create package
    if build:
        success = run_conan_command("conan create . --build=missing")
    else:
        success = run_conan_command("conan export .")

    return success


def validate_package_dependencies():
    """Validate that all packages have correct dependencies"""
    print("\n🔍 Validating package dependencies...")
    print("=" * 50)

    packages = [
        ("openssl-conan-base", "Foundation package", True),
        ("openssl-fips-policy", "FIPS policy package", True),

        # Original modular packages
        ("openssl-tools/conanfile-testing.py", "Testing tools", False),
        ("openssl-tools/conanfile-security.py", "Security tools", False),
        ("openssl-tools/conanfile-automation.py", "Automation tools", False),
        ("openssl-tools/conanfile-validation.py", "Validation tools", False),

        # OpenSSL 3.5.2 enhanced packages
        ("openssl-tools/conanfile-providers.py", "Provider management tools", False),
        ("openssl-tools/conanfile-optimization.py", "Build optimization tools", False),
        ("openssl-tools/conanfile-monitoring.py", "Monitoring and observability tools", False),
        ("openssl-tools/conanfile-compliance.py", "Compliance and standards tools", False),

        # NEW specialized packages
        ("openssl-tools/conanfile-benchmarking.py", "Performance benchmarking tools", False),
        ("openssl-tools/conanfile-migration.py", "Migration and upgrade tools", False),
        ("openssl-tools/conanfile-containerization.py", "Containerization and deployment tools", False),
        ("openssl-tools/conanfile-cross-compilation.py", "Cross-compilation tools", False),
        ("openssl-tools/conanfile-development.py", "Development productivity tools", False),
        ("openssl-tools/conanfile-release-management.py", "Release management tools", False),
        ("openssl-tools/conanfile-security-audit.py", "Security audit tools", False),
        ("openssl-tools/conanfile-integration.py", "Third-party integration tools", False),

        # Advanced enterprise packages
        ("openssl-tools/conanfile-documentation.py", "Documentation generation tools", False),
        ("openssl-tools/conanfile-hardware-acceleration.py", "Hardware acceleration tools", False),
        ("openssl-tools/conanfile-cloud-integration.py", "Cloud integration tools", False),
        ("openssl-tools/conanfile-mobile-development.py", "Mobile development tools", False),
        ("openssl-tools/conanfile-embedded-systems.py", "Embedded systems tools", False),
        ("openssl-tools/conanfile-legacy-compatibility.py", "Legacy compatibility tools", False),
        ("openssl-tools/conanfile-enterprise-integration.py", "Enterprise integration tools", False),
        ("openssl-tools/conanfile-high-availability.py", "High availability tools", False),
        ("openssl-tools/conanfile-analytics-reporting.py", "Analytics and reporting tools", False),
        ("openssl-tools/conanfile-openssl-3.5.2-complete.py", "OpenSSL 3.5.2 complete package", False),

        # Meta-package (requires all components)
        ("openssl-tools", "Complete meta-package (26 components)", True),

        # Main OpenSSL 3.5.2 package
        ("openssl", "Main OpenSSL 3.5.2 package", True),
    ]

    all_success = True
    for package_path, description, build in packages:
        print(f"\n📋 Testing {description}...")

        if package_path.startswith("openssl-tools/"):
            # Handle sub-conanfiles in tools
            package_path = package_path.replace("openssl-tools/", "")
            full_path = f"openssl-tools/{package_path}"
        else:
            full_path = package_path

        if not create_package(full_path, description, build):
            all_success = False

    return all_success


def test_package_integration():
    """Test that packages work together correctly"""
    print("\n🔗 Testing package integration...")
    print("=" * 50)

    # Test foundation package
    if not run_conan_command("conan install openssl-base/1.0.1@sparesparrow/stable"):
        return False

    # Test tools meta-package
    if not run_conan_command("conan install openssl-tools/1.2.0@sparesparrow/stable"):
        return False

    # Test main package
    if not run_conan_command("conan install openssl/3.3.0@sparesparrow/stable"):
        return False

    # Test with FIPS enabled
    if not run_conan_command("conan install openssl/3.3.0@sparesparrow/stable -o enable_fips=True"):
        return False

    return True


def upload_packages():
    """Upload packages to remote repository"""
    print("\n📤 Uploading packages to remote...")
    print("=" * 50)

    packages = [
        "openssl-base/1.0.1@sparesparrow/stable",
        "openssl-fips-data/140-3.2@sparesparrow/stable",
        "openssl-testing/1.0.0@sparesparrow/stable",
        "openssl-security/1.0.0@sparesparrow/stable",
        "openssl-automation/1.0.0@sparesparrow/stable",
        "openssl-validation/1.0.0@sparesparrow/stable",
        "openssl-tools/1.2.0@sparesparrow/stable",
        "openssl/3.3.0@sparesparrow/stable",
    ]

    all_success = True
    for package in packages:
        if not run_conan_command(f"conan upload {package} -r=sparesparrow-conan"):
            all_success = False

    return all_success


def main():
    parser = argparse.ArgumentParser(description="Create and validate OpenSSL modular packages")
    parser.add_argument("--skip-build", action="store_true", help="Skip building packages (export only)")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to remote")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing packages")
    parser.add_argument("--package", help="Create only specific package")

    args = parser.parse_args()

    print("🚀 Enhanced OpenSSL Package Creation")
    print("=" * 60)

    if args.validate_only:
        # Just validate existing packages
        success = test_package_integration()
        sys.exit(0 if success else 1)

    # Check Conan is available
    if not run_conan_command("conan --version"):
        print("❌ Conan is not available. Please install Conan 2.x")
        sys.exit(1)

    # Create individual packages
    if args.package:
        # Create only specific package
        success = create_package(args.package, args.package, not args.skip_build)
    else:
        # Create all packages
        success = validate_package_dependencies()

        if success and not args.skip_build:
            success = test_package_integration()

    # Upload if successful and not skipped
    if success and not args.skip_upload:
        upload_packages()

    print("\n" + "=" * 60)
    if success:
        print("✅ All packages created successfully!")
        print("\n📋 Available packages:")
        run_conan_command("conan list '*' --format=table")
    else:
        print("❌ Some packages failed to create")
        sys.exit(1)


if __name__ == "__main__":
    main()
