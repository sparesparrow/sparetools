#!/usr/bin/env python3
"""
WiFi Scanner Tool
Scans for nearby WiFi networks and performs motion detection analysis
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.motion_detector import MotionDetector
    from tts_enhanced import EnhancedTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class WiFiScanner:
    """WiFi network scanner with motion detection capabilities"""

    def __init__(self, interface="wlan0", motion_detection=False):
        self.interface = interface
        self.motion_detection = motion_detection

        # Initialize components
        self.motion_detector = MotionDetector() if motion_detection else None
        self.tts = EnhancedTTS() if TTS_AVAILABLE else None

        # Scan results
        self.last_scan = {}
        self.scan_count = 0

    def scan_networks(self):
        """Scan for WiFi networks using iwlist"""
        try:
            cmd = ["iwlist", self.interface, "scan"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"❌ Scan failed: {result.stderr}")
                return {}

            networks = self._parse_iwlist_output(result.stdout)
            self.last_scan = networks
            self.scan_count += 1

            return networks

        except subprocess.TimeoutExpired:
            print("⏰ Scan timed out")
            return {}
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return {}

    def _parse_iwlist_output(self, output):
        """Parse iwlist scan output"""
        networks = {}
        current_network = {}

        for line in output.split('\n'):
            line = line.strip()

            # New network starts
            if line.startswith('Cell ') or line.startswith('Address: '):
                if current_network and 'address' in current_network:
                    networks[current_network['address']] = current_network
                current_network = {}

            # Parse network information
            if 'Address:' in line:
                current_network['address'] = line.split('Address:')[1].strip()
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                current_network['essid'] = essid if essid else '<hidden>'
            elif 'Frequency:' in line:
                import re
                freq_match = re.search(r'(\d+\.\d+)', line)
                if freq_match:
                    current_network['frequency'] = float(freq_match.group(1))
            elif 'Signal level=' in line:
                import re
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                if signal_match:
                    current_network['signal_level'] = int(signal_match.group(1))
            elif 'Quality=' in line:
                import re
                quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                if quality_match:
                    current_network['quality'] = int(quality_match.group(1))
                    current_network['quality_max'] = int(quality_match.group(2))
            elif 'Encryption key:' in line:
                current_network['encrypted'] = 'on' in line.lower()

        # Add last network
        if current_network and 'address' in current_network:
            networks[current_network['address']] = current_network

        return networks

    def print_network_summary(self, networks):
        """Print formatted network summary"""
        if not networks:
            print("📡 No WiFi networks found")
            return

        print(f"\n📡 Found {len(networks)} WiFi networks (Scan #{self.scan_count}):")
        print("-" * 80)

        # Sort by signal strength
        sorted_networks = sorted(networks.values(),
                               key=lambda x: x.get('signal_level', -100),
                               reverse=True)

        for i, network in enumerate(sorted_networks[:10], 1):  # Top 10
            essid = network.get('essid', '<hidden>')
            signal = network.get('signal_level', 'N/A')
            quality = network.get('quality', 0)
            quality_max = network.get('quality_max', 70)
            freq = network.get('frequency', 'N/A')
            encrypted = "🔒" if network.get('encrypted', False) else "🔓"

            quality_percent = int((quality / quality_max) * 100) if quality_max > 0 else 0

            print("2d")

        print("-" * 80)

    def analyze_motion(self, networks):
        """Analyze networks for motion detection"""
        if not self.motion_detector:
            return

        # Update motion detector with current signals
        for mac, network in networks.items():
            if 'signal_level' in network:
                self.motion_detector.update_signal(mac, network['signal_level'])

        # Analyze for motion
        motion_results = self.motion_detector.analyze_signal_fluctuations()

        if motion_results:
            motion_detected = any(result['motion_detected'] for result in motion_results.values())

            if motion_detected:
                print("🚨 MOTION DETECTED!")
                for mac, result in motion_results.items():
                    if result['motion_detected']:
                        network = networks.get(mac, {})
                        essid = network.get('essid', 'Unknown')
                        print(".1f")

                # TTS announcement
                if self.tts:
                    self.tts.speak_async("Motion detected through WiFi signals")

    def continuous_scan(self, interval=5, max_scans=None):
        """Perform continuous scanning"""
        print(f"🔍 Starting continuous WiFi scanning on {self.interface}")
        print(f"📊 Scanning every {interval} seconds...")
        if self.motion_detection:
            print("🎯 Motion detection enabled")
        print("Press Ctrl+C to stop\n")

        scan_num = 0
        try:
            while max_scans is None or scan_num < max_scans:
                scan_num += 1
                print(f"\n🔄 Scan #{scan_num} - {time.strftime('%H:%M:%S')}")

                networks = self.scan_networks()

                if networks:
                    self.print_network_summary(networks)

                    if self.motion_detection:
                        self.analyze_motion(networks)
                else:
                    print("📡 No networks detected")

                if max_scans is None or scan_num < max_scans:
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\n🛑 Stopping WiFi scanner...")

        # Final statistics
        if self.motion_detection and self.motion_detector:
            stats = self.motion_detector.get_motion_statistics()
            print(f"\n📊 Final Statistics:")
            print(f"   Total scans: {scan_num}")
            print(f"   Motion events: {stats['total_events']}")
            print(f"   Networks monitored: {stats['networks_monitored']}")

    def single_scan(self):
        """Perform a single scan"""
        print("🔍 Performing single WiFi scan...")

        networks = self.scan_networks()

        if networks:
            self.print_network_summary(networks)

            if self.motion_detection:
                self.analyze_motion(networks)

                # Show motion statistics
                if self.motion_detector:
                    stats = self.motion_detector.get_motion_statistics()
                    print(f"\n📊 Motion Analysis:")
                    print(f"   Networks analyzed: {len(self.motion_detector.signal_history)}")
                    if stats['total_events'] > 0:
                        print(f"   Motion events detected: {stats['total_events']}")
                        print(".2f")
                    else:
                        print("   No significant motion detected in this scan")
        else:
            print("❌ No WiFi networks found. Make sure WiFi is enabled and scanning is allowed.")

def main():
    parser = argparse.ArgumentParser(description='WiFi Scanner with Motion Detection')
    parser.add_argument('-i', '--interface', default='wlan0',
                       help='WiFi interface to use (default: wlan0)')
    parser.add_argument('-c', '--continuous', action='store_true',
                       help='Enable continuous scanning mode')
    parser.add_argument('-t', '--interval', type=int, default=5,
                       help='Scan interval in seconds (default: 5)')
    parser.add_argument('-m', '--motion-detection', action='store_true',
                       help='Enable motion detection analysis')
    parser.add_argument('-n', '--max-scans', type=int,
                       help='Maximum number of scans for continuous mode')
    parser.add_argument('--no-tts', action='store_true',
                       help='Disable text-to-speech announcements')

    args = parser.parse_args()

    # Check if interface exists
    try:
        result = subprocess.run(['iwconfig', args.interface], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ WiFi interface '{args.interface}' not found!")
            print("Available interfaces:")
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    interface = line.split()[0]
                    print(f"  - {interface}")
            return 1
    except FileNotFoundError:
        print("❌ iwconfig not found. Please install wireless-tools package.")
        return 1

    # Create scanner
    scanner = WiFiScanner(args.interface, args.motion_detection)

    if args.no_tts:
        scanner.tts = None

    if args.continuous:
        scanner.continuous_scan(args.interval, args.max_scans)
    else:
        scanner.single_scan()

if __name__ == "__main__":
    main()