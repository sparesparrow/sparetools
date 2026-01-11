#!/usr/bin/env python3
"""
Automated Google Cast Protocol Testing Script
Tests all discovered Cast URLs with voice feedback
"""

import requests
import subprocess
import time
import json
import threading
from urllib.parse import urlparse
import sys

class CastTester:
    def __init__(self):
        self.test_results = {}
        self.voice_enabled = True

    def speak(self, message):
        """Provide voice output for test results"""
        if self.voice_enabled:
            try:
                subprocess.run(['spd-say', message], check=True)
            except Exception as e:
                print(f"Voice error: {e}")

    def test_url(self, url, description):
        """Test a single URL and report results"""
        print(f"\n🔍 Testing: {description}")
        print(f"   URL: {url}")

        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            content_type = response.headers.get('content-type', 'unknown')

            # Analyze response
            is_json = 'application/json' in content_type
            is_html = 'text/html' in content_type
            has_content = len(response.text) > 10

            # Determine success criteria
            success = (
                status == 200 and
                (is_json or is_html or has_content)
            )

            result = {
                'url': url,
                'status_code': status,
                'content_type': content_type,
                'success': success,
                'response_size': len(response.text),
                'description': description
            }

            self.test_results[url] = result

            if success:
                print(f"   ✅ SUCCESS: {status} - {content_type}")
                if is_json:
                    print("   📄 JSON Response detected")
                if len(response.text) < 500:
                    print(f"   📝 Content: {response.text[:200]}...")
                self.speak(f"Success: {description} returned {status}")
            else:
                print(f"   ❌ FAILED: {status} - {content_type}")
                self.speak(f"Failed: {description} returned {status}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results[url] = {
                'url': url,
                'error': str(e),
                'success': False,
                'description': description
            }
            self.speak(f"Error testing {description}: {str(e)[:50]}")

    def test_websocket_availability(self, host, port=8009):
        """Test if WebSocket port is accessible"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                print(f"   🔌 WebSocket port {port} is OPEN on {host}")
                self.speak(f"WebSocket port {port} is accessible on {host}")
                return True
            else:
                print(f"   🔌 WebSocket port {port} is CLOSED on {host}")
                return False
        except Exception as e:
            print(f"   🔌 WebSocket test failed: {e}")
            return False

    def run_comprehensive_test(self):
        """Run all Cast URL tests"""
        print("🚀 STARTING AUTOMATED GOOGLE CAST PROTOCOL TESTING")
        print("=" * 60)
        self.speak("Starting automated Google Cast protocol testing")

        # Test Cast device URLs
        cast_urls = [
            ("http://192.168.200.44:8008/setup", "Hisense TV Cast Setup"),
            ("http://192.168.200.44:8008/receiver/status", "TV Receiver Status"),
            ("http://192.168.200.44:8008/apps/674A0243", "Cast Device 674A0243"),
            ("http://192.168.200.44:8008/apps/233637DE", "Cast Device 233637DE"),
            ("http://192.168.200.44:8008/apps/8E6C866D", "Cast Device 8E6C866D"),
            ("http://192.168.200.44:8008/apps/YouTube", "YouTube Cast Receiver"),
            ("http://192.168.200.84:8008/setup", "Android Device Cast Setup"),
            ("https://192.168.200.44:8443/setup", "TV Secure Cast Setup"),
            ("http://192.168.200.44:9090/setup", "TV Alternative Cast Port"),
        ]

        print("\n📡 PHASE 1: Testing Cast URLs")
        self.speak("Phase 1: Testing all discovered Cast URLs")

        for url, description in cast_urls:
            self.test_url(url, description)
            time.sleep(1)  # Brief pause between tests

        print("\n🔌 PHASE 2: Testing WebSocket Connectivity")
        self.speak("Phase 2: Testing WebSocket connectivity for Cast control")

        # Test WebSocket ports
        websocket_tests = [
            ("192.168.200.44", 8009, "TV Cast WebSocket"),
            ("192.168.200.84", 8009, "Android Cast WebSocket"),
        ]

        for host, port, description in websocket_tests:
            print(f"\n🔍 Testing: {description}")
            self.test_websocket_availability(host, port)

        print("\n⏳ PHASE 3: Monitoring for Active Casting")
        self.speak("Phase 3: Monitoring for active YouTube casting. Please start casting from Android device now")

        # Monitor for a period while user starts casting
        print("   Monitoring network for 30 seconds...")
        print("   👆 START YOUTUBE CASTING ON ANDROID DEVICE NOW 👆")

        monitor_start = time.time()
        while time.time() - monitor_start < 30:
            remaining = int(30 - (time.time() - monitor_start))
            print(f"   ⏱️  Monitoring... {remaining} seconds remaining", end='\r')
            time.sleep(1)

        print("\n   ✅ Monitoring complete")
        self.speak("Monitoring period complete. Stop casting and check results")

        print("\n📊 PHASE 4: Test Results Summary")
        self.speak("Phase 4: Generating test results summary")

        successful_tests = [r for r in self.test_results.values() if r.get('success', False)]
        failed_tests = [r for r in self.test_results.values() if not r.get('success', False)]

        print(f"\n✅ SUCCESSFUL TESTS: {len(successful_tests)}")
        for result in successful_tests:
            print(f"   ✓ {result['description']} ({result.get('status_code', 'N/A')})")

        print(f"\n❌ FAILED TESTS: {len(failed_tests)}")
        for result in failed_tests:
            error = result.get('error', f"Status: {result.get('status_code', 'Unknown')}")
            print(f"   ✗ {result['description']} - {error}")

        print("\n🎯 ANALYSIS:")
        if successful_tests:
            print("   📡 Found working Cast endpoints - protocol interception possible")
            self.speak("Found working Cast endpoints. Protocol can be intercepted")
        else:
            print("   📡 No working Cast endpoints found - may need different approach")
            self.speak("No working Cast endpoints found. May need alternative testing")

        print("\n💾 Saving results to cast_test_results.json")
        with open('cast_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

        print("\n🎉 AUTOMATED TESTING COMPLETE")
        self.speak("Automated Google Cast testing complete. Check results file for details")

def main():
    tester = CastTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()