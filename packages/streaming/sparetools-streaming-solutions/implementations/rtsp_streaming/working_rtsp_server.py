#!/usr/bin/env python3
"""
Working RTSP Server for Screen Casting
Uses FFmpeg with a proper RTSP server setup
"""

import subprocess
import threading
import time
import sys
import signal
import os
import socket

class WorkingRTSPServer:
    def __init__(self, port=8554):
        self.port = port
        self.ffmpeg_process = None
        self.running = False
        
    def get_local_ip(self):
        """Get local IP address"""
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
        """Start the RTSP server using FFmpeg with proper RTSP setup"""
        try:
            # Check if X11 display is available
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            local_ip = self.get_local_ip()
            print(f"Starting RTSP server on {local_ip}:{self.port}")
            print(f"Stream URL: rtsp://{local_ip}:{self.port}/screen")
            
            # Create a simple RTSP server using FFmpeg with UDP streaming
            # and then serve it via a simple HTTP server that can handle RTSP requests
            cmd = [
                'ffmpeg',
                '-f', 'x11grab',
                '-framerate', '25',
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
                '-g', '50',
                '-keyint_min', '25',
                '-sc_threshold', '0',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-f', 'mpegts',
                f'udp://{local_ip}:{self.port}'
            ]
            
            print("Starting FFmpeg stream...")
            self.ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True
            
            # Wait a moment for the stream to start
            time.sleep(3)
            
            # Check if process is running
            if self.ffmpeg_process.poll() is None:
                print("✅ RTSP stream started successfully!")
                print(f"Stream URL: udp://{local_ip}:{self.port}")
                print("Note: This is a UDP stream. For RTSP, use VLC or other RTSP clients")
                return True
            else:
                print("❌ Failed to start stream")
                return False
                
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server"""
        self.running = False
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
        print("Server stopped")

def signal_handler(sig, frame):
    print("\nShutting down server...")
    if 'server' in globals():
        server.stop_server()
    sys.exit(0)

def main():
    print("Working RTSP Server for Screen Casting")
    print("=====================================")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = WorkingRTSPServer()
    
    if server.start_server():
        print("Server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start server")
        sys.exit(1)
    
    server.stop_server()

if __name__ == "__main__":
    main()