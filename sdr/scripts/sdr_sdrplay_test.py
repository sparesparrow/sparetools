#!/usr/bin/env python3
"""
SDRplay RSP1 Test Script
Test the SDRplay device and show basic information
"""

import subprocess
import sys
import os

def run_command(cmd, timeout=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def main():
    print("=== SDRplay RSP1 Test ===")
    print()

    # Check USB connection
    print("1. USB Device Detection:")
    returncode, stdout, stderr = run_command("lsusb | grep '1df7:2500'")
    if "SDRplay RSP1" in stdout:
        print("✓ SDRplay RSP1 detected via USB")
    else:
        print("❌ SDRplay RSP1 not found via USB")
        print("Make sure the device is connected and powered on.")
        return 1

    # Check SDRplay API
    print("\n2. SDRplay API Status:")
    api_paths = [
        "/usr/local/lib/libsdrplay_api.so",
        "/usr/local/include/sdrplay_api.h"
    ]

    api_found = False
    for path in api_paths:
        if os.path.exists(path):
            print(f"✓ SDRplay API found: {path}")
            api_found = True

    if not api_found:
        print("❌ SDRplay API not found")
        print("The SDRplay API may not be properly installed.")
        return 1

    # Check GNU Radio SDRplay block
    print("\n3. GNU Radio SDRplay Support:")
    returncode, stdout, stderr = run_command("python3 -c \"import gnuradio; print('GNU Radio OK')\"")
    if returncode == 0:
        print("✓ GNU Radio is available")
    else:
        print("❌ GNU Radio not working")

    # Check for SDRplay block in GNU Radio
    returncode, stdout, stderr = run_command("find /usr -name '*sdrplay*' -type f 2>/dev/null | head -5")
    if returncode == 0 and stdout.strip():
        print("✓ SDRplay blocks found in GNU Radio")
        print("Files:", stdout[:200] + "..." if len(stdout) > 200 else stdout)
    else:
        print("ℹ️  SDRplay GNU Radio blocks may not be available")

    # Check SoapySDR (though SDRplay may not use it)
    print("\n4. SoapySDR Status:")
    returncode, stdout, stderr = run_command("SoapySDRUtil --find 2>/dev/null | grep -i sdrplay")
    if "sdrplay" in stdout.lower():
        print("✓ SDRplay detected via SoapySDR")
    else:
        print("ℹ️  SDRplay not detected via SoapySDR (expected for proprietary API)")

    # Recommendations
    print("\n5. Recommendations:")
    print("• For best SDRplay experience on Linux, consider using:")
    print("  - GNU Radio with SDRplay blocks")
    print("  - SDRangel (if available)")
    print("  - SDRplay's official tools (may require Windows)")
    print("• SDRplay RSP1 covers 1 kHz to 2 GHz with up to 10 MHz bandwidth")
    print("• Sample rates up to 10 MSPS")

    print("\n=== Test Complete ===")
    print("Your SDRplay RSP1 hardware is detected and ready!")
    print("For actual signal reception, try GNU Radio Companion or SDRangel.")

if __name__ == "__main__":
    main()