#!/usr/bin/env python3
"""
UDP Streaming Server for Screen Casting
Creates a UDP stream that can be accessed by smart TVs
"""

import subprocess
import threading
import time
import sys
import signal
import os

class UDPStreamingServer:
    def __init__(self, port=1234):
        self.port = port
        self.process = None
        self.running = False
        
    def get_local_ip(self):
        """Get local IP address"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
    
    def start_server(self):
        """Start the UDP streaming server"""
        try:
            # Check if X11 display is available
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            local_ip = self.get_local_ip()
            print(f"Starting UDP streaming server on {local_ip}:{self.port}")
            
            # FFmpeg command for UDP streaming
            cmd = [
                'ffmpeg',
                '-f', 'x11grab',
                '-framerate', '30',
                '-video_size', '1280x720',
                '-i', ':0.0',
                '-f', 'alsa',
                '-i', 'default',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-profile:v', 'baseline',
                '-level', '3.0',
                '-pix_fmt', 'yuv420p',
                '-b:v', '2000k',
                '-maxrate', '2000k',
                '-bufsize', '4000k',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-f', 'mpegts',
                f'udp://{local_ip}:{self.port}'
            ]
            
            print("Starting FFmpeg UDP stream...")
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True
            
            print(f"UDP stream started!")
            print(f"Stream URL: udp://{local_ip}:{self.port}")
            print(f"TV should connect to: udp://192.168.200.44:{self.port}")
            
            # Monitor the process
            def monitor():
                while self.running and self.process:
                    if self.process.poll() is not None:
                        print("FFmpeg process ended unexpectedly")
                        break
                    time.sleep(1)
            
            monitor_thread = threading.Thread(target=monitor)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error starting UDP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the UDP server"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        print("UDP Server stopped")

def signal_handler(sig, frame):
    print("\nShutting down UDP server...")
    if 'server' in globals():
        server.stop_server()
    sys.exit(0)

def main():
    print("UDP Streaming Server for Screen Casting")
    print("======================================")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = UDPStreamingServer()
    
    if server.start_server():
        print("UDP server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start UDP server")
        sys.exit(1)
    
    server.stop_server()

if __name__ == "__main__":
    main()