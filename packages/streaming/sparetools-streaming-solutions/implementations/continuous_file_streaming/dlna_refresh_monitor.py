#!/usr/bin/env python3
"""
DLNA Refresh Monitor
Monitors and manages DLNA refreshes for continuous streaming
"""

import time
import subprocess
import os
import json
import threading
from datetime import datetime

class DLNARefreshMonitor:
    def __init__(self, stream_dir="/var/lib/continuous-stream", stream_file="live_screen.mp4"):
        self.stream_dir = stream_dir
        self.stream_file = stream_file
        self.target_file = os.path.join(stream_dir, stream_file)
        self.monitoring = False
        self.last_modified = 0
        self.refresh_count = 0
        self.error_count = 0
        
    def start_monitoring(self):
        """Start monitoring file changes and DLNA refreshes"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        print(f"DLNA Refresh Monitor started for {self.target_file}")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                if os.path.exists(self.target_file):
                    current_modified = os.path.getmtime(self.target_file)
                    if current_modified > self.last_modified:
                        self.last_modified = current_modified
                        self._refresh_dlna()
                        self.refresh_count += 1
                        print(f"DLNA refreshed - Count: {self.refresh_count}")
                time.sleep(1)
            except Exception as e:
                self.error_count += 1
                print(f"Monitor error: {e} - Count: {self.error_count}")
                time.sleep(5)
    
    def _refresh_dlna(self):
        """Force DLNA rescan"""
        try:
            # Restart MiniDLNA service
            subprocess.run(['sudo', 'systemctl', 'restart', 'minidlna'], 
                         check=True, capture_output=True)
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"DLNA refresh failed: {e}")
            self.error_count += 1
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'monitoring': self.monitoring,
            'file_exists': os.path.exists(self.target_file),
            'last_modified': self.last_modified,
            'refresh_count': self.refresh_count,
            'error_count': self.error_count,
            'file_size': os.path.getsize(self.target_file) if os.path.exists(self.target_file) else 0
        }
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        print("DLNA Refresh Monitor stopped")

def main():
    print("Starting DLNA Refresh Monitor...")
    
    monitor = DLNARefreshMonitor()
    monitor.start_monitoring()
    
    try:
        while True:
            status = monitor.get_status()
            print(f"Status: {json.dumps(status, indent=2)}")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()