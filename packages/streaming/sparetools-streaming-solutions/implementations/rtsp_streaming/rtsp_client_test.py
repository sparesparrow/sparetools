#!/usr/bin/env python3
"""
RTSP Client Test
Test RTSP stream connectivity and quality
"""

import cv2
import sys
import time
import threading

class RTSPClientTest:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self.running = False
        self.frame_count = 0
        self.start_time = 0
        
    def connect(self):
        """Connect to RTSP stream"""
        try:
            print(f"Connecting to RTSP stream: {self.rtsp_url}")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if not self.cap.isOpened():
                print("Error: Could not open RTSP stream")
                return False
                
            print("Successfully connected to RTSP stream")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def test_stream(self, duration=30):
        """Test stream for specified duration"""
        if not self.connect():
            return False
            
        self.running = True
        self.start_time = time.time()
        self.frame_count = 0
        
        print(f"Testing stream for {duration} seconds...")
        
        try:
            while self.running and (time.time() - self.start_time) < duration:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_count += 1
                    if self.frame_count % 30 == 0:  # Print every 30 frames
                        elapsed = time.time() - self.start_time
                        fps = self.frame_count / elapsed
                        print(f"Frames: {self.frame_count}, FPS: {fps:.2f}, Elapsed: {elapsed:.1f}s")
                else:
                    print("Warning: Failed to read frame")
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            
        finally:
            self.stop_test()
            
        return True
    
    def stop_test(self):
        """Stop the test"""
        self.running = False
        if self.cap:
            self.cap.release()
        
        if self.start_time > 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            print(f"\nTest completed:")
            print(f"Total frames: {self.frame_count}")
            print(f"Total time: {elapsed:.2f} seconds")
            print(f"Average FPS: {fps:.2f}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 rtsp_client_test.py <rtsp_url>")
        print("Example: python3 rtsp_client_test.py rtsp://192.168.200.44:8554/screen")
        sys.exit(1)
    
    rtsp_url = sys.argv[1]
    
    print("RTSP Client Test")
    print("================")
    
    client = RTSPClientTest(rtsp_url)
    client.test_stream(30)

if __name__ == "__main__":
    main()