#!/usr/bin/env python3
"""
OBD-II bootstrap entrypoint packaged for Conan consumption.

Uses bundled CPython from sparetools-cpython package via tool_requires.
Run after: conan install --requires=sparetools-obd-sim/2.0.0 -g VirtualRunEnv
Then source the generated environment script.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Use bundled CPython from environment (set by sparetools-cpython tool_requires)
INSTALL_DIR = os.environ.get("PYTHONHOME", sys.prefix)
BIN_DIR = os.path.dirname(sys.executable)
PYTHON_EXE = sys.executable

SYS_PLATFORM = platform.system()
PACKAGE_ROOT = Path(__file__).resolve().parent


def print_status(msg: str) -> None:
    """Print status message."""
    print(f"[BOOTSTRAP] {msg}", flush=True)


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)



def verify_installation() -> bool:
    """Verify that CPython installation is valid."""
    print_status("Verifying installation...")

    if not os.path.exists(PYTHON_EXE):
        print_error(f"Python executable not found: {PYTHON_EXE}")
        return False

    # Test Python version
    try:
        result = subprocess.run(
            [PYTHON_EXE, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print_error("Python version check failed")
            return False
        print_status(f"Python version: {result.stdout.strip()}")
    except Exception as e:  # pylint: disable=broad-except
        print_error(f"Python verification failed: {e}")
        return False

    # Ensure pip is available
    try:
        result = subprocess.run(
            [PYTHON_EXE, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            print_error("pip check failed")
            print_error(result.stderr)
            return False
        print_status(f"pip: {result.stdout.strip()}")
    except Exception as e:  # pylint: disable=broad-except
        print_error(f"pip verification failed: {e}")
        return False

    return True


def install_packages() -> bool:
    """Install ELM327-emulator and obd packages."""
    print_status("Installing ELM327-emulator and obd packages...")

    packages = ["ELM327-emulator", "obd"]

    for package in packages:
        print_status(f"Installing {package}...")
        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            if result.returncode != 0:
                print_error(f"Failed to install {package}")
                print_error(result.stderr)
                return False
            print_status(f"{package} installed successfully")
        except subprocess.TimeoutExpired:
            print_error(f"Installation of {package} timed out")
            return False
        except Exception as e:  # pylint: disable=broad-except
            print_error(f"Failed to install {package}: {e}")
            return False

    return True


def launch_emulator() -> bool:
    """Launch ELM327-emulator in car scenario mode."""
    print_status("Launching ELM327-emulator in car scenario mode...")

    # Set up environment with bundled Python
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
    except Exception as e:  # pylint: disable=broad-except
        print_error(f"Failed to launch emulator: {e}")
        return False

    return True


def bootstrap() -> int:
    """Main bootstrap function using bundled CPython."""
    print_status("=" * 60)
    print_status("OBD-II Bootstrap Script")
    print_status("=" * 60)
    print_status(f"Platform: {SYS_PLATFORM}")
    print_status(f"Python Executable: {PYTHON_EXE}")
    print_status(f"Python Home: {INSTALL_DIR}")
    print_status("=" * 60)

    # Verify bundled Python installation
    if not verify_installation():
        print_error("Bundled Python verification failed")
        print_error("Make sure you're running this after:")
        print_error("  conan install --requires=sparetools-obd-sim/2.0.0 -g VirtualRunEnv")
        print_error("  source .conan/activate.sh  # or .conan\\activate.bat on Windows")
        return 1

    print_status("Using bundled CPython from sparetools-cpython package")

    # Install packages
    if not install_packages():
        return 1

    # Launch emulator
    if not launch_emulator():
        return 1

    return 0


def main() -> int:
    """Entrypoint wrapper for module execution."""
    try:
        return bootstrap()
    except KeyboardInterrupt:
        print_status("\nBootstrap interrupted by user")
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print_error(f"Unexpected error: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
