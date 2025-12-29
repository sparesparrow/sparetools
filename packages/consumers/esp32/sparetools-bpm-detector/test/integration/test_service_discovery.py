#!/usr/bin/env python3
"""
Test Service Discovery Concepts
Validates automatic device detection mechanisms for modular ESP32 BPM system
"""

import socket
import json
import time
import threading
import uuid
from typing import Dict, List, Optional

class MockServiceDiscovery:
    """Mock service discovery implementation"""
    
    def __init__(self, multicast_group: str = "239.0.0.1", port: int = 5353):
        self.multicast_group = multicast_group
        self.port = port
        self.sock = None
        self.services: Dict[str, Dict] = {}
        self.running = False
        
    def start(self):
        """Start service discovery"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        
        try:
            self.sock.bind(("", self.port))
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, 
                               socket.inet_aton(self.multicast_group) + socket.inet_aton("0.0.0.0"))
            self.running = True
            print(f"✅ Service discovery started on {self.multicast_group}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to start service discovery: {e}")
            return False
    
    def stop(self):
        """Stop service discovery"""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None
        print("✅ Service discovery stopped")
    
    def advertise_service(self, service_info: Dict):
        """Advertise a service"""
        service_id = str(uuid.uuid4())
        service_info["service_id"] = service_id
        service_info["timestamp"] = int(time.time() * 1000)
        
        self.services[service_id] = service_info
        
        # Send multicast announcement
        message = {
            "type": "service_announcement",
            "service": service_info
        }
        
        try:
            data = json.dumps(message).encode('utf-8')
            self.sock.sendto(data, (self.multicast_group, self.port))
            print(f"✅ Advertised service: {service_info['name']} ({service_id})")
            return service_id
        except Exception as e:
            print(f"❌ Failed to advertise service: {e}")
            return None
    
    def discover_services(self, timeout: float = 2.0) -> List[Dict]:
        """Discover available services"""
        discovered = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                self.sock.settimeout(0.1)
                data, addr = self.sock.recvfrom(4096)
                message = json.loads(data.decode('utf-8'))
                
                if message.get("type") == "service_announcement":
                    service = message["service"]
                    if service not in discovered:
                        discovered.append(service)
                        print(f"✅ Discovered service: {service['name']} at {addr[0]}:{service.get('port', 'N/A')}")
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Discovery error: {e}")
                break
        
        return discovered

def test_esp32_service_advertisement():
    """Test ESP32 device advertisement"""
    discovery = MockServiceDiscovery()
    
    if not discovery.start():
        return False, "Failed to start discovery service"
    
    try:
        # Advertise ESP32 BPM detector service
        esp32_service = {
            "name": "ESP32 BPM Detector",
            "type": "bpm_detector",
            "capabilities": ["bpm_detection", "fft_analysis", "wifi_api"],
            "api_endpoints": {
                "bpm": "/api/bpm",
                "settings": "/api/settings",
                "health": "/api/health"
            },
            "ip_address": "192.168.1.100",
            "port": 80,
            "firmware_version": "1.0.0",
            "hardware": "ESP32-WROOM-32"
        }
        
        service_id = discovery.advertise_service(esp32_service)
        if not service_id:
            return False, "Failed to advertise ESP32 service"
        
        # Verify service was registered locally
        if service_id not in discovery.services:
            return False, "Service not registered locally"
        
        registered_service = discovery.services[service_id]
        required_fields = ["name", "type", "capabilities", "api_endpoints", "ip_address"]
        
        if not all(field in registered_service for field in required_fields):
            return False, "Service registration missing required fields"
        
        print("✅ ESP32 service advertisement: Successfully registered")
        return True, "ESP32 service advertisement successful"
        
    finally:
        discovery.stop()

def test_client_service_discovery():
    """Test client discovery of ESP32 services"""
    discovery1 = MockServiceDiscovery()
    discovery2 = MockServiceDiscovery()
    
    if not discovery1.start() or not discovery2.start():
        return False, "Failed to start discovery services"
    
    try:
        # Advertise service from discovery1
        esp32_service = {
            "name": "ESP32 BPM Detector #1",
            "type": "bpm_detector",
            "ip_address": "192.168.1.100",
            "port": 80
        }
        
        service_id = discovery1.advertise_service(esp32_service)
        if not service_id:
            return False, "Failed to advertise service"
        
        # Give time for multicast propagation
        time.sleep(0.5)
        
        # Discover services from discovery2
        discovered_services = discovery2.discover_services(timeout=3.0)
        
        if not discovered_services:
            return False, "No services discovered"
        
        # Check if our service was discovered
        found_service = None
        for service in discovered_services:
            if service.get("name") == "ESP32 BPM Detector #1":
                found_service = service
                break
        
        if not found_service:
            return False, "Advertised service not discovered"
        
        # Validate discovered service data
        if found_service.get("ip_address") != "192.168.1.100":
            return False, "Discovered service has incorrect IP"
        
        print("✅ Client service discovery: Successfully discovered ESP32 service")
        return True, f"Discovered {len(discovered_services)} service(s)"
        
    finally:
        discovery1.stop()
        discovery2.stop()

def test_service_metadata_exchange():
    """Test detailed service metadata exchange"""
    discovery = MockServiceDiscovery()
    
    if not discovery.start():
        return False, "Failed to start discovery service"
    
    try:
        # Advertise comprehensive service metadata
        detailed_service = {
            "name": "ESP32 BPM Detector Pro",
            "type": "bpm_detector",
            "version": "1.0.0",
            "capabilities": [
                "bpm_detection",
                "fft_analysis", 
                "envelope_detection",
                "wifi_api",
                "oled_display",
                "midi_output"
            ],
            "api_endpoints": {
                "bpm": {"path": "/api/bpm", "method": "GET"},
                "settings": {"path": "/api/settings", "method": "GET"},
                "health": {"path": "/api/health", "method": "GET"}
            },
            "network_config": {
                "ip_address": "192.168.1.100",
                "port": 80,
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "hostname": "esp32-bpm-001"
            },
            "hardware_specs": {
                "microcontroller": "ESP32-WROOM-32",
                "flash_size": "4MB",
                "psram": "8MB",
                "wifi_standard": "802.11b/g/n",
                "bluetooth": "4.2 + BLE"
            },
            "supported_modules": [
                "bpm-qt-client",
                "bpm-network-server", 
                "bpm-bluetooth",
                "bpm-advanced"
            ]
        }
        
        service_id = discovery.advertise_service(detailed_service)
        if not service_id:
            return False, "Failed to advertise detailed service"
        
        # Validate comprehensive metadata
        registered = discovery.services[service_id]
        
        # Check capabilities
        if "bpm_detection" not in registered["capabilities"]:
            return False, "Missing core BPM capability"
        
        # Check API endpoints structure
        api_endpoints = registered["api_endpoints"]
        if not isinstance(api_endpoints, dict) or "bpm" not in api_endpoints:
            return False, "Invalid API endpoints structure"
        
        # Check network configuration
        network = registered["network_config"]
        if network["ip_address"] != "192.168.1.100":
            return False, "Network configuration incorrect"
        
        # Check hardware specifications
        hardware = registered["hardware_specs"]
        if hardware["microcontroller"] != "ESP32-WROOM-32":
            return False, "Hardware specifications incorrect"
        
        # Check module compatibility
        modules = registered["supported_modules"]
        if "bpm-qt-client" not in modules:
            return False, "Missing module compatibility information"
        
        print("✅ Service metadata exchange: Comprehensive service information validated")
        return True, "Service metadata exchange successful"
        
    finally:
        discovery.stop()

def main():
    """Run all service discovery tests"""
    print("Testing Service Discovery Concepts...")
    print("=" * 50)
    
    tests = [
        ("ESP32 Service Advertisement", test_esp32_service_advertisement),
        ("Client Service Discovery", test_client_service_discovery),
        ("Service Metadata Exchange", test_service_metadata_exchange)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        success, message = test_func()
        results.append((test_name, success, message))
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {message}")
    
    print("\n" + "=" * 50)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Service discovery concepts: All tests passed")
        return True
    else:
        print("❌ Service discovery concepts: Some tests failed")
        return False

if __name__ == '__main__':
    main()
