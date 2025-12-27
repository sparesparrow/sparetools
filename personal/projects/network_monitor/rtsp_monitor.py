#!/usr/bin/env python3
"""
RTSP Stream Monitor
Monitors RTSP stream quality, latency, and performance
"""

import time
import subprocess
import threading
import json
import psutil
from datetime import datetime

class RTSPMonitor:
    def __init__(self, rtsp_url, monitor_interval=5):
        self.rtsp_url = rtsp_url
        self.monitor_interval = monitor_interval
        self.monitoring = False
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_frames': 0,
            'dropped_frames': 0,
            'latency_samples': [],
            'bitrate_samples': [],
            'cpu_usage': [],
            'memory_usage': [],
            'errors': []
        }
    
    def start_monitoring(self):
        """Start monitoring the RTSP stream"""
        print(f"🎬 Starting RTSP stream monitoring")
        print(f"📺 Stream: {self.rtsp_url}")
        print(f"⏱️  Interval: {self.monitor_interval}s")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        self.monitoring = True
        self.stats['start_time'] = datetime.now()
        
        try:
            while self.monitoring:
                self.collect_stats()
                self.display_stats()
                time.sleep(self.monitor_interval)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.stats['end_time'] = datetime.now()
        print("\n🛑 Monitoring stopped")
        self.show_summary()
    
    def collect_stats(self):
        """Collect stream statistics"""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            self.stats['cpu_usage'].append(cpu_percent)
            self.stats['memory_usage'].append(memory_percent)
            
            # Get stream stats using ffprobe
            self.get_stream_stats()
            
        except Exception as e:
            self.stats['errors'].append(f"Error collecting stats: {e}")
    
    def get_stream_stats(self):
        """Get stream statistics using ffprobe"""
        try:
            # Get stream info
            cmd = [
                'ffprobe', '-v', 'quiet', '-rtsp_transport', 'tcp',
                '-i', self.rtsp_url, '-show_entries', 'format=duration,bit_rate',
                '-of', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                format_info = data.get('format', {})
                
                # Extract bitrate
                bitrate = format_info.get('bit_rate')
                if bitrate:
                    self.stats['bitrate_samples'].append(int(bitrate))
                
                # Calculate latency (simplified)
                duration = format_info.get('duration')
                if duration:
                    latency = time.time() - float(duration)
                    self.stats['latency_samples'].append(latency)
            
        except Exception as e:
            self.stats['errors'].append(f"Error getting stream stats: {e}")
    
    def display_stats(self):
        """Display current statistics"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Calculate averages
        avg_cpu = sum(self.stats['cpu_usage'][-10:]) / len(self.stats['cpu_usage'][-10:]) if self.stats['cpu_usage'] else 0
        avg_memory = sum(self.stats['memory_usage'][-10:]) / len(self.stats['memory_usage'][-10:]) if self.stats['memory_usage'] else 0
        avg_bitrate = sum(self.stats['bitrate_samples'][-10:]) / len(self.stats['bitrate_samples'][-10:]) if self.stats['bitrate_samples'] else 0
        avg_latency = sum(self.stats['latency_samples'][-10:]) / len(self.stats['latency_samples'][-10:]) if self.stats['latency_samples'] else 0
        
        # Clear screen and show stats
        print(f"\033[2J\033[H")  # Clear screen
        print(f"🎬 RTSP Stream Monitor - {current_time}")
        print("=" * 50)
        print(f"📺 Stream: {self.rtsp_url}")
        print(f"⏱️  Duration: {self.get_duration()}")
        print()
        
        print("📊 Current Stats:")
        print(f"  CPU Usage: {avg_cpu:.1f}%")
        print(f"  Memory Usage: {avg_memory:.1f}%")
        print(f"  Bitrate: {avg_bitrate/1000:.0f} kbps" if avg_bitrate > 0 else "  Bitrate: N/A")
        print(f"  Latency: {avg_latency:.2f}s" if avg_latency > 0 else "  Latency: N/A")
        print()
        
        print("📈 Trends (last 10 samples):")
        print(f"  CPU: {self.get_trend(self.stats['cpu_usage'][-10:])}")
        print(f"  Memory: {self.get_trend(self.stats['memory_usage'][-10:])}")
        print(f"  Bitrate: {self.get_trend(self.stats['bitrate_samples'][-10:])}")
        print()
        
        if self.stats['errors']:
            print(f"❌ Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][-3:]:  # Show last 3 errors
                print(f"  {error}")
            print()
    
    def get_trend(self, values):
        """Get trend indicator for values"""
        if len(values) < 2:
            return "N/A"
        
        if values[-1] > values[0]:
            return "📈 Rising"
        elif values[-1] < values[0]:
            return "📉 Falling"
        else:
            return "➡️  Stable"
    
    def get_duration(self):
        """Get monitoring duration"""
        if not self.stats['start_time']:
            return "0s"
        
        duration = datetime.now() - self.stats['start_time']
        return str(duration).split('.')[0]
    
    def show_summary(self):
        """Show monitoring summary"""
        print("\n📊 Monitoring Summary")
        print("=" * 20)
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            print(f"Duration: {duration}")
        
        if self.stats['cpu_usage']:
            avg_cpu = sum(self.stats['cpu_usage']) / len(self.stats['cpu_usage'])
            max_cpu = max(self.stats['cpu_usage'])
            print(f"CPU Usage: {avg_cpu:.1f}% (max: {max_cpu:.1f}%)")
        
        if self.stats['memory_usage']:
            avg_memory = sum(self.stats['memory_usage']) / len(self.stats['memory_usage'])
            max_memory = max(self.stats['memory_usage'])
            print(f"Memory Usage: {avg_memory:.1f}% (max: {max_memory:.1f}%)")
        
        if self.stats['bitrate_samples']:
            avg_bitrate = sum(self.stats['bitrate_samples']) / len(self.stats['bitrate_samples'])
            print(f"Average Bitrate: {avg_bitrate/1000:.0f} kbps")
        
        if self.stats['latency_samples']:
            avg_latency = sum(self.stats['latency_samples']) / len(self.stats['latency_samples'])
            print(f"Average Latency: {avg_latency:.2f}s")
        
        if self.stats['errors']:
            print(f"Total Errors: {len(self.stats['errors'])}")
        
        print()
    
    def save_stats(self, filename="rtsp_monitor_stats.json"):
        """Save monitoring statistics to file"""
        stats_data = {
            'rtsp_url': self.rtsp_url,
            'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
            'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None,
            'duration': str(self.stats['end_time'] - self.stats['start_time']) if self.stats['start_time'] and self.stats['end_time'] else None,
            'stats': self.stats
        }
        
        with open(filename, 'w') as f:
            json.dump(stats_data, f, indent=2, default=str)
        
        print(f"💾 Statistics saved to {filename}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 rtsp_monitor.py <RTSP_URL> [interval]")
        print("Example: python3 rtsp_monitor.py rtsp://192.168.1.100:8554/screen 5")
        sys.exit(1)
    
    rtsp_url = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    monitor = RTSPMonitor(rtsp_url, interval)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
    finally:
        monitor.save_stats()

if __name__ == "__main__":
    main()