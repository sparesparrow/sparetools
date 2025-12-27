#!/usr/bin/env python3
"""
HLS Client Test
Test HLS stream connectivity and quality
"""

import requests
import time
import sys
import json
from urllib.parse import urljoin

class HLSClientTest:
    def __init__(self, hls_url):
        self.hls_url = hls_url
        self.base_url = '/'.join(hls_url.split('/')[:-1]) + '/'
        self.running = False
        self.segment_count = 0
        self.start_time = 0
        
    def test_playlist(self):
        """Test HLS playlist accessibility"""
        try:
            print(f"Testing HLS playlist: {self.hls_url}")
            response = requests.get(self.hls_url, timeout=10)
            
            if response.status_code == 200:
                print("✓ Playlist accessible")
                print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"Content-Length: {len(response.content)} bytes")
                return True
            else:
                print(f"✗ Playlist error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Playlist error: {e}")
            return False
    
    def test_segments(self, duration=30):
        """Test HLS segments for specified duration"""
        if not self.test_playlist():
            return False
            
        self.running = True
        self.start_time = time.time()
        self.segment_count = 0
        
        print(f"Testing segments for {duration} seconds...")
        
        try:
            while self.running and (time.time() - self.start_time) < duration:
                # Get current playlist
                response = requests.get(self.hls_url, timeout=5)
                if response.status_code == 200:
                    playlist_content = response.text
                    segments = [line.strip() for line in playlist_content.split('\n') 
                              if line.strip().endswith('.ts')]
                    
                    if segments:
                        self.segment_count = len(segments)
                        print(f"Segments available: {self.segment_count}")
                        
                        # Test latest segment
                        latest_segment = segments[-1]
                        segment_url = urljoin(self.base_url, latest_segment)
                        
                        try:
                            seg_response = requests.head(segment_url, timeout=5)
                            if seg_response.status_code == 200:
                                print(f"✓ Latest segment accessible: {latest_segment}")
                            else:
                                print(f"✗ Segment error: HTTP {seg_response.status_code}")
                        except Exception as e:
                            print(f"✗ Segment error: {e}")
                    else:
                        print("No segments found in playlist")
                else:
                    print(f"Playlist error: HTTP {response.status_code}")
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            
        finally:
            self.stop_test()
            
        return True
    
    def stop_test(self):
        """Stop the test"""
        self.running = False
        
        if self.start_time > 0:
            elapsed = time.time() - self.start_time
            print(f"\nTest completed:")
            print(f"Total time: {elapsed:.2f} seconds")
            print(f"Segments found: {self.segment_count}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 hls_client_test.py <hls_url>")
        print("Example: python3 hls_client_test.py http://192.168.200.44:8080/hls/screen.m3u8")
        sys.exit(1)
    
    hls_url = sys.argv[1]
    
    print("HLS Client Test")
    print("===============")
    
    client = HLSClientTest(hls_url)
    client.test_segments(30)

if __name__ == "__main__":
    main()