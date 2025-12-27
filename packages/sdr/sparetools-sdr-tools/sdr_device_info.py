#!/usr/bin/env python3
"""
SDR Device Information Script
Shows information about connected SDR devices
"""

import subprocess
import sys

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def main():
    print("=== SDR Device Information ===")
    print()

    # Check USB devices
    print("USB SDR Devices:")
    usb_output, usb_error = run_command("lsusb | grep -E '(RTL|SDRplay|HackRF|BladeRF|Airspy)'")
    if usb_output:
        print(usb_output)
    else:
        print("No SDR USB devices found")
    print()

    # Check SoapySDR devices
    print("SoapySDR Devices:")
    soapy_output, soapy_error = run_command("SoapySDRUtil --find")
    if soapy_output:
        print(soapy_output)
    else:
        print("No SoapySDR devices found")
        if soapy_error:
            print(f"Error: {soapy_error}")
    print()

    # Check RTL-SDR devices
    print("RTL-SDR Test:")
    rtl_output, rtl_error = run_command("rtl_test -t 1 2>/dev/null | head -5")
    if rtl_output and "No supported devices found" not in rtl_output:
        print("RTL-SDR device detected")
        print(rtl_output)
    else:
        print("No RTL-SDR devices found")
    print()

    # Check GNU Radio
    print("GNU Radio Status:")
    try:
        import gnuradio
        from gnuradio import gr
        print("✓ GNU Radio is installed and working")
    except ImportError as e:
        print(f"✗ GNU Radio import failed: {e}")
    print()

    # SDR Software Status
    print("SDR Software Status:")
    software = [
        ("gqrx", "which gqrx >/dev/null && echo 'Available'"),
        ("cubicsdr", "which cubicsdr >/dev/null && echo 'Available'"),
        ("inspectrum", "which inspectrum >/dev/null && echo 'Available'"),
        ("kalibrate-rtl", "which kalibrate-rtl >/dev/null && echo 'Available'"),
        ("multimon-ng", "which multimon-ng >/dev/null && echo 'Available'"),
        ("gnuradio-companion", "which gnuradio-companion >/dev/null && echo 'Available'"),
        ("rtl_test", "which rtl_test >/dev/null && echo 'Available'"),
    ]

    for name, cmd in software:
        output, error = run_command(cmd)
        if output.strip():
            print(f"✓ {name}: Available")
        else:
            print(f"✗ {name}: Not available")

if __name__ == "__main__":
    main()