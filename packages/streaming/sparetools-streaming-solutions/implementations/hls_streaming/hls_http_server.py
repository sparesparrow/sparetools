#!/usr/bin/env python3
"""
HLS HTTP Server for Screen Casting
Serves HLS playlist and segments via HTTP
"""

from flask import Flask, send_file, Response
from flask_cors import CORS
import os
import time
import threading
import json

app = Flask(__name__)
CORS(app)

# Configuration
HLS_DIR = "/var/lib/hls-server"
PLAYLIST_FILE = os.path.join(HLS_DIR, "screen.m3u8")
PORT = 8080

class HLSMonitor:
    def __init__(self):
        self.last_modified = 0
        self.segments = []
        self.monitoring = False
        
    def start_monitoring(self):
        """Start monitoring HLS directory for changes"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def _monitor_loop(self):
        """Monitor loop for HLS directory changes"""
        while self.monitoring:
            try:
                if os.path.exists(PLAYLIST_FILE):
                    current_modified = os.path.getmtime(PLAYLIST_FILE)
                    if current_modified > self.last_modified:
                        self.last_modified = current_modified
                        self._update_segments()
                        print(f"HLS playlist updated at {time.ctime()}")
                time.sleep(1)
            except Exception as e:
                print(f"Error monitoring HLS: {e}")
                time.sleep(5)
    
    def _update_segments(self):
        """Update segment list from playlist"""
        try:
            with open(PLAYLIST_FILE, 'r') as f:
                content = f.read()
                self.segments = [line.strip() for line in content.split('\n') if line.endswith('.ts')]
        except Exception as e:
            print(f"Error reading playlist: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

# Global monitor instance
hls_monitor = HLSMonitor()

@app.route('/')
def index():
    """Main page with stream information"""
    return f"""
    <html>
    <head><title>HLS Screen Stream</title></head>
    <body>
        <h1>HLS Screen Stream</h1>
        <p>Stream URL: <a href="/hls/screen.m3u8">http://{get_local_ip()}:{PORT}/hls/screen.m3u8</a></p>
        <p>Status: {'Active' if os.path.exists(PLAYLIST_FILE) else 'Inactive'}</p>
        <p>Segments: {len(hls_monitor.segments)}</p>
        <p>Last Updated: {time.ctime(hls_monitor.last_modified) if hls_monitor.last_modified else 'Never'}</p>
    </body>
    </html>
    """

@app.route('/hls/<path:filename>')
def serve_hls(filename):
    """Serve HLS playlist and segments"""
    file_path = os.path.join(HLS_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Set appropriate headers for HLS
    if filename.endswith('.m3u8'):
        return send_file(file_path, mimetype='application/vnd.apple.mpegurl')
    elif filename.endswith('.ts'):
        return send_file(file_path, mimetype='video/mp2t')
    else:
        return send_file(file_path)

@app.route('/status')
def status():
    """API endpoint for stream status"""
    return {
        'active': os.path.exists(PLAYLIST_FILE),
        'segments': len(hls_monitor.segments),
        'last_modified': hls_monitor.last_modified,
        'playlist_url': f"http://{get_local_ip()}:{PORT}/hls/screen.m3u8"
    }

def get_local_ip():
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

def main():
    print("Starting HLS HTTP Server...")
    print(f"Server will run on http://{get_local_ip()}:{PORT}")
    print(f"HLS stream: http://{get_local_ip()}:{PORT}/hls/screen.m3u8")
    
    # Start monitoring
    hls_monitor.start_monitoring()
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        hls_monitor.stop_monitoring()

if __name__ == "__main__":
    main()