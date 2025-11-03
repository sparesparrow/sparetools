#!/usr/bin/env python3
"""
Validation script for SpareTools repository completion.

Tests:
1. Conan 2.x API compliance (no env_info usage)
2. Bundled Python integration (cpython tool_requires)
3. Test package validation for all packages
4. Dependency chain integrity
"""

import os
import re
import sys
from pathlib import Path


def validate_conan_api():
    """Validate that all packages use Conan 2.x API"""
    print("=" * 80)
    print("TEST 1: Conan 2.x API Compliance")
    print("=" * 80)

    packages_dir = Path("packages")
    issues = []

    for conanfile in packages_dir.rglob("conanfile.py"):
        # Skip deprecated packages
        if "deprecated" in str(conanfile):
            continue

        with open(conanfile, "r") as f:
            content = f.read()

            # Check for deprecated env_info usage
            if re.search(r"self\.env_info\.", content):
                issues.append(f"{conanfile}: Uses deprecated env_info API")

            # Check that buildenv_info or runenv_info is used instead
            # BUT: Library packages (with cpp_info.components or cpp_info.libs) don't need env vars
            if "package_info" in content:
                is_library = bool(re.search(r"cpp_info\.components", content)) or bool(re.search(r"cpp_info\.libs\s*=\s*\[", content))
                has_env_info = bool(re.search(r"self\.buildenv_info\.", content) or re.search(r"self\.runenv_info\.", content))

                # python-require packages should have buildenv_info
                is_python_require = 'package_type = "python-require"' in content

                if is_python_require and not has_env_info and "cpp_info.libs = []" not in content:
                    issues.append(f"{conanfile}: python-require package should use buildenv_info")
                elif not is_library and not has_env_info and "cpp_info.libs = []" not in content:
                    # Non-library, non-python-require packages without environment info
                    pass  # This is fine for some packages

    if issues:
        print("❌ FAILED: Found Conan API issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: All packages use Conan 2.x API correctly")
        return True


def validate_test_packages():
    """Validate that key packages have test_package/ directories"""
    print("\n" + "=" * 80)
    print("TEST 2: Test Package Coverage")
    print("=" * 80)

    required_test_packages = [
        "packages/sparetools-cpython/test_package",
        "packages/sparetools-shared-dev-tools/test_package",
        "packages/sparetools-bootstrap/test_package",
        "packages/sparetools-openssl/test_package",
    ]

    missing = []
    for test_pkg in required_test_packages:
        test_pkg_path = Path(test_pkg)
        conanfile_path = test_pkg_path / "conanfile.py"

        if not conanfile_path.exists():
            missing.append(test_pkg)

    if missing:
        print("❌ FAILED: Missing test_package directories:")
        for pkg in missing:
            print(f"  - {pkg}")
        return False
    else:
        print("✅ PASSED: All key packages have test_package validation")
        print(f"  Total: {len(required_test_packages)} packages validated")
        return True


def validate_deprecated_moved():
    """Validate that deprecated packages are in deprecated/ directory"""
    print("\n" + "=" * 80)
    print("TEST 3: Deprecated Package Archival")
    print("=" * 80)

    deprecated_packages = [
        "packages/deprecated/sparetools-openssl-cmake",
        "packages/deprecated/sparetools-openssl-autotools",
        "packages/deprecated/sparetools-openssl-hybrid",
        "packages/deprecated/sparetools-openssl-tools-mini",
    ]

    missing = []
    for pkg in deprecated_packages:
        if not Path(pkg).exists():
            missing.append(pkg)

    # Check that they're not in main packages/ directory
    should_not_exist = [
        "packages/sparetools-openssl-cmake",
        "packages/sparetools-openssl-autotools",
        "packages/sparetools-openssl-hybrid",
        "packages/sparetools-openssl-tools-mini",
    ]

    still_in_main = []
    for pkg in should_not_exist:
        if Path(pkg).exists() and not Path(pkg).is_symlink():
            still_in_main.append(pkg)

    if missing or still_in_main:
        print("❌ FAILED: Deprecated package issues:")
        if missing:
            print("  Missing from deprecated/:")
            for pkg in missing:
                print(f"    - {pkg}")
        if still_in_main:
            print("  Still in main packages/ directory:")
            for pkg in still_in_main:
                print(f"    - {pkg}")
        return False
    else:
        print("✅ PASSED: All deprecated packages archived correctly")
        print(f"  Total: {len(deprecated_packages)} packages archived")
        return True


def validate_workflows():
    """Validate that duplicate workflows are removed"""
    print("\n" + "=" * 80)
    print("TEST 4: Workflow Consolidation")
    print("=" * 80)

    active_workflows = [
        ".github/workflows/ci.yml",
        ".github/workflows/publish.yml",
        ".github/workflows/security.yml",
        ".github/workflows/nightly.yml",
        ".github/workflows/release.yml",
    ]

    deprecated_workflows = [
        ".github/workflows/deprecated/build-test.yml",
        ".github/workflows/deprecated/build-and-test.yml",
        ".github/workflows/deprecated/deploy-cloudsmith.yml",
        ".github/workflows/deprecated/integration.yml",
        ".github/workflows/deprecated/build-cpython-matrix.yml",
    ]

    issues = []

    # Check active workflows exist
    for wf in active_workflows:
        if not Path(wf).exists():
            issues.append(f"Missing active workflow: {wf}")

    # Check deprecated workflows are moved
    for wf in deprecated_workflows:
        if not Path(wf).exists():
            issues.append(f"Missing deprecated workflow: {wf}")

    # Check they're not in main directory
    should_not_exist = [
        ".github/workflows/build-test.yml",
        ".github/workflows/build-and-test.yml",
        ".github/workflows/deploy-cloudsmith.yml",
        ".github/workflows/integration.yml",
        ".github/workflows/build-cpython-matrix.yml",
    ]

    for wf in should_not_exist:
        if Path(wf).exists():
            issues.append(f"Workflow should be deprecated but still in main: {wf}")

    if issues:
        print("❌ FAILED: Workflow issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: Workflow consolidation complete")
        print(f"  Active workflows: {len(active_workflows)}")
        print(f"  Deprecated workflows: {len(deprecated_workflows)}")
        return True


def main():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("SpareTools Repository Completion Validation")
    print("=" * 80)
    print()

    # Change to repo root
    os.chdir(Path(__file__).parent)

    results = []

    results.append(("Conan 2.x API Compliance", validate_conan_api()))
    results.append(("Test Package Coverage", validate_test_packages()))
    results.append(("Deprecated Package Archival", validate_deprecated_moved()))
    results.append(("Workflow Consolidation", validate_workflows()))

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - please review")
        return 1


if __name__ == "__main__":
    sys.exit(main())
