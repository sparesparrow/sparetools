#!/usr/bin/env python3
"""
VLC-compatible RTSP Server for Screen Casting
Uses FFmpeg to create a proper RTSP stream that VLC can connect to
"""

import subprocess
import threading
import time
import sys
import signal
import os
import socket

class VLCRTSPServer:
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
        """Start the RTSP server using FFmpeg with proper RTSP output"""
        try:
            # Check if X11 display is available
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            local_ip = self.get_local_ip()
            print(f"Starting VLC-compatible RTSP server on {local_ip}:{self.port}")
            print(f"Stream URL: rtsp://{local_ip}:{self.port}/screen")
            
            # Create a simple RTSP server using FFmpeg with TCP transport
            # This creates a proper RTSP stream that VLC can connect to
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
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                f'rtsp://0.0.0.0:{self.port}/screen'
            ]
            
            print("Starting FFmpeg RTSP server...")
            print(f"Command: {' '.join(cmd)}")
            
            # Start the process
            self.ffmpeg_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.running = True
            
            # Monitor the process output
            def monitor_output():
                for line in iter(self.ffmpeg_process.stdout.readline, ''):
                    if line:
                        print(f"FFmpeg: {line.strip()}")
                        if "rtsp://" in line.lower() and "listening" in line.lower():
                            print("✅ RTSP server is ready!")
            
            monitor_thread = threading.Thread(target=monitor_output)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Wait for the server to start
            time.sleep(5)
            
            # Check if process is still running
            if self.ffmpeg_process.poll() is None:
                print("✅ RTSP server started successfully!")
                print(f"Connect VLC to: rtsp://{local_ip}:{self.port}/screen")
                return True
            else:
                print("❌ RTSP server failed to start")
                return False
                
        except Exception as e:
            print(f"Error starting RTSP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the RTSP server"""
        self.running = False
        if self.ffmpeg_process:
            print("Stopping RTSP server...")
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing RTSP server...")
                self.ffmpeg_process.kill()
        print("RTSP Server stopped")

def signal_handler(sig, frame):
    print("\nShutting down RTSP server...")
    if 'server' in globals():
        server.stop_server()
    sys.exit(0)

def main():
    print("VLC-Compatible RTSP Server for Screen Casting")
    print("=============================================")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = VLCRTSPServer()
    
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