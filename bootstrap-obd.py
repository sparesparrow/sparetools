#!/usr/bin/env python3
"""
OBD-II Bootstrap Script

Bootstraps a hermetic CPython 3.12.7 runtime from Conan and launches
the ELM327-emulator for OBD-II simulation.
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

# CONFIGURATION
CPY_VER = "3.12.7"
CPYTHON_PACKAGE = f"sparetools-cpython/{CPY_VER}"
CONAN_REMOTE = "sparesparrow-conan"
INSTALL_DIR = os.path.abspath(".mia/python")
BIN_DIR = os.path.join(INSTALL_DIR, "Scripts" if platform.system() == "Windows" else "bin")
PIP_EXE = os.path.join(BIN_DIR, "pip.exe" if platform.system() == "Windows" else "pip3")
PYTHON_EXE = os.path.join(BIN_DIR, "python.exe" if platform.system() == "Windows" else "python3")
SYS_PLATFORM = platform.system()


def print_status(msg):
    """Print status message."""
    print(f"[BOOTSTRAP] {msg}", flush=True)


def print_error(msg):
    """Print error message."""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def find_conan_executable():
    """Find Conan executable in PATH."""
    conan_exe = shutil.which("conan")
    if conan_exe:
        return conan_exe
    
    # Try common locations
    common_paths = [
        os.path.expanduser("~/.local/bin/conan"),
        "/usr/local/bin/conan",
        "/usr/bin/conan",
    ]
    
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def install_cpython_via_conan():
    """Install CPython via Conan."""
    conan_exe = find_conan_executable()
    if not conan_exe:
        print_error("Conan not found in PATH")
        print_error("Please install Conan: pip install conan==2.21.0")
        return False
    
    print_status(f"Using Conan: {conan_exe}")
    
    # Check if package is already built
    list_cmd = [conan_exe, "list", f"{CPYTHON_PACKAGE}:*"]
    result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
    
    has_package = False
    if result.returncode == 0:
        # Check if there's a built package (has package_id)
        output = result.stdout
        if "packages" in output and "da39a3ee5e6b4b0d3255bfef95601890afd80709" not in output:
            # Has actual package, not just recipe
            has_package = True
        elif "packages" in output:
            # Check if package folder exists
            package_path = get_conan_package_path()
            if package_path and os.path.exists(os.path.join(package_path, "bin", "python3")):
                has_package = True
    
    if has_package:
        print_status(f"{CPYTHON_PACKAGE} found in cache")
        return True
    
    # Install from remote or build
    print_status(f"Installing/Building {CPYTHON_PACKAGE} via Conan...")
    
    # Try to install from remote first, then build if needed
    install_cmd = [
        conan_exe, "install", "--tool-requires", CPYTHON_PACKAGE,
        "--build=missing"
    ]
    
    # Add remote if specified
    if CONAN_REMOTE:
        install_cmd.extend(["-r", CONAN_REMOTE])
    
    print_status("This may take several minutes if building from source...")
    result = subprocess.run(install_cmd, timeout=1800)  # 30 minute timeout
    
    if result.returncode != 0:
        # Try building locally
        print_status("Remote install failed, trying local build...")
        local_build_cmd = [
            conan_exe, "create", "packages/sparetools-cpython",
            f"--version={CPY_VER}", "--build=missing"
        ]
        result = subprocess.run(local_build_cmd, timeout=1800)
        
        if result.returncode != 0:
            print_error("Conan install/build failed")
            print_error("You may need to build the package manually:")
            print_error(f"  cd packages/sparetools-cpython")
            print_error(f"  conan create . --version={CPY_VER} --build=missing")
            return False
    
    print_status("CPython installed successfully via Conan")
    return True


def get_conan_package_path():
    """Get the Conan cache path for CPython package."""
    conan_exe = find_conan_executable()
    if not conan_exe:
        return None
    
    # First, try to get package ID from list command
    list_cmd = [conan_exe, "list", f"{CPYTHON_PACKAGE}:*", "--format", "json"]
    result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
    
    package_id = None
    if result.returncode == 0:
        import json
        try:
            data = json.loads(result.stdout)
            # Navigate the JSON structure to find package_id
            for pkg_ref in data.get("Local Cache", {}).get("sparetools-cpython", {}).get("sparetools-cpython/3.12.7", {}).get("revisions", {}).values():
                for pkg_id in pkg_ref.get("packages", {}).keys():
                    if pkg_id != "da39a3ee5e6b4b0d3255bfef95601890afd80709":  # Skip empty package ID
                        package_id = pkg_id
                        break
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    
    # If we have a package ID, use it to get the path
    if package_id:
        cache_cmd = [conan_exe, "cache", "path", f"{CPYTHON_PACKAGE}:{package_id}"]
        result = subprocess.run(cache_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            package_path = result.stdout.strip().split('\n')[0]
            if package_path and os.path.exists(package_path):
                # Verify it has bin/python3
                bin_path = os.path.join(package_path, "bin", "python3")
                if os.path.exists(bin_path):
                    return package_path
    
    # Fallback: search entire Conan cache for bin directory with python3
    conan_home = os.path.expanduser("~/.conan2")
    if os.path.exists(conan_home):
        for root, dirs, files in os.walk(conan_home):
            # Look for bin/python3 or Scripts/python.exe
            if os.path.basename(root) == "bin":
                python_exe = os.path.join(root, "python3")
                if os.path.exists(python_exe):
                    # Check if this is sparetools-cpython by checking parent path
                    parent = os.path.dirname(root)
                    if "sparetools-cpython" in str(parent) or "spare" in str(parent):
                        return parent
            elif os.path.basename(root) == "Scripts":
                python_exe = os.path.join(root, "python.exe")
                if os.path.exists(python_exe):
                    parent = os.path.dirname(root)
                    if "sparetools-cpython" in str(parent) or "spare" in str(parent):
                        return parent
    
    return None


def copy_from_conan_cache(source_dir, dest_dir):
    """Copy CPython from Conan cache to installation directory."""
    print_status(f"Copying CPython from Conan cache to {dest_dir}...")
    
    if not os.path.exists(source_dir):
        print_error(f"Source directory not found: {source_dir}")
        return False
    
    # Remove existing installation if it exists
    if os.path.exists(dest_dir):
        print_status("Removing existing installation...")
        shutil.rmtree(dest_dir)
    
    # Create parent directory
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    
    # Copy entire directory
    try:
        shutil.copytree(source_dir, dest_dir)
        print_status("Copy complete")
        return True
    except OSError as e:
        print_error(f"Copy failed: {e}")
        print_error("Check disk space and permissions")
        return False
    except Exception as e:
        print_error(f"Copy failed: {e}")
        return False


def verify_installation():
    """Verify that CPython installation is valid."""
    print_status("Verifying installation...")
    
    if not os.path.exists(PYTHON_EXE):
        print_error(f"Python executable not found: {PYTHON_EXE}")
        return False
    
    if not os.path.exists(PIP_EXE):
        print_error(f"pip executable not found: {PIP_EXE}")
        return False
    
    # Test Python version
    try:
        result = subprocess.run(
            [PYTHON_EXE, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print_error("Python version check failed")
            return False
        print_status(f"Python version: {result.stdout.strip()}")
    except Exception as e:
        print_error(f"Python verification failed: {e}")
        return False
    
    return True


def install_packages():
    """Install ELM327-emulator and obd packages."""
    print_status("Installing ELM327-emulator and obd packages...")
    
    packages = ["ELM327-emulator", "obd"]
    
    for package in packages:
        print_status(f"Installing {package}...")
        try:
            result = subprocess.run(
                [PIP_EXE, "install", package],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            if result.returncode != 0:
                print_error(f"Failed to install {package}")
                print_error(result.stderr)
                return False
            print_status(f"{package} installed successfully")
        except subprocess.TimeoutExpired:
            print_error(f"Installation of {package} timed out")
            return False
        except Exception as e:
            print_error(f"Failed to install {package}: {e}")
            return False
    
    return True


def launch_emulator():
    """Launch ELM327-emulator in car scenario mode."""
    print_status("Launching ELM327-emulator in car scenario mode...")
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONHOME"] = INSTALL_DIR
    env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")
    
    # Launch emulator with car scenario
    try:
        # ELM327-emulator typically runs with: python -m elm327_emulator --scenario car
        cmd = [PYTHON_EXE, "-m", "elm327_emulator", "--scenario", "car"]
        
        print_status("Starting emulator (this will run in foreground)...")
        print_status("Press Ctrl+C to stop the emulator")
        print_status("=" * 60)
        
        # Run in foreground so user can see output
        subprocess.run(cmd, env=env, check=False)
        
    except KeyboardInterrupt:
        print_status("\nEmulator stopped by user")
    except FileNotFoundError:
        print_error("ELM327-emulator module not found")
        print_error("Verify installation completed successfully")
        return False
    except Exception as e:
        print_error(f"Failed to launch emulator: {e}")
        return False
    
    return True


def bootstrap():
    """Main bootstrap function."""
    print_status("=" * 60)
    print_status("OBD-II Bootstrap Script")
    print_status("=" * 60)
    print_status(f"Platform: {SYS_PLATFORM}")
    print_status(f"CPython Version: {CPY_VER}")
    print_status(f"Install Directory: {INSTALL_DIR}")
    print_status("=" * 60)
    
    # Check if already installed
    if os.path.exists(INSTALL_DIR) and os.path.exists(PYTHON_EXE):
        print_status("CPython installation found, skipping download")
        if not verify_installation():
            print_error("Installation verification failed, re-downloading...")
            shutil.rmtree(INSTALL_DIR)
        else:
            print_status("Installation verified")
    else:
        # Install CPython via Conan
        if not install_cpython_via_conan():
            print_error("\n" + "="*60)
            print_error("CPython installation failed. Options:")
            print_error("1. Install Conan: pip install conan==2.21.0")
            print_error(f"2. Build locally: cd packages/sparetools-cpython && conan create . --version={CPY_VER} --build=missing")
            print_error("3. Check Conan remote configuration")
            print_error("="*60)
            return 1
        
        # Get package path from Conan cache
        conan_package_path = get_conan_package_path()
        if not conan_package_path:
            print_error("Could not locate CPython package in Conan cache")
            print_error(f"Try: conan cache path {CPYTHON_PACKAGE}")
            return 1
        
        print_status(f"Found CPython in Conan cache: {conan_package_path}")
        
        # Copy from Conan cache to installation directory
        if not copy_from_conan_cache(conan_package_path, INSTALL_DIR):
            return 1
        
        if not verify_installation():
            return 1
    
    # Install packages
    if not install_packages():
        return 1
    
    # Launch emulator
    if not launch_emulator():
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(bootstrap())
    except KeyboardInterrupt:
        print_status("\nBootstrap interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
