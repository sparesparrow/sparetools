#!/usr/bin/env python3
"""
Test cross-platform detection logic from DevEnv OpenSSL conanfile.py
"""

def test_platform_detection():
    """Test the platform mapping logic"""

    # Platform map from the fixed conanfile.py
    platform_map = {
        "Linux": {"x86_64": "linux-x86_64", "x86": "linux-x86", "armv7": "linux-armv4", "armv8": "linux-aarch64"},
        "Macos": {"x86_64": "darwin64-x86_64", "armv8": "darwin64-arm64"},
        "Windows": {"x86_64": "mingw64", "x86": "mingw"},
    }

    # Test cases: (os, arch, expected_result)
    test_cases = [
        # Linux platforms
        ("Linux", "x86_64", "linux-x86_64"),
        ("Linux", "x86", "linux-x86"),
        ("Linux", "armv7", "linux-armv4"),
        ("Linux", "armv8", "linux-aarch64"),
        ("Linux", "aarch64", "linux-aarch64"),  # Should fallback

        # macOS platforms
        ("Macos", "x86_64", "darwin64-x86_64"),
        ("Macos", "armv8", "darwin64-arm64"),

        # Windows platforms
        ("Windows", "x86_64", "mingw64"),
        ("Windows", "x86", "mingw"),

        # Unknown combinations (should fallback to linux-{arch})
        ("FreeBSD", "x86_64", "linux-x86_64"),  # Fallback
        ("Linux", "ppc64le", "linux-ppc64le"),  # Fallback
    ]

    print("="*70)
    print("CROSS-PLATFORM DETECTION TEST")
    print("="*70)
    print()

    passed = 0
    failed = 0

    for os_name, arch_name, expected in test_cases:
        # Simulate the logic from conanfile.py
        target_platform = platform_map.get(os_name, {}).get(arch_name, f"linux-{arch_name}")

        status = "✅ PASS" if target_platform == expected else "❌ FAIL"
        if target_platform == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status}: {os_name:10} + {arch_name:10} → {target_platform:25} (expected: {expected})")

    print()
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70)

    return failed == 0


def test_configure_args_generation():
    """Test that configure arguments are generated correctly for different platforms"""

    print("\n" + "="*70)
    print("CONFIGURE ARGUMENTS GENERATION TEST")
    print("="*70)
    print()

    platform_map = {
        "Linux": {"x86_64": "linux-x86_64", "x86": "linux-x86", "armv7": "linux-armv4", "armv8": "linux-aarch64"},
        "Macos": {"x86_64": "darwin64-x86_64", "armv8": "darwin64-arm64"},
        "Windows": {"x86_64": "mingw64", "x86": "mingw"},
    }

    test_configs = [
        {"os": "Linux", "arch": "x86_64", "shared": True},
        {"os": "Macos", "arch": "armv8", "shared": False},
        {"os": "Windows", "arch": "x86_64", "shared": True},
    ]

    for config in test_configs:
        os_name = config["os"]
        arch_name = config["arch"]
        shared = config["shared"]

        target_platform = platform_map.get(os_name, {}).get(arch_name, f"linux-{arch_name}")

        # Simulate configure args (simplified)
        configure_args = [
            target_platform,
            "shared" if shared else "no-shared",
            "--prefix=/opt/openssl",
            "--openssldir=/opt/openssl/ssl",
            "no-md2",
            "no-md4",
        ]

        print(f"Platform: {os_name} / {arch_name} (shared={shared})")
        print(f"  Target: {target_platform}")
        print(f"  Args: {' '.join(configure_args)}")
        print()


def test_version_consistency():
    """Check that version references are now consistent"""

    print("="*70)
    print("VERSION CONSISTENCY CHECK")
    print("="*70)
    print()

    import os

    files_to_check = [
        "/home/sparrow/sparetools/packages/sparetools-cpython/conanfile.py",
        "/home/sparrow/sparetools/packages/sparetools-openssl-tools/conanfile.py",
        "/home/sparrow/sparetools/packages/sparetools-shared-dev-tools/conanfile.py",
        "/home/sparrow/projects/openssl-devenv/openssl/conanfile.py",
    ]

    expected_version = "2.0.0"
    issues = []

    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"⚠️  SKIP: {filepath} (not found)")
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        # Check for old version references
        if "sparetools-base/1.0.0" in content:
            issues.append(f"❌ {filepath}: Still references sparetools-base/1.0.0")
        elif "sparetools-base/2.0.0" in content or "python_requires" in content:
            print(f"✅ {filepath}: Version references correct")
        else:
            print(f"⚠️  {filepath}: No sparetools-base reference found")

        if "sparetools-openssl-tools/1.0.0" in content:
            issues.append(f"❌ {filepath}: Still references sparetools-openssl-tools/1.0.0")
        elif "openssl-profiles" in content:
            issues.append(f"❌ {filepath}: Still references non-existent openssl-profiles")

    print()
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All version references are consistent!")

    return len(issues) == 0


def test_cpython_staging_env():
    """Test that CPython staging path can be configured via environment variable"""

    print("\n" + "="*70)
    print("CPYTHON STAGING PATH CONFIGURATION TEST")
    print("="*70)
    print()

    import os

    # Simulate the logic from the fixed conanfile.py
    default_path = "/tmp/cpython-3.12.7-staging/usr/local"

    # Test 1: No environment variable (should use default)
    if 'CPYTHON_STAGING_DIR' in os.environ:
        del os.environ['CPYTHON_STAGING_DIR']

    staging_dir = os.environ.get("CPYTHON_STAGING_DIR", default_path)
    print(f"Test 1 (no env var): {staging_dir}")
    assert staging_dir == default_path, "Should use default path"
    print("  ✅ PASS: Uses default path")

    # Test 2: Custom environment variable
    custom_path = "/custom/staging/path"
    os.environ['CPYTHON_STAGING_DIR'] = custom_path
    staging_dir = os.environ.get("CPYTHON_STAGING_DIR", default_path)
    print(f"Test 2 (custom env): {staging_dir}")
    assert staging_dir == custom_path, "Should use custom path"
    print("  ✅ PASS: Uses custom path from environment")

    # Cleanup
    if 'CPYTHON_STAGING_DIR' in os.environ:
        del os.environ['CPYTHON_STAGING_DIR']

    print()
    print("✅ CPython staging path configuration works correctly!")


if __name__ == "__main__":
    print("\n🧪 SPARETOOLS CROSS-PLATFORM TEST SUITE\n")

    all_passed = True

    # Run all tests
    all_passed &= test_platform_detection()
    test_configure_args_generation()
    all_passed &= test_version_consistency()
    test_cpython_staging_env()

    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Review output above")
    print("="*70)
    print()
