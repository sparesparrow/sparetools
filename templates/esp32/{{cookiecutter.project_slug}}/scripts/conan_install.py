#!/usr/bin/env python3
"""
PlatformIO pre-build script to install Conan dependencies for {{cookiecutter.project_name}}.

This script runs `conan install` to set up the SpareTools dependencies
before the PlatformIO build process.
"""

import os
import sys
import subprocess
import platform

def run_conan_install():
    """Run conan install to set up dependencies."""

    # Get the project root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change to project directory
    os.chdir(project_dir)

    print("Installing Conan dependencies for {{cookiecutter.project_name}}...")
    print("Using SpareTools ecosystem packages...")

    # Run conan install
    cmd = [
        "conan", "install", ".",
        "--build=missing",
        "--profile", "esp32_base"
    ]

    # Try with profile first, then fallback without profile
    try:
        # Try to find SpareTools profile
        sparetools_profile = os.path.join(os.path.dirname(os.path.dirname(project_dir)),
                                        "dev-tools", "sparetools", "conan_profiles", "esp32_base.prof")

        if os.path.exists(sparetools_profile):
            print(f"Using SpareTools profile: {sparetools_profile}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        else:
            print("SpareTools profile not found, installing without profile...")
            cmd_profile = cmd[:-2] + cmd[-1:]  # Remove profile argument
            result = subprocess.run(cmd_profile, capture_output=True, text=True, check=True)

        print("✅ Conan dependencies installed successfully!")
        if result.stdout:
            print("Conan output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Conan dependencies: {e}")
        if e.stdout:
            print("Conan stdout:", e.stdout)
        if e.stderr:
            print("Conan stderr:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Error: Conan not found. Please install Conan package manager.")
        print("Visit: https://conan.io/downloads.html")
        return False

def main():
    """Main entry point."""
    print("{{cookiecutter.project_name}} - SpareTools Dependency Setup")
    print("=" * 60)

    success = run_conan_install()

    if success:
        print("✅ Dependencies ready for PlatformIO build")
        print("📦 Using SpareTools ecosystem packages:")
        print("   - sparesparrow-protocols/1.0.0")
        {% if cookiecutter.schema_component != 'none' %}
        print("   - Schema component: {{cookiecutter.schema_component}}")
        {% endif %}
        sys.exit(0)
    else:
        print("❌ Failed to install dependencies")
        print("Please check your Conan installation and network connectivity")
        print("For help with SpareTools: https://github.com/sparesparrow/sparetools")
        sys.exit(1)

if __name__ == "__main__":
    main()




