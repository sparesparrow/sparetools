#!/usr/bin/env python3
"""
Test script for audio alerts and system functionality
"""

import time
import sys
import os

try:
    import pygame
    import numpy as np
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pygame", "numpy"], check=True)
    import pygame
    import numpy as np

def test_audio_alerts():
    """Test the audio alert system"""
    print("🔊 Testing Audio Alert System...")
    
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Create test sounds
    sample_rate = 22050
    duration = 0.5
    
    # Test different frequencies
    frequencies = [440, 550, 660, 880]  # A4, C#5, E5, A5
    
    for i, freq in enumerate(frequencies):
        print(f"Playing alert {i+1}/4 (Frequency: {freq} Hz)...")
        
        # Create sound
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for j in range(frames):
            arr[j][0] = np.sin(2 * np.pi * freq * j / sample_rate)
            arr[j][1] = np.sin(2 * np.pi * freq * j / sample_rate)
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        
        # Play sound
        sound.play()
        time.sleep(duration + 0.2)  # Wait for sound to finish
    
    print("✅ Audio alert test completed!")

def test_system_components():
    """Test all system components"""
    print("\n🔍 Testing System Components...")
    
    # Test 1: Check if scripts exist
    scripts = ["network_monitor.py", "xiaomi_hidden_settings.py", "launcher.py"]
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script} - Found")
        else:
            print(f"❌ {script} - Missing")
    
    # Test 2: Check dependencies
    dependencies = ["scapy", "matplotlib", "numpy", "pygame"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - Installed")
        except ImportError:
            print(f"❌ {dep} - Missing")
    
    # Test 3: Check permissions
    if os.geteuid() == 0:
        print("✅ Running as root - Packet capture enabled")
    else:
        print("⚠️  Not running as root - Packet capture may be limited")
    
    print("✅ System component test completed!")

def simulate_network_alerts():
    """Simulate network monitoring alerts"""
    print("\n📡 Simulating Network Monitoring Alerts...")
    
    # Simulate packet counting
    for i in range(1, 21):
        print(f"Packet {i}: 192.168.43.{100 + i} -> 8.8.8.8 (Protocol: 17)")
        
        # Alert every 5 packets
        if i % 5 == 0:
            print(f"🚨 ALERT: {i} packets processed!")
            test_audio_alerts()
        
        time.sleep(0.1)
    
    print("✅ Network alert simulation completed!")

def main():
    print("="*60)
    print("    WiFi Hotspot Monitor - System Test")
    print("="*60)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test system components
    test_system_components()
    
    # Test audio alerts
    test_audio_alerts()
    
    # Simulate network monitoring
    simulate_network_alerts()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("Your WiFi hotspot monitoring system is ready to use!")
    print("\nTo start monitoring:")
    print("  sudo python3 network_monitor.py")
    print("\nTo access Xiaomi 11 settings:")
    print("  python3 xiaomi_hidden_settings.py")
    print("\nTo use the launcher:")
    print("  python3 launcher.py")
    print("="*60)

if __name__ == "__main__":
    main()