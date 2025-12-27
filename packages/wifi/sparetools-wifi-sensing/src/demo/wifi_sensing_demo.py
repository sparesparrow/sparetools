#!/usr/bin/env python3
"""
WiFi Sensing Demo
Interactive demonstration of WiFi sensing capabilities
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tools.wifi_scanner import WiFiScanner
    from tts_enhanced import EnhancedTTS
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    TTS_AVAILABLE = False

def demo_basic_scanning():
    """Demonstrate basic WiFi scanning"""
    print("🏠 WiFi Sensing Demo - Basic Scanning")
    print("=" * 50)

    scanner = WiFiScanner(motion_detection=False)

    # Perform single scan
    scanner.single_scan()

    print("\n✅ Basic scanning demo complete!")

def demo_motion_detection():
    """Demonstrate motion detection capabilities"""
    print("🏠 WiFi Sensing Demo - Motion Detection")
    print("=" * 50)

    if not TTS_AVAILABLE:
        print("⚠️  TTS not available - motion announcements will be text-only")

    scanner = WiFiScanner(motion_detection=True)

    # Perform multiple scans to build signal history
    print("📊 Building signal history for motion analysis...")
    for i in range(3):
        print(f"Scan {i+1}/3...")
        networks = scanner.scan_networks()
        if networks:
            scanner.analyze_motion(networks)
        time.sleep(2)

    # Show final analysis
    print("\n📊 Motion Detection Analysis:")
    if scanner.motion_detector:
        stats = scanner.motion_detector.get_motion_statistics()
        print(f"   Networks monitored: {stats['networks_monitored']}")
        print(f"   Motion events: {stats['total_events']}")

        if stats['total_events'] > 0:
            print(".2f")
            print("   Motion detection: ACTIVE ✅")
        else:
            print("   No motion detected in analysis window")
            print("   (Try moving around or having someone walk nearby)")

    print("\n✅ Motion detection demo complete!")

def demo_continuous_monitoring():
    """Demonstrate continuous monitoring"""
    print("🏠 WiFi Sensing Demo - Continuous Monitoring")
    print("=" * 50)
    print("This will monitor WiFi signals for 30 seconds")
    print("Try moving around to trigger motion detection!")
    print("Press Ctrl+C to stop early\n")

    scanner = WiFiScanner(motion_detection=True)

    try:
        scanner.continuous_scan(interval=3, max_scans=10)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")

    print("\n✅ Continuous monitoring demo complete!")

def demo_tts_announcements():
    """Demonstrate text-to-speech capabilities"""
    print("🏠 WiFi Sensing Demo - TTS Announcements")
    print("=" * 50)

    if not TTS_AVAILABLE:
        print("❌ TTS not available. Install pyttsx3 and pygame for voice announcements.")
        return

    tts = EnhancedTTS()

    announcements = [
        "WiFi sensing system initialized",
        "Scanning for nearby networks",
        "Motion detected through walls",
        "Activity recognition active",
        "Signal analysis complete"
    ]

    print("🎤 Testing voice announcements...")
    for announcement in announcements:
        print(f"   Speaking: '{announcement}'")
        tts.speak(announcement)
        time.sleep(1)

    print("\n✅ TTS demo complete!")

def interactive_menu():
    """Interactive demo menu"""
    print("🏠 WiFi Sensing Research Workspace Demo")
    print("=" * 60)
    print("Choose a demonstration:")
    print("1. Basic WiFi Scanning")
    print("2. Motion Detection")
    print("3. Continuous Monitoring")
    print("4. Text-to-Speech Announcements")
    print("5. Run All Demos")
    print("0. Exit")
    print("=" * 60)

    while True:
        try:
            choice = input("Enter your choice (0-5): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                demo_basic_scanning()
            elif choice == "2":
                demo_motion_detection()
            elif choice == "3":
                demo_continuous_monitoring()
            elif choice == "4":
                demo_tts_announcements()
            elif choice == "5":
                print("\n🚀 Running all demos...")
                demo_basic_scanning()
                print()
                demo_motion_detection()
                print()
                demo_tts_announcements()
                print("\n✅ All demos completed!")
            else:
                print("❌ Invalid choice. Please enter 0-5.")

            if choice != "5":
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    if len(sys.argv) > 1:
        # Command line mode
        demo_name = sys.argv[1].lower()

        if demo_name == "scan":
            demo_basic_scanning()
        elif demo_name == "motion":
            demo_motion_detection()
        elif demo_name == "continuous":
            demo_continuous_monitoring()
        elif demo_name == "tts":
            demo_tts_announcements()
        elif demo_name == "all":
            demo_basic_scanning()
            demo_motion_detection()
            demo_tts_announcements()
        else:
            print("Usage: python wifi_sensing_demo.py [scan|motion|continuous|tts|all]")
            print("Or run without arguments for interactive menu")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()