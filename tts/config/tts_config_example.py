#!/usr/bin/env python3
"""
TTS Configuration Examples
==========================

Examples of how to configure TTS engines programmatically.
"""

from mr_robot_monitor import VoiceAlertSystem, TTSEngine, VoicePersona

def example_basic_configuration():
    """Basic TTS engine configuration"""
    print("🎵 Basic TTS Configuration")

    # Configure pyttsx3 engine
    pyttsx3_config = {
        "pyttsx3": {
            "rate": 180,      # Speech rate (words per minute)
            "volume": 0.8,    # Volume (0.0-1.0)
            "voice": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
        }
    }

    # Create voice system with configuration
    voice = VoiceAlertSystem(
        preferred_engine=TTSEngine.PYTTSX3,
        engine_config=pyttsx3_config
    )

    # Speak with configured settings
    voice.speak("This uses the configured pyttsx3 settings.", VoicePersona.PROFESSIONAL)


def example_elevenlabs_configuration():
    """ElevenLabs TTS configuration"""
    print("🎭 ElevenLabs Configuration")

    # Configure ElevenLabs (requires API key)
    elevenlabs_config = {
        "elevenlabs": {
            "api_key": "your_elevenlabs_api_key_here",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Mr. Robot style voice
            "model": "eleven_monolingual_v1",
            "stability": 0.8,
            "similarity_boost": 0.9
        }
    }

    # Create voice system with ElevenLabs
    voice = VoiceAlertSystem(
        preferred_engine=TTSEngine.ELEVENLABS,
        engine_config=elevenlabs_config
    )

    # Speak with high-quality voice
    voice.speak("This uses premium ElevenLabs voice synthesis.", VoicePersona.MR_ROBOT)


def example_multi_engine_fallback():
    """Multi-engine configuration with fallbacks"""
    print("🔄 Multi-Engine Configuration")

    # Configure multiple engines
    multi_config = {
        "elevenlabs": {
            "api_key": "your_api_key",
            "voice_id": "29vD33N1CtxCmqQRPOHJ",  # Elliot voice
            "model": "eleven_monolingual_v1"
        },
        "pyttsx3": {
            "rate": 160,
            "volume": 0.9
        },
        "espeak-ng": {
            "voice": "en-us",
            "speed": 140,
            "pitch": 45
        }
    }

    # System will try ElevenLabs first, then fallback to others
    voice = VoiceAlertSystem(
        preferred_engine=TTSEngine.ELEVENLABS,  # Primary choice
        engine_config=multi_config
    )

    # Test different personas
    personas = [VoicePersona.ELLIOT, VoicePersona.MR_ROBOT, VoicePersona.FSOCIETY]

    for persona in personas:
        voice.speak(f"Hello from {persona.value} persona.", persona)


def example_dynamic_configuration():
    """Dynamic TTS configuration changes"""
    print("⚙️  Dynamic Configuration")

    voice = VoiceAlertSystem()

    # Start with default settings
    voice.speak("Default voice settings.", VoicePersona.PROFESSIONAL)

    # Change to faster, louder speech
    fast_config = {
        "pyttsx3": {
            "rate": 220,
            "volume": 1.0
        }
    }

    voice = VoiceAlertSystem(
        preferred_engine=TTSEngine.PYTTSX3,
        engine_config=fast_config
    )

    voice.speak("Now I'm speaking faster and louder!", VoicePersona.ENTHUSIASTIC)

    # Change to slower, calmer speech
    calm_config = {
        "pyttsx3": {
            "rate": 120,
            "volume": 0.6
        }
    }

    voice = VoiceAlertSystem(
        preferred_engine=TTSEngine.PYTTSX3,
        engine_config=calm_config
    )

    voice.speak("Now I'm speaking slower and softer.", VoicePersona.CALM)


def main():
    """Run all examples"""
    print("🎛️  TTS Configuration Examples")
    print("=" * 35)

    try:
        example_basic_configuration()
        print()

        # Only run ElevenLabs if API key is available
        import os
        if os.getenv('ELEVENLABS_API_KEY'):
            example_elevenlabs_configuration()
            print()
        else:
            print("⏭️  Skipping ElevenLabs example (no API key)")

        example_multi_engine_fallback()
        print()

        example_dynamic_configuration()
        print()

        print("✅ All examples completed!")

    except Exception as e:
        print(f"❌ Example failed: {e}")


if __name__ == "__main__":
    main()