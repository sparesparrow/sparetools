#!/usr/bin/env python3
"""
SDR Frequency Scanner
Scans frequency ranges and detects signals using RTL-SDR
"""

import subprocess
import sys
import time
import argparse

def run_command(cmd, timeout=None):
    """Run a shell command with optional timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def scan_frequency(freq_mhz, gain=20, sample_rate=2.4e6):
    """Scan a specific frequency"""
    freq_hz = int(freq_mhz * 1e6)
    sample_rate_hz = int(sample_rate * 1e6)

    # Use rtl_power to scan
    cmd = f"rtl_power -f {freq_hz}:{freq_hz} -g {gain} -r {sample_rate_hz} -i 1 -1 scan.csv"
    returncode, stdout, stderr = run_command(cmd, timeout=5)

    if returncode == 0:
        # Parse the CSV output
        try:
            with open("scan.csv", "r") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    data = lines[1].strip().split(",")
                    if len(data) >= 7:
                        power_db = float(data[6])
                        return power_db
        except:
            pass

    return None

def main():
    parser = argparse.ArgumentParser(description="SDR Frequency Scanner")
    parser.add_argument("-f", "--freq", type=float, default=100.0,
                       help="Frequency to scan in MHz (default: 100.0)")
    parser.add_argument("-s", "--start", type=float,
                       help="Start frequency in MHz")
    parser.add_argument("-e", "--end", type=float,
                       help="End frequency in MHz")
    parser.add_argument("-g", "--gain", type=int, default=20,
                       help="RTL-SDR gain (default: 20)")
    parser.add_argument("-r", "--rate", type=float, default=2.4,
                       help="Sample rate in MHz (default: 2.4)")

    args = parser.parse_args()

    print("=== SDR Frequency Scanner ===")
    print()

    # Check if RTL-SDR is available
    returncode, stdout, stderr = run_command("rtl_test -t 1", timeout=5)
    if returncode != 0:
        print("❌ No RTL-SDR device found!")
        print("Make sure RTL-SDR is connected and drivers are installed.")
        return 1

    print("✓ RTL-SDR device detected")

    if args.start and args.end:
        # Scan a range
        print(f"Scanning from {args.start} MHz to {args.end} MHz...")
        print("Frequency (MHz) | Power (dB)")
        print("-" * 30)

        freq = args.start
        while freq <= args.end:
            power = scan_frequency(freq, args.gain, args.rate)
            if power is not None:
                signal_indicator = "📶" if power > -50 else "📡" if power > -70 else "📻"
                print(".1f")
            else:
                print(".1f")

            freq += 1.0  # Scan in 1 MHz steps
            time.sleep(0.1)  # Small delay

    else:
        # Scan single frequency
        freq = args.freq
        print(f"Scanning frequency: {freq} MHz")
        power = scan_frequency(freq, args.gain, args.rate)

        if power is not None:
            print(".1f")

            # Signal strength interpretation
            if power > -30:
                print("🎯 Strong signal detected!")
            elif power > -50:
                print("📶 Moderate signal")
            elif power > -70:
                print("📡 Weak signal")
            else:
                print("📻 Very weak or no signal")
        else:
            print("❌ Failed to scan frequency")

    # Clean up
    run_command("rm -f scan.csv")

if __name__ == "__main__":
    main()