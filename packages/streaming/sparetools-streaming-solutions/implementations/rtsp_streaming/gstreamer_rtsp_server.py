#!/usr/bin/env python3
"""
GStreamer RTSP Server for Real-Time Screen Casting
Provides RTSP stream of desktop screen capture
"""

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
import threading
import time
import sys
import os

class RTSPScreenServer:
    def __init__(self, port=8554):
        Gst.init(None)
        self.port = port
        self.server = None
        self.loop = None
        self.running = False
        
    def create_pipeline(self):
        """Create GStreamer pipeline for screen capture and RTSP streaming"""
        pipeline_str = (
            "ximagesrc ! "
            "video/x-raw,framerate=25/1,width=1280,height=720 ! "
            "videoconvert ! "
            "x264enc bitrate=2000 tune=zerolatency profile=baseline ! "
            "rtph264pay name=pay0 pt=96"
        )
        
        return Gst.parse_launch(pipeline_str)
    
    def start_server(self):
        """Start the RTSP server"""
        try:
            # Create RTSP server
            self.server = GstRtspServer.RTSPServer()
            self.server.set_property('service', str(self.port))
            
            # Create media factory
            factory = GstRtspServer.RTSPMediaFactory()
            factory.set_launch("ximagesrc ! video/x-raw,framerate=25/1,width=1280,height=720 ! videoconvert ! x264enc bitrate=2000 tune=zerolatency profile=baseline ! rtph264pay name=pay0 pt=96")
            factory.set_shared(True)
            
            # Add factory to server
            self.server.get_mount_points().add_factory("/screen", factory)
            
            # Start server
            self.server.attach(None)
            
            print(f"RTSP Server started on port {self.port}")
            print(f"Stream URL: rtsp://{self.get_local_ip()}:{self.port}/screen")
            
            self.running = True
            
            # Start main loop
            self.loop = GLib.MainLoop()
            self.loop.run()
            
        except Exception as e:
            print(f"Error starting RTSP server: {e}")
            sys.exit(1)
    
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
    
    def stop_server(self):
        """Stop the RTSP server"""
        if self.loop:
            self.loop.quit()
        self.running = False
        print("RTSP Server stopped")

def main():
    print("Starting GStreamer RTSP Screen Server...")
    
    # Check if X11 display is available
    import os
    if not os.environ.get('DISPLAY'):
        print("Error: No X11 display available")
        sys.exit(1)
    
    server = RTSPScreenServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop_server()

if __name__ == "__main__":
    main()