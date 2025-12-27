#!/usr/bin/env python3
"""
RTSP Service Discovery
Discovers RTSP services on the network and tests connectivity
"""

import socket
import threading
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class RTSPDiscovery:
    def __init__(self):
        self.rtsp_services = []
        self.discovered_ips = set()
        
    def scan_ip_range(self, network_base, start=1, end=254):
        """Scan IP range for RTSP services"""
        print(f"🔍 Scanning network {network_base}.{start}-{end} for RTSP services...")
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            
            for i in range(start, end + 1):
                ip = f"{network_base}.{i}"
                future = executor.submit(self.test_rtsp_service, ip)
                futures.append((ip, future))
            
            for ip, future in futures:
                try:
                    result = future.result(timeout=2)
                    if result:
                        self.rtsp_services.append(result)
                        print(f"✅ Found RTSP service: {result['url']}")
                except:
                    pass
    
    def test_rtsp_service(self, ip):
        """Test if IP has RTSP service"""
        rtsp_ports = [554, 8554, 1935]  # Common RTSP ports
        
        for port in rtsp_ports:
            try:
                # Test TCP connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    # Test RTSP handshake
                    rtsp_url = f"rtsp://{ip}:{port}/"
                    if self.test_rtsp_handshake(rtsp_url):
                        return {
                            'ip': ip,
                            'port': port,
                            'url': rtsp_url,
                            'status': 'active'
                        }
            except:
                continue
        
        return None
    
    def test_rtsp_handshake(self, rtsp_url):
        """Test RTSP handshake"""
        try:
            # Use ffprobe to test RTSP connection
            cmd = ['ffprobe', '-v', 'quiet', '-rtsp_transport', 'tcp', 
                   '-i', rtsp_url, '-show_entries', 'format=duration']
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def discover_rtsp_services(self):
        """Main discovery function"""
        print("🚀 Starting RTSP Service Discovery")
        print("=" * 40)
        
        # Get local network
        local_ip = self.get_local_ip()
        if not local_ip:
            print("❌ Could not determine local IP")
            return
        
        network_base = '.'.join(local_ip.split('.')[:-1])
        print(f"🌐 Local network: {network_base}.x")
        
        # Scan local network
        self.scan_ip_range(network_base)
        
        # Show results
        self.show_results()
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None
    
    def show_results(self):
        """Show discovery results"""
        print(f"\n📊 Discovery Results")
        print("=" * 20)
        
        if not self.rtsp_services:
            print("❌ No RTSP services found")
            return
        
        print(f"✅ Found {len(self.rtsp_services)} RTSP service(s):")
        print()
        
        for i, service in enumerate(self.rtsp_services, 1):
            print(f"{i}. {service['ip']}:{service['port']}")
            print(f"   URL: {service['url']}")
            print(f"   Status: {service['status']}")
            print()
    
    def test_rtsp_url(self, rtsp_url):
        """Test specific RTSP URL"""
        print(f"🧪 Testing RTSP URL: {rtsp_url}")
        
        try:
            # Extract IP and port
            url_parts = rtsp_url.replace('rtsp://', '').split('/')
            ip_port = url_parts[0]
            ip, port = ip_port.split(':')
            
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            
            if result != 0:
                print(f"❌ TCP connection failed")
                return False
            
            print(f"✅ TCP connection successful")
            
            # Test RTSP handshake
            if self.test_rtsp_handshake(rtsp_url):
                print(f"✅ RTSP handshake successful")
                return True
            else:
                print(f"❌ RTSP handshake failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing RTSP URL: {e}")
            return False
    
    def save_results(self, filename="rtsp_discovery_results.json"):
        """Save discovery results to JSON file"""
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'services': self.rtsp_services
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to {filename}")

def main():
    discovery = RTSPDiscovery()
    
    print("RTSP Service Discovery Tool")
    print("=" * 30)
    print()
    print("Options:")
    print("1. Discover RTSP services on network")
    print("2. Test specific RTSP URL")
    print("3. Exit")
    print()
    
    while True:
        choice = input("Enter your choice [1-3]: ").strip()
        
        if choice == '1':
            discovery.discover_rtsp_services()
            discovery.save_results()
            break
        elif choice == '2':
            rtsp_url = input("Enter RTSP URL: ").strip()
            if rtsp_url:
                discovery.test_rtsp_url(rtsp_url)
            break
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()