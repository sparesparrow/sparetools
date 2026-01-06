#!/usr/bin/env python3
"""
Monitor for Google Cast services becoming available during active casting
"""

import requests
import time
import subprocess
import threading

class CastMonitor:
    def __init__(self):
        self.monitoring = False
        self.found_services = []

    def speak(self, message):
        """Voice alerts"""
        try:
            subprocess.run(['spd-say', message], check=True)
        except:
            pass

    def test_cast_endpoint(self, url, name):
        """Test if a Cast endpoint is now available"""
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True, response
        except:
            pass
        return False, None

    def monitor_cast_services(self, duration=120):
        """Monitor for Cast services becoming available"""
        print(f"🔍 Monitoring for Cast services for {duration} seconds...")
        self.speak("Starting Cast service monitoring. Begin casting from YouTube app now")

        cast_urls = [
            ("http://192.168.200.44:8008/setup", "TV Cast Setup"),
            ("http://192.168.200.44:8008/receiver/status", "TV Receiver Status"),
            ("http://192.168.200.84:8008/setup", "Android Cast Setup"),
        ]

        start_time = time.time()
        check_interval = 2  # Check every 2 seconds

        while time.time() - start_time < duration:
            for url, name in cast_urls:
                available, response = self.test_cast_endpoint(url, name)
                if available and url not in self.found_services:
                    print(f"\n🎉 CAST SERVICE FOUND: {name}")
                    print(f"   URL: {url}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                    if len(response.text) < 300:
                        print(f"   Response: {response.text}")

                    self.found_services.append(url)
                    self.speak(f"Cast service now available: {name}")

            remaining = int(duration - (time.time() - start_time))
            print(f"⏱️  Monitoring... {remaining}s remaining (Found: {len(self.found_services)} services)", end='\r')
            time.sleep(check_interval)

        print(f"\n✅ Monitoring complete. Found {len(self.found_services)} Cast services")
        self.speak(f"Monitoring complete. Found {len(self.found_services)} Cast services")

        return self.found_services

def main():
    monitor = CastMonitor()
    services = monitor.monitor_cast_services()

    if services:
        print("\n🎯 ACTIVE CAST SERVICES FOUND:")
        for service in services:
            print(f"   ✓ {service}")
    else:
        print("\n❌ No Cast services became available during monitoring")
        print("   Possible reasons:")
        print("   - TV doesn't support Google Cast")
        print("   - Casting not initiated properly")
        print("   - Different protocol used (DLNA, Miracast, etc.)")

if __name__ == "__main__":
    main()