#!/usr/bin/env python3
"""
Working RTSP Server for Screen Casting
Uses FFmpeg to capture screen and stream via UDP, then serves via simple HTTP/RTSP
"""

import subprocess
import threading
import time
import sys
import signal
import os
import socket
import http.server
import socketserver
from urllib.parse import urlparse

class WorkingRTSPServer:
    def __init__(self, port=8554):
        self.port = port
        self.ffmpeg_process = None
        self.http_server = None
        self.running = False
        self.udp_port = 1234  # Internal UDP port for FFmpeg stream
        
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
    
    def start_ffmpeg_stream(self):
        """Start FFmpeg screen capture to UDP"""
        try:
            if not os.environ.get('DISPLAY'):
                print("Error: No X11 display available")
                return False
                
            local_ip = self.get_local_ip()
            print(f"Starting FFmpeg screen capture to UDP {local_ip}:{self.udp_port}")
            
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
                f'udp://{local_ip}:{self.udp_port}'
            ]
            
            print("Starting FFmpeg stream...")
            self.ffmpeg_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Wait for stream to start
            time.sleep(3)
            
            if self.ffmpeg_process.poll() is None:
                print("✅ FFmpeg stream started successfully!")
                return True
            else:
                print("❌ FFmpeg stream failed to start")
                return False
                
        except Exception as e:
            print(f"Error starting FFmpeg stream: {e}")
            return False
    
    def start_http_server(self):
        """Start HTTP server to serve the stream"""
        try:
            local_ip = self.get_local_ip()
            
            class StreamHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/screen':
                        self.send_response(200)
                        self.send_header('Content-Type', 'video/mp2t')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        # Forward UDP stream to HTTP client
                        try:
                            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            udp_sock.bind(('', 0))
                            udp_sock.connect((local_ip, self.udp_port))
                            
                            while True:
                                data = udp_sock.recv(4096)
                                if not data:
                                    break
                                self.wfile.write(data)
                        except Exception as e:
                            print(f"Stream error: {e}")
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Not Found')
                
                def log_message(self, format, *args):
                    pass  # Suppress HTTP logs
            
            self.http_server = socketserver.TCPServer(('0.0.0.0', self.port), StreamHandler)
            print(f"HTTP server started on port {self.port}")
            return True
            
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
            return False
    
    def start_server(self):
        """Start the complete streaming server"""
        try:
            print("Starting Working RTSP Server...")
            print("=" * 40)
            
            # Start FFmpeg stream
            if not self.start_ffmpeg_stream():
                return False
            
            # Start HTTP server
            if not self.start_http_server():
                return False
            
            local_ip = self.get_local_ip()
            print(f"✅ Server started successfully!")
            print(f"Stream URL: http://{local_ip}:{self.port}/screen")
            print(f"VLC URL: http://{local_ip}:{self.port}/screen")
            print("Press Ctrl+C to stop the server")
            
            self.running = True
            
            # Start HTTP server in a thread
            def run_http_server():
                self.http_server.serve_forever()
            
            http_thread = threading.Thread(target=run_http_server)
            http_thread.daemon = True
            http_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server"""
        self.running = False
        
        if self.ffmpeg_process:
            print("Stopping FFmpeg stream...")
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
        
        if self.http_server:
            print("Stopping HTTP server...")
            self.http_server.shutdown()
        
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