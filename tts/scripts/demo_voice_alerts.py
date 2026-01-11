#!/usr/bin/env python3
"""
Demo script for Mr. Robot Voice Alert System
Shows how to use the voice system programmatically
"""

from mr_robot_monitor import VoiceAlertSystem, VoicePersona

def demo_voice_alerts():
    """Demonstrate different voice personas and alert types"""

    print("🎭 Mr. Robot Voice Alert System Demo")
    print("=" * 40)

    voice_system = VoiceAlertSystem()

    # Demo alerts with different personas
    alerts = [
        ("System initialization complete.", VoicePersona.MR_ROBOT, "normal"),
        ("Security breach detected.", VoicePersona.FSOCIETY, "high"),
        ("I think we have a problem.", VoicePersona.ELLIOT, "normal"),
        ("CRITICAL: Intrusion detected!", VoicePersona.MR_ROBOT, "critical"),
        ("Maintenance check required.", VoicePersona.ELLIOT, "low"),
        ("Hack the planet.", VoicePersona.FSOCIETY, "high"),
    ]

    print("Playing voice alerts...")
    print("(Press Ctrl+C to skip)")

    try:
        for message, persona, urgency in alerts:
            print(f"\n🎤 {persona.value.upper()}: {message}")
            voice_system.speak(message, persona, urgency)

    except KeyboardInterrupt:
        print("\nDemo interrupted.")

    print("\nDemo complete! 🎉")

if __name__ == "__main__":
    demo_voice_alerts()