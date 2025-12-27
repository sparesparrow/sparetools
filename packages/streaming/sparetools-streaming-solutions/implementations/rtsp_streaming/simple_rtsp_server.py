#!/usr/bin/env python3
"""
Simple RTSP Server using FFmpeg subprocess
Creates an RTSP server by running FFmpeg in a subprocess
"""

import subprocess
import threading
import time
import sys
import signal
import os

class SimpleRTSPServer:
    def __init__(self, port=8554):
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
        """Start the RTSP server using FFmpeg"""
        try:
            # Check if X11 display is available
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            local_ip = self.get_local_ip()
            print(f"Starting RTSP server on {local_ip}:{self.port}")
            print(f"Stream URL: rtsp://{local_ip}:{self.port}/screen")
            
            # FFmpeg command for RTSP server
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
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                f'rtsp://0.0.0.0:{self.port}/screen'
            ]
            
            print("Starting FFmpeg RTSP server...")
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True
            
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
            print(f"Error starting RTSP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the RTSP server"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        print("RTSP Server stopped")

def signal_handler(sig, frame):
    print("\nShutting down RTSP server...")
    if 'server' in globals():
        server.stop_server()
    sys.exit(0)

def main():
    print("Simple RTSP Server for Screen Casting")
    print("=====================================")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = SimpleRTSPServer()
    
    if server.start_server():
        print("RTSP server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start RTSP server")
        sys.exit(1)
    
    server.stop_server()

if __name__ == "__main__":
    main()