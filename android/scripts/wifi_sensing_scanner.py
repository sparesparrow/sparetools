#!/usr/bin/env python3
"""
WiFi Sensing Scanner - Advanced WiFi Network Analysis and Motion Detection
Uses WiFi signal analysis to detect nearby networks and monitor signal fluctuations
that could indicate movement through walls (CSI-based sensing)
"""

import subprocess
import sys
import time
import json
import threading
import argparse
from collections import defaultdict, deque
from datetime import datetime
import re
import os

# Import TTS for announcements
sys.path.append('.')
try:
    from tts_enhanced import EnhancedTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class WiFiSensingScanner:
    def __init__(self, interface="wlan0", continuous=False):
        self.interface = interface
        self.continuous = continuous
        self.running = False
        self.networks = {}
        self.signal_history = defaultdict(lambda: deque(maxlen=100))
        self.motion_events = deque(maxlen=50)

        # Initialize TTS
        if TTS_AVAILABLE:
            self.tts = EnhancedTTS()
        else:
            self.tts = None

    def scan_wifi_networks(self):
        """Scan for WiFi networks using iwlist"""
        try:
            cmd = ["iwlist", self.interface, "scan"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"❌ WiFi scan failed: {result.stderr}")
                return {}

            networks = {}
            current_network = {}

            for line in result.stdout.split('\n'):
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
                    freq_match = re.search(r'(\d+\.\d+)', line)
                    if freq_match:
                        current_network['frequency'] = float(freq_match.group(1))
                elif 'Signal level=' in line:
                    signal_match = re.search(r'Signal level=(-?\d+)', line)
                    if signal_match:
                        current_network['signal_level'] = int(signal_match.group(1))
                elif 'Quality=' in line:
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

        except subprocess.TimeoutExpired:
            print("⚠️ WiFi scan timed out")
            return {}
        except Exception as e:
            print(f"❌ Error scanning WiFi: {e}")
            return {}

    def analyze_signal_fluctuations(self, current_networks):
        """Analyze signal strength fluctuations for motion detection"""
        motion_detected = False
        anomalies = []

        for mac, network in current_networks.items():
            if 'signal_level' in network:
                signal = network['signal_level']
                self.signal_history[mac].append({
                    'timestamp': datetime.now(),
                    'signal': signal,
                    'essid': network.get('essid', 'Unknown')
                })

                # Analyze recent signal history for motion patterns
                history = list(self.signal_history[mac])
                if len(history) >= 5:
                    recent_signals = [h['signal'] for h in history[-5:]]

                    # Calculate signal variance (motion indicator)
                    variance = sum((x - sum(recent_signals)/len(recent_signals))**2 for x in recent_signals) / len(recent_signals)

                    # Sudden signal drops/changes can indicate movement
                    if variance > 50:  # High variance threshold
                        anomalies.append({
                            'mac': mac,
                            'essid': network.get('essid', 'Unknown'),
                            'variance': variance,
                            'recent_signals': recent_signals
                        })
                        motion_detected = True

        if motion_detected and anomalies:
            motion_event = {
                'timestamp': datetime.now(),
                'anomalies': anomalies,
                'description': f"Signal fluctuations detected in {len(anomalies)} networks"
            }
            self.motion_events.append(motion_event)

            # Announce motion detection
            if self.tts:
                self.tts.speak_async("Motion detected through WiFi signals")

            print(f"🚨 MOTION DETECTED: Signal fluctuations in {len(anomalies)} networks")
            for anomaly in anomalies[:3]:  # Show top 3
                print(".1f")

        return motion_detected

    def print_network_summary(self, networks):
        """Print a summary of discovered networks"""
        if not networks:
            print("📡 No WiFi networks found")
            return

        print(f"\n📡 Found {len(networks)} WiFi networks:")
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

    def continuous_monitoring(self, interval=5):
        """Continuously monitor WiFi networks for sensing"""
        print(f"🔍 Starting WiFi sensing on interface: {self.interface}")
        print(f"📊 Monitoring every {interval} seconds...")
        print("🎯 Looking for signal fluctuations that may indicate motion through walls")
        print("Press Ctrl+C to stop\n")

        self.running = True
        scan_count = 0

        try:
            while self.running:
                scan_count += 1
                print(f"\n🔄 Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")

                # Scan networks
                networks = self.scan_wifi_networks()

                if networks:
                    # Analyze for motion detection
                    motion_detected = self.analyze_signal_fluctuations(networks)

                    # Print summary periodically
                    if scan_count % 5 == 1:  # Every 5 scans
                        self.print_network_summary(networks)

                    # Show motion events
                    if motion_detected:
                        print(f"📈 Total motion events detected: {len(self.motion_events)}")
                else:
                    print("📡 No networks detected")

                # Wait before next scan
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n🛑 Stopping WiFi sensing...")
            self.running = False

    def single_scan(self):
        """Perform a single WiFi scan and analysis"""
        print("🔍 Performing single WiFi scan and analysis...")

        networks = self.scan_wifi_networks()

        if networks:
            self.print_network_summary(networks)
            self.analyze_signal_fluctuations(networks)

            # Show CSI-like analysis
            print("\n🔬 WiFi Sensing Analysis:")
            print("-" * 50)
            print("This demonstrates the concept of WiFi sensing for motion detection.")
            print("In real CSI (Channel State Information) sensing systems:")
            print("• Signal fluctuations can detect movement through walls")
            print("• Multi-path effects create unique 'fingerprints' of environments")
            print("• AI/ML models analyze signal patterns to classify activities")
            print("• Studies show accuracy rates of 85-95% for presence detection")

            if self.motion_events:
                print(f"\n✅ Motion analysis: {len(self.motion_events)} events detected in this scan")
            else:
                print("\n📊 No significant motion detected in current scan")

        else:
            print("❌ No WiFi networks found. Make sure WiFi is enabled and scanning is allowed.")

    def export_data(self, filename="wifi_sensing_data.json"):
        """Export collected sensing data"""
        data = {
            'scan_timestamp': datetime.now().isoformat(),
            'interface': self.interface,
            'networks': dict(self.networks),
            'motion_events': list(self.motion_events),
            'signal_history': {mac: list(history) for mac, history in self.signal_history.items()}
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"💾 Data exported to {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='WiFi Sensing Scanner - Motion Detection through Walls')
    parser.add_argument('-i', '--interface', default='wlan0',
                       help='WiFi interface to use (default: wlan0)')
    parser.add_argument('-c', '--continuous', action='store_true',
                       help='Enable continuous monitoring mode')
    parser.add_argument('-t', '--interval', type=int, default=5,
                       help='Scan interval in seconds for continuous mode (default: 5)')
    parser.add_argument('-e', '--export', type=str,
                       help='Export data to JSON file')
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
    scanner = WiFiSensingScanner(interface=args.interface, continuous=args.continuous)

    if args.no_tts:
        scanner.tts = None

    print("🏠 WiFi Sensing Scanner")
    print("=" * 50)
    print("This tool demonstrates WiFi sensing concepts for motion detection")
    print("Similar to studies that use AI to detect movement through walls")
    print("using WiFi signal fluctuations and Channel State Information (CSI)")
    print()

    if args.continuous:
        scanner.continuous_monitoring(args.interval)
    else:
        scanner.single_scan()

    # Export data if requested
    if args.export:
        scanner.export_data(args.export)

if __name__ == "__main__":
    main()