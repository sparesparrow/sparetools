#!/usr/bin/env python3
"""
Simple SpareTools Module Test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_module(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False

def main():
    print("=== SpareTools Module Test ===\n")

    modules = [
        "sparetools",
        "sparetools.fs",
        "sparetools.proc",
        "sparetools.net",
        "sparetools.scm.git",
        "sparetools.logging",
        "sparetools.security",
        "sparetools.gui",
        "sparetools.conan",
        "sparetools.conan.repositories",
        "sparetools.conan.config",
    ]

    success_count = 0
    for module in modules:
        if test_module(module):
            success_count += 1

    print(f"\n✅ {success_count}/{len(modules)} modules imported successfully")

    # Test conan specific functionality
    try:
        import sparetools.conan
        print(f"📦 Repository types: {[rt.value for rt in sparetools.conan.RepositoryType]}")
    except Exception as e:
        print(f"❌ Conan test failed: {e}")

if __name__ == "__main__":
    main()