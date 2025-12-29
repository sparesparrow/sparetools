#!/usr/bin/env python3
"""
FlatBuffers Code Generation Script for ESP32 BPM Detector

This script generates C++ code from FlatBuffers schema files
for efficient binary serialization in the ESP32 firmware.

Uses sparetools bundled CPython if available, otherwise falls back to system Python.

Usage:
    # With sparetools bundled CPython (preferred):
    sparetools python scripts/generate_flatbuffers.py
    
    # Or set environment variable:
    export SPARETOOLS_PYTHON=~/.sparetools/bin/python
    python3 scripts/generate_flatbuffers.py
    
    # Or use system Python (fallback):
    python3 scripts/generate_flatbuffers.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def is_sparetools_python():
    """Check if current Python is sparetools bundled CPython"""
    python_exe = sys.executable
    python_path = os.path.dirname(python_exe)
    
    # Check if Python path contains sparetools indicators
    if "sparetools" in python_exe.lower() or "sparetools" in python_path.lower():
        return True
    
    # Check environment variables
    if os.environ.get("SPARETOOLS_PYTHON") or os.environ.get("SPARE_PYTHON"):
        return True
    
    return False

def find_python():
    """Find Python interpreter, preferring sparetools bundled CPython"""
    # Check if already running under sparetools Python
    if is_sparetools_python():
        print(f"Already using sparetools bundled CPython: {sys.executable}")
        return [sys.executable]
    
    # Try sparetools bundled CPython first
    sparetools_paths = [
        # Primary sparetools location (user specified)
        os.path.expanduser("~/sparetools/packages/foundation/sparetools-base/test_env/bin/python"),
        os.path.expanduser("~/sparetools/bin/python"),
        os.path.expanduser("~/sparetools/python"),
        # Other common sparetools locations
        os.path.expanduser("~/.sparetools/bin/python"),
        os.path.expanduser("~/.sparetools/python"),
        "/opt/sparetools/bin/python",
        "/usr/local/sparetools/bin/python",
        # Environment variable override
        os.environ.get("SPARETOOLS_PYTHON"),
        os.environ.get("SPARE_PYTHON"),
    ]
    
    # Try sparetools command first
    try:
        result = subprocess.run(
            ["sparetools", "python", "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            print("Using sparetools bundled CPython (via sparetools command)")
            return ["sparetools", "python"]
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try direct paths
    for path in sparetools_paths:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            print(f"Using sparetools bundled CPython: {path}")
            return [path]
    
    # Fall back to system Python
    python_cmd = sys.executable
    print(f"Using system Python: {python_cmd}")
    print("Note: To use sparetools bundled CPython, set SPARETOOLS_PYTHON env var or run: sparetools python scripts/generate_flatbuffers.py")
    return [python_cmd]

def find_flatc():
    """Find the flatc (FlatBuffers compiler) executable"""
    # Check common installation locations
    possible_paths = [
        "/usr/local/bin/flatc",
        "/usr/bin/flatc",
        "/opt/homebrew/bin/flatc",  # macOS
        "./flatc"  # Local directory
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    # Try to find in PATH
    try:
        result = subprocess.run(["which", "flatc"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    return None

def download_flatc(python_cmd=None):
    """Download and setup flatc if not found"""
    print("flatc not found. Attempting to download...")
    
    if python_cmd is None:
        python_cmd = find_python()

    system = platform.system().lower()
    machine = platform.machine().lower()

    # Determine download URL based on platform
    if system == "linux":
        if "x86_64" in machine or "amd64" in machine:
            url = "https://github.com/google/flatbuffers/releases/latest/download/Linux.flatc.binary.clang++17.zip"
        elif "aarch64" in machine or "arm64" in machine:
            url = "https://github.com/google/flatbuffers/releases/latest/download/Linux.flatc.binary.clang++17.zip"
        else:
            print(f"Unsupported Linux architecture: {machine}")
            return False
    elif system == "darwin":  # macOS
        url = "https://github.com/google/flatbuffers/releases/latest/download/Mac.flatc.binary.zip"
    elif system == "windows":
        url = "https://github.com/google/flatbuffers/releases/latest/download/Windows.flatc.binary.zip"
    else:
        print(f"Unsupported platform: {system}")
        return False

    try:
        # Use sparetools Python if available for downloads
        import urllib.request
        import zipfile
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "flatc.zip")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the flatc binary
            for root, dirs, files in os.walk(temp_dir):
                if "flatc" in files:
                    flatc_path = os.path.join(root, "flatc")
                    # Make executable and copy to local directory
                    os.chmod(flatc_path, 0o755)
                    local_flatc = "./flatc"
                    import shutil
                    shutil.copy2(flatc_path, local_flatc)
                    os.chmod(local_flatc, 0o755)
                    print(f"Downloaded flatc to {local_flatc}")
                    return local_flatc

    except Exception as e:
        print(f"Failed to download flatc: {e}")
        return False

    return False

def generate_cpp_code(schema_file, output_dir, flatc_path):
    """Generate C++ code from FlatBuffers schema"""
    print(f"Generating C++ code from {schema_file}...")

    cmd = [
        flatc_path,
        "--cpp",
        "--gen-object-api",
        "--gen-mutable",
        "--scoped-enums",
        "-o", output_dir,
        schema_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Successfully generated C++ code in {output_dir}")
            return True
        else:
            print(f"❌ Failed to generate code: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running flatc: {e}")
        return False

def main():
    """Main code generation function"""
    # Find and use appropriate Python interpreter
    python_cmd = find_python()
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Schema and output directories
    schema_dir = project_root / "schemas"
    include_dir = project_root / "include"
    src_dir = project_root / "src"

    # Create output directories
    include_dir.mkdir(exist_ok=True)
    src_dir.mkdir(exist_ok=True)

    # Find flatc
    flatc_path = find_flatc()
    if not flatc_path:
        print("flatc not found, attempting to download...")
        flatc_path = download_flatc(python_cmd)
        if not flatc_path:
            print("❌ Could not obtain flatc. Please install FlatBuffers compiler manually.")
            print("Visit: https://google.github.io/flatbuffers/flatbuffers_guide_building.html")
            sys.exit(1)

    print(f"Using flatc: {flatc_path}")

    # Check schema file
    schema_file = schema_dir / "bpm_protocol.fbs"
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)

    # Generate C++ code
    success = generate_cpp_code(str(schema_file), str(include_dir), flatc_path)

    if success:
        # List generated files
        print("\n📁 Generated files:")
        for file in include_dir.glob("*.h"):
            print(f"  Header: {file.name}")
        for file in src_dir.glob("*.cpp"):
            print(f"  Source: {file.name}")

        print("\n✅ FlatBuffers code generation completed successfully!")
        print("\nNext steps:")
        print("1. Add generated headers to your ESP32 project includes")
        print("2. Include flatbuffers library in your PlatformIO project")
        print("3. Implement BPM detector message serialization")
        print("4. Update REST API to support binary FlatBuffers format")
    else:
        print("❌ Code generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()