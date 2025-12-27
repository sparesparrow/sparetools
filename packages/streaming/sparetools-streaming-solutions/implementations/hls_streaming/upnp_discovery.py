#!/usr/bin/env python3
"""
UPnP Discovery Script for TV and Media Server Detection
"""

import socket
import time
import threading
from urllib.parse import urlparse
import requests

MCAST_GRP = '239.255.255.250'
MCAST_PORT = 1900

SSDP_DISCOVER = """M-SEARCH * HTTP/1.1\r
HOST: 239.255.255.250:1900\r
MAN: "ssdp:discover"\r
MX: 2\r
ST: ssdp:all\r
\r
"""

def send_ssdp_discovery():
    """Send SSDP discovery message"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(SSDP_DISCOVER.encode(), (MCAST_GRP, MCAST_PORT))
    return sock

def receive_responses(sock, timeout=5):
    """Receive SSDP responses"""
    sock.settimeout(timeout)
    devices = []

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data, addr = sock.recvfrom(1024)
            response = data.decode('utf-8', errors='ignore')
            devices.append((addr, response))
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error receiving response: {e}")
            break

    return devices

def parse_ssdp_response(response):
    """Parse SSDP response to extract device info"""
    lines = response.split('\n')
    device_info = {}

    for line in lines:
        if ': ' in line:
            key, value = line.split(': ', 1)
            device_info[key.lower()] = value.strip()

    return device_info

def test_device_connectivity(ip, port, path):
    """Test HTTP connectivity to device"""
    try:
        url = f"http://{ip}:{port}{path}"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def discover_upnp_devices():
    """Main UPnP discovery function"""
    print("🔍 Starting UPnP device discovery...")

    sock = send_ssdp_discovery()
    devices = receive_responses(sock, 10)
    sock.close()

    print(f"📡 Found {len(devices)} UPnP responses")

    media_servers = []
    media_renderers = []

    for addr, response in devices:
        ip, _ = addr
        info = parse_ssdp_response(response)

        print(f"\n📱 Device: {ip}")
        print(f"   ST: {info.get('st', 'Unknown')}")
        print(f"   USN: {info.get('usn', 'Unknown')}")
        print(f"   Server: {info.get('server', 'Unknown')}")

        if 'location' in info:
            print(f"   Location: {info['location']}")

            # Test connectivity
            try:
                parsed = urlparse(info['location'])
                if test_device_connectivity(parsed.hostname, parsed.port or 80, parsed.path):
                    print("   ✅ Reachable")
                else:
                    print("   ❌ Not reachable")
            except:
                print("   ❌ Parse error")

        # Categorize devices
        st = info.get('st', '').lower()
        if 'mediaserver' in st:
            media_servers.append((ip, info))
        elif 'mediarenderer' in st or 'tv' in st:
            media_renderers.append((ip, info))

    print(f"\n🎬 Media Servers found: {len(media_servers)}")
    for ip, info in media_servers:
        print(f"   - {ip}: {info.get('friendlyname', 'Unknown')}")

    print(f"\n📺 Media Renderers/TVs found: {len(media_renderers)}")
    for ip, info in media_renderers:
        print(f"   - {ip}: {info.get('friendlyname', 'Unknown')}")

    return media_servers, media_renderers

if __name__ == "__main__":
    discover_upnp_devices()