#!/usr/bin/env python3
"""
WiFi Hotspot Network Monitor with DNS Request Monitoring and TTS
Monitors connected devices, DNS requests, provides audio alerts with domain names, and visualizes traffic
"""

import subprocess
import json
import time
import threading
import socket
import struct
import os
import sys
import re
from collections import defaultdict, deque
from datetime import datetime
import argparse
import signal

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import Ether, ARP
    from scapy.layers.dns import DNS, DNSQR, DNSRR
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "scapy", "matplotlib", "numpy", "pygame", "pyttsx3", "gTTS"], check=True)
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import Ether, ARP
    from scapy.layers.dns import DNS, DNSQR, DNSRR

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    import pygame
    from tts_enhanced import EnhancedTTS
except ImportError:
    print("Installing visualization and TTS packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "numpy", "pygame", "pyttsx3", "gTTS"], check=True)
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    import pygame
    from tts_enhanced import EnhancedTTS

class NetworkMonitor:
    def __init__(self, interface="eth0", alert_threshold=10):
        self.interface = interface
        self.alert_threshold = alert_threshold
        self.running = False
        self.packet_count = 0
        self.destinations = defaultdict(int)
        self.devices = {}
        self.packet_history = deque(maxlen=1000)
        self.dns_requests = deque(maxlen=100)
        self.alerts_enabled = True
        
        # Initialize audio system
        try:
            pygame.mixer.init()
            self.alert_sound = self.create_alert_sound()
        except Exception as e:
            print(f"Warning: Could not initialize audio system: {e}")
            self.alert_sound = None
        
        # Initialize enhanced TTS
        try:
            self.tts = EnhancedTTS()
        except Exception as e:
            print(f"Warning: Could not initialize TTS: {e}")
            self.tts = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        

    def create_alert_sound(self):
        """Create a simple beep sound for alerts"""
        try:
            # Create a simple beep sound
            sample_rate = 22050
            duration = 0.5
            frequency = 800
            
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                arr[i][0] = np.sin(2 * np.pi * frequency * i / sample_rate)
                arr[i][1] = np.sin(2 * np.pi * frequency * i / sample_rate)
            
            arr = (arr * 32767).astype(np.int16)
            
            sound = pygame.sndarray.make_sound(arr)
            return sound
        except Exception as e:
            print(f"Warning: Could not create alert sound: {e}")
            return None
    
    def extract_domain_from_dns(self, packet):
        """Extract domain name from DNS query packet"""
        try:
            if packet.haslayer(DNS) and packet[DNS].qr == 0:  # DNS query
                dns_layer = packet[DNS]
                if dns_layer.qd:  # Query section exists
                    domain = dns_layer.qd.qname.decode('utf-8').rstrip('.')
                    return domain
        except Exception as e:
            pass
        return None

    def get_base_domain(self, domain):
        """Extract base domain name (e.g., google.com from www.google.com)"""
        if not domain:
            return None
        
        # Remove common subdomains
        subdomains_to_remove = ['www.', 'm.', 'mobile.', 'api.', 'app.', 'static.', 'cdn.', 'img.', 'images.']
        
        for subdomain in subdomains_to_remove:
            if domain.startswith(subdomain):
                domain = domain[len(subdomain):]
                break
        
        return domain

    def speak_domain(self, domain):
        """Speak the domain name using enhanced TTS"""
        if not self.alerts_enabled or not domain or not self.tts:
            return
        
        base_domain = self.get_base_domain(domain)
        if not base_domain:
            return
        
        try:
            # Use enhanced TTS asynchronously to avoid blocking
            self.tts.speak_async(f"Connecting to {base_domain}")
        except Exception as e:
            print(f"TTS Error: {e}")

    def play_alert(self):
        """Play alert sound"""
        if self.alert_sound and self.alerts_enabled:
            try:
                self.alert_sound.play()
            except Exception as e:
                print(f"Could not play alert sound: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down network monitor...")
        self.running = False
        sys.exit(0)
    
    def get_connected_devices(self):
        """Get list of devices connected to WiFi hotspot"""
        try:
            # Try to get connected devices using various methods
            devices = []
            
            # Method 1: Check ARP table
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[1].strip('()')
                            mac = parts[3]
                            devices.append({'ip': ip, 'mac': mac, 'method': 'arp'})
            
            # Method 2: Check DHCP leases (if available)
            try:
                with open('/var/lib/dhcp/dhcpd.leases', 'r') as f:
                    content = f.read()
                    # Parse DHCP leases (simplified)
                    for line in content.split('\n'):
                        if 'lease' in line and 'binding state active' in line:
                            # Extract IP and MAC from lease
                            pass
            except FileNotFoundError:
                pass
            
            return devices
        except Exception as e:
            print(f"Error getting connected devices: {e}")
            return []
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        if not self.running:
            return
        
        self.packet_count += 1
        
        try:
            # Extract packet information
            if packet.haslayer(IP):
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                protocol = packet[IP].proto
                
                # Update destination statistics
                self.destinations[dst_ip] += 1
                
                # Check for DNS queries
                domain = self.extract_domain_from_dns(packet)
                if domain:
                    base_domain = self.get_base_domain(domain)
                    dns_info = {
                        'timestamp': datetime.now(),
                        'src_ip': src_ip,
                        'domain': domain,
                        'base_domain': base_domain
                    }
                    self.dns_requests.append(dns_info)
                    
                    # Speak the domain name
                    self.speak_domain(domain)
                    print(f"🌐 DNS Query: {src_ip} -> {domain} (Base: {base_domain})")
                
                # Store packet info
                packet_info = {
                    'timestamp': datetime.now(),
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'protocol': protocol,
                    'size': len(packet),
                    'domain': domain if domain else None
                }
                
                if packet.haslayer(TCP):
                    packet_info['src_port'] = packet[TCP].sport
                    packet_info['dst_port'] = packet[TCP].dport
                elif packet.haslayer(UDP):
                    packet_info['src_port'] = packet[UDP].sport
                    packet_info['dst_port'] = packet[UDP].dport
                
                self.packet_history.append(packet_info)
                
                # Check for alert conditions
                if self.packet_count % self.alert_threshold == 0:
                    self.play_alert()
                    print(f"Alert: {self.packet_count} packets processed")
                
                # Print packet info
                if domain:
                    print(f"📦 Packet {self.packet_count}: {src_ip} -> {dst_ip} (DNS: {domain})")
                else:
                    print(f"📦 Packet {self.packet_count}: {src_ip} -> {dst_ip} (Protocol: {protocol})")
                
        except Exception as e:
            print(f"Error processing packet: {e}")
    
    def start_monitoring(self):
        """Start packet monitoring"""
        print(f"Starting network monitoring on interface: {self.interface}")
        print("Press Ctrl+C to stop monitoring")
        
        self.running = True
        
        try:
            # Start packet capture
            scapy.sniff(
                iface=self.interface,
                prn=self.packet_handler,
                store=0,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            print(f"Error during packet capture: {e}")
            print("Make sure you have the necessary permissions (run with sudo)")
    
    def get_top_destinations(self, limit=10):
        """Get top destination addresses"""
        return sorted(self.destinations.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_domains(self, limit=10):
        """Get top queried domains"""
        domain_counts = defaultdict(int)
        for dns_req in self.dns_requests:
            if dns_req['base_domain']:
                domain_counts[dns_req['base_domain']] += 1
        return sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def print_statistics(self):
        """Print current statistics"""
        print("\n" + "="*60)
        print("NETWORK MONITORING STATISTICS")
        print("="*60)
        print(f"Total packets processed: {self.packet_count}")
        print(f"DNS queries captured: {len(self.dns_requests)}")
        print(f"Unique destinations: {len(self.destinations)}")
        print(f"Connected devices: {len(self.get_connected_devices())}")
        
        print("\nTop 10 Destinations:")
        for i, (dest, count) in enumerate(self.get_top_destinations(10), 1):
            print(f"{i:2d}. {dest:15s} - {count:6d} packets")
        
        print("\nTop 10 Domains Queried:")
        for i, (domain, count) in enumerate(self.get_top_domains(10), 1):
            print(f"{i:2d}. {domain:25s} - {count:6d} queries")
        
        print("="*60)

def create_visualization(monitor):
    """Create real-time visualization of network traffic"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('WiFi Hotspot Network Monitor', fontsize=16)
    
    # Setup plots
    ax1.set_title('Packet Count Over Time')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Packets per Second')
    
    ax2.set_title('Top Destination Addresses')
    ax2.set_xlabel('Destination IP')
    ax2.set_ylabel('Packet Count')
    
    def animate(frame):
        ax1.clear()
        ax2.clear()
        
        # Plot packet count over time
        if len(monitor.packet_history) > 0:
            timestamps = [p['timestamp'] for p in list(monitor.packet_history)[-100:]]
            packet_counts = list(range(len(timestamps)))
            ax1.plot(timestamps, packet_counts, 'b-', linewidth=2)
            ax1.set_title(f'Packet Count Over Time (Total: {monitor.packet_count})')
            ax1.set_ylabel('Packets')
        
        # Plot top destinations
        top_dests = monitor.get_top_destinations(10)
        if top_dests:
            dests, counts = zip(*top_dests)
            ax2.bar(range(len(dests)), counts, color='red', alpha=0.7)
            ax2.set_xticks(range(len(dests)))
            ax2.set_xticklabels(dests, rotation=45, ha='right')
            ax2.set_title('Top Destination Addresses')
            ax2.set_ylabel('Packet Count')
        
        plt.tight_layout()
    
    ani = animation.FuncAnimation(fig, animate, interval=1000, blit=False)
    plt.show()

def setup_xiaomi_hidden_settings():
    """Setup instructions for accessing Xiaomi 11 hidden settings"""
    print("\n" + "="*60)
    print("XIAOMI 11 HIDDEN SETTINGS ACCESS")
    print("="*60)
    print("To access hidden settings on Xiaomi 11:")
    print()
    print("1. Open the Phone/Dialer app")
    print("2. Dial the following codes:")
    print()
    print("   * # * # 4636 # * # *  - Testing menu")
    print("   * # * # 6484 # * # *  - Version info")
    print("   * # * # 6485 # * # *  - Version info (alternative)")
    print("   * # * # 232337 # * # * - Bluetooth test")
    print("   * # * # 0842 # * # *  - Vibration test")
    print("   * # * # 2663 # * # *  - Touch screen test")
    print("   * # * # 0289 # * # *  - Audio test")
    print("   * # * # 0588 # * # *  - Proximity sensor test")
    print("   * # * # 3264 # * # *  - RAM info")
    print("   * # * # 232338 # * # * - WiFi test")
    print("   * # * # 232331 # * # * - Bluetooth test")
    print("   * # * # 232337 # * # * - Bluetooth test (alternative)")
    print()
    print("3. For WiFi hotspot settings:")
    print("   - Go to Settings > WiFi > WiFi Hotspot")
    print("   - Or use: * # * # 232338 # * # *")
    print()
    print("4. For advanced network settings:")
    print("   - Go to Settings > About Phone > All specs")
    print("   - Tap 'Kernel version' 7 times")
    print("   - Go back to Settings > Additional settings > Developer options")
    print()
    print("5. Enable USB Debugging and Developer Options:")
    print("   - Go to Settings > About Phone")
    print("   - Tap 'MIUI version' 7 times")
    print("   - Go to Settings > Additional settings > Developer options")
    print("   - Enable 'USB debugging' and 'USB debugging (Security settings)'")
    print()
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='WiFi Hotspot Network Monitor')
    parser.add_argument('-i', '--interface', default='wlan0', 
                       help='Network interface to monitor (default: wlan0)')
    parser.add_argument('-t', '--threshold', type=int, default=10,
                       help='Alert threshold for packet count (default: 10)')
    parser.add_argument('-v', '--visualize', action='store_true',
                       help='Enable real-time visualization')
    parser.add_argument('--no-audio', action='store_true',
                       help='Disable audio alerts')
    parser.add_argument('--xiaomi-setup', action='store_true',
                       help='Show Xiaomi 11 hidden settings setup')
    
    args = parser.parse_args()
    
    if args.xiaomi_setup:
        setup_xiaomi_hidden_settings()
        return
    
    # Check if running as root
    if os.geteuid() != 0:
        print("Warning: This script requires root privileges for packet capture.")
        print("Please run with: sudo python3 network_monitor.py")
        print("Or use: sudo -E python3 network_monitor.py")
    
    # Create and configure monitor
    monitor = NetworkMonitor(interface=args.interface, alert_threshold=args.threshold)
    monitor.alerts_enabled = not args.no_audio
    
    # Show connected devices
    devices = monitor.get_connected_devices()
    if devices:
        print(f"\nFound {len(devices)} connected devices:")
        for device in devices:
            print(f"  IP: {device['ip']}, MAC: {device['mac']}")
    else:
        print("\nNo connected devices found or unable to detect them.")
    
    # Start monitoring
    if args.visualize:
        # Start visualization in separate thread
        viz_thread = threading.Thread(target=create_visualization, args=(monitor,))
        viz_thread.daemon = True
        viz_thread.start()
        
        # Start monitoring in main thread
        monitor.start_monitoring()
    else:
        # Start monitoring with periodic statistics
        def print_stats():
            while monitor.running:
                time.sleep(30)  # Print stats every 30 seconds
                if monitor.running:
                    monitor.print_statistics()
        
        stats_thread = threading.Thread(target=print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        monitor.start_monitoring()

if __name__ == "__main__":
    main()
