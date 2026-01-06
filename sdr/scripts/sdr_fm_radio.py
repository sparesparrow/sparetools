#!/usr/bin/env python3
"""
SDR FM Radio Receiver
Receive FM radio stations using RTL-SDR
"""

import subprocess
import sys
import argparse
import os

def run_command(cmd, background=False, timeout=None):
    """Run a shell command"""
    try:
        if background:
            process = subprocess.Popen(cmd, shell=True)
            return process, "", ""
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def play_fm_radio(freq_mhz, gain=20, output_device=None):
    """Play FM radio using rtl_fm and play"""
    freq_hz = int(freq_mhz * 1e6)

    # Build rtl_fm command
    cmd = f"rtl_fm -f {freq_hz} -M fm -s 170k -A fast -r 32k -l 0 -g {gain}"

    # Add output device if specified
    if output_device:
        cmd += f" | play -r 32k -t raw -e s -b 16 -c 1 -V1 -"
    else:
        cmd += " | play -r 32k -t raw -e s -b 16 -c 1 -V1 -"

    print(f"Tuning to {freq_mhz} MHz FM...")
    print("Press Ctrl+C to stop")
    print()

    try:
        returncode, stdout, stderr = run_command(cmd)
        return returncode
    except KeyboardInterrupt:
        print("\nStopping FM radio...")
        return 0

def main():
    parser = argparse.ArgumentParser(description="SDR FM Radio Receiver")
    parser.add_argument("-f", "--freq", type=float, required=True,
                       help="FM frequency in MHz (e.g., 88.5)")
    parser.add_argument("-g", "--gain", type=int, default=20,
                       help="RTL-SDR gain (default: 20)")
    parser.add_argument("-o", "--output", type=str,
                       help="Audio output device (optional)")

    args = parser.parse_args()

    print("=== SDR FM Radio Receiver ===")
    print()

    # Check if RTL-SDR is available
    returncode, stdout, stderr = run_command("rtl_test -t 1", timeout=5)
    if returncode != 0:
        print("❌ No RTL-SDR device found!")
        print("Make sure RTL-SDR is connected and drivers are installed.")
        print("Note: SDRplay devices may not work with this script.")
        return 1

    print("✓ RTL-SDR device detected")

    # Check if play (sox) is available
    returncode, stdout, stderr = run_command("which play")
    if returncode != 0:
        print("❌ 'play' command not found!")
        print("Install sox package: sudo apt install sox")
        return 1

    print("✓ Audio playback available")

    # Validate frequency range
    if not (65.0 <= args.freq <= 108.0):
        print(f"❌ Frequency {args.freq} MHz is outside FM broadcast range (65-108 MHz)")
        return 1

    print(f"🎵 Starting FM radio on {args.freq} MHz...")
    print(f"   Gain: {args.gain}")
    if args.output:
        print(f"   Output device: {args.output}")
    print()

    # Start FM radio
    result = play_fm_radio(args.freq, args.gain, args.output)

    if result == 0:
        print("FM radio session ended successfully")
    else:
        print(f"FM radio session failed with code: {result}")

if __name__ == "__main__":
    main()