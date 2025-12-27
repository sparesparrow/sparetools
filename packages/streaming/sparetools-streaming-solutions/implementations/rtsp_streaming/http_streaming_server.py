#!/usr/bin/env python3
"""
HTTP Streaming Server for Screen Casting
Creates an HTTP stream that can be accessed by smart TVs
"""

import subprocess
import threading
import time
import sys
import signal
import os
import http.server
import socketserver
from urllib.parse import urlparse

class HTTPStreamingServer:
    def __init__(self, port=8080):
        self.port = port
        self.ffmpeg_process = None
        self.http_server = None
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
    
    def start_ffmpeg_stream(self):
        """Start FFmpeg to create the stream"""
        try:
            # Check if X11 display is available
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            print("Starting FFmpeg screen capture...")
            
            # FFmpeg command for HTTP streaming
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
                'http://localhost:8080/screen'
            ]
            
            self.ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
            
        except Exception as e:
            print(f"Error starting FFmpeg: {e}")
            return False
    
    def start_http_server(self):
        """Start HTTP server to serve the stream"""
        try:
            class StreamHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/screen':
                        self.send_response(200)
                        self.send_header('Content-Type', 'video/mp2t')
                        self.send_header('Cache-Control', 'no-cache')
                        self.send_header('Connection', 'close')
                        self.end_headers()
                        
                        # Stream the FFmpeg output
                        if self.server.ffmpeg_process:
                            try:
                                for chunk in iter(lambda: self.server.ffmpeg_process.stdout.read(4096), b""):
                                    self.wfile.write(chunk)
                            except:
                                pass
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    pass  # Suppress default logging
            
            self.http_server = socketserver.TCPServer(("", self.port), StreamHandler)
            self.http_server.ffmpeg_process = self.ffmpeg_process
            
            print(f"HTTP server started on port {self.port}")
            return True
            
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
            return False
    
    def start_server(self):
        """Start both FFmpeg and HTTP server"""
        if not self.start_ffmpeg_stream():
            return False
            
        time.sleep(2)  # Give FFmpeg time to start
        
        if not self.start_http_server():
            return False
            
        self.running = True
        local_ip = self.get_local_ip()
        print(f"Streaming server started!")
        print(f"Stream URL: http://{local_ip}:{self.port}/screen")
        print(f"TV URL: http://192.168.200.44:8080/screen")
        
        return True
    
    def stop_server(self):
        """Stop the streaming server"""
        self.running = False
        
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
                
        if self.http_server:
            self.http_server.shutdown()
            
        print("Streaming server stopped")

def signal_handler(sig, frame):
    print("\nShutting down streaming server...")
    if 'server' in globals():
        server.stop_server()
    sys.exit(0)

def main():
    print("HTTP Streaming Server for Screen Casting")
    print("=======================================")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server = HTTPStreamingServer()
    
    if server.start_server():
        print("Streaming server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start streaming server")
        sys.exit(1)
    
    server.stop_server()

if __name__ == "__main__":
    main()