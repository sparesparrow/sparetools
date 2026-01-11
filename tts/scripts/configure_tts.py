#!/usr/bin/env python3
"""
TTS Engine Configuration Helper
===============================

Interactive tool to configure and test TTS engines for the Mr. Robot monitor.
"""

import json
import os
import sys
from typing import Dict, Any

# Add the current directory to path for importing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mr_robot_monitor import VoiceAlertSystem, TTSEngine, VoicePersona


def load_config() -> Dict[str, Any]:
    """Load existing TTS configuration"""
    config_file = "tts_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}


def save_config(config: Dict[str, Any]):
    """Save TTS configuration"""
    try:
        with open("tts_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        print("Configuration saved to tts_config.json")
    except Exception as e:
        print(f"Error saving config: {e}")


def configure_elevenlabs():
    """Configure ElevenLabs TTS engine"""
    print("\n🎭 ElevenLabs Configuration")
    print("-" * 30)

    api_key = input("Enter ElevenLabs API key (or press Enter to skip): ").strip()
    if not api_key:
        return None

    voice_id = input("Enter voice ID (default: 21m00Tcm4TlvDq8ikWAM): ").strip()
    if not voice_id:
        voice_id = "21m00Tcm4TlvDq8ikWAM"

    model = input("Enter model (default: eleven_monolingual_v1): ").strip()
    if not model:
        model = "eleven_monolingual_v1"

    return {
        "api_key": api_key,
        "voice_id": voice_id,
        "model": model,
        "stability": 0.8,
        "similarity_boost": 0.9
    }


def configure_pyttsx3():
    """Configure pyttsx3 TTS engine"""
    print("\n🎤 pyttsx3 Configuration")
    print("-" * 25)

    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        print("Available voices:")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name}")

        voice_choice = input("Enter voice number (or press Enter for default): ").strip()
        rate = input("Enter speech rate (default: 180): ").strip()
        volume = input("Enter volume (0.0-1.0, default: 0.8): ").strip()

        config = {}

        if voice_choice and voice_choice.isdigit():
            voice_index = int(voice_choice)
            if 0 <= voice_index < len(voices):
                config["voice"] = voices[voice_index].id

        if rate and rate.isdigit():
            config["rate"] = int(rate)
        else:
            config["rate"] = 180

        if volume and volume.replace('.', '').isdigit():
            config["volume"] = float(volume)
        else:
            config["volume"] = 0.8

        return config

    except ImportError:
        print("pyttsx3 not installed. Install with: pip install pyttsx3")
        return None


def configure_espeak_ng():
    """Configure espeak-ng TTS engine"""
    print("\n🎵 espeak-ng Configuration")
    print("-" * 25)

    voice = input("Enter voice variant (default: en-us): ").strip() or "en-us"
    speed = input("Enter speed (default: 150): ").strip()
    pitch = input("Enter pitch (default: 50): ").strip()
    volume = input("Enter volume (default: 80): ").strip()

    config = {"voice": voice}

    if speed and speed.isdigit():
        config["speed"] = int(speed)
    if pitch and pitch.isdigit():
        config["pitch"] = int(pitch)
    if volume and volume.isdigit():
        config["volume"] = int(volume)

    return config


def test_engine(engine: TTSEngine, config: Dict[str, Any]):
    """Test a TTS engine configuration"""
    print(f"\n🧪 Testing {engine.value} engine...")

    try:
        voice_system = VoiceAlertSystem(preferred_engine=engine, engine_config={engine.value: config})
        success = voice_system.speak("This is a test of the TTS engine configuration.", VoicePersona.PROFESSIONAL)
        if success:
            print(f"✓ {engine.value} test successful!")
            return True
        else:
            print(f"✗ {engine.value} test failed")
            return False
    except Exception as e:
        print(f"✗ {engine.value} test error: {e}")
        return False


def interactive_configuration():
    """Run interactive TTS configuration"""
    print("🎛️  TTS Engine Configuration Tool")
    print("=" * 40)
    print("Configure and test TTS engines for the Mr. Robot monitor")

    # Load existing configuration
    config = load_config()
    print(f"\nLoaded existing configuration with {len(config)} engine settings")

    while True:
        print("\nAvailable TTS engines:")
        for i, engine in enumerate(TTSEngine):
            configured = "✓" if engine.value in config else " "
            print(f"  {i+1}. {configured} {engine.value}")

        print("\nOptions:")
        print("  c. Configure an engine")
        print("  t. Test an engine")
        print("  r. Remove engine configuration")
        print("  s. Save configuration")
        print("  q. Quit")

        choice = input("\nEnter your choice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == 's':
            save_config(config)
        elif choice == 'c':
            # Configure engine
            try:
                engine_num = int(input("Enter engine number to configure: ")) - 1
                if 0 <= engine_num < len(TTSEngine):
                    engine = list(TTSEngine)[engine_num]

                    if engine == TTSEngine.ELEVENLABS:
                        engine_config = configure_elevenlabs()
                    elif engine == TTSEngine.PYTTSX3:
                        engine_config = configure_pyttsx3()
                    elif engine == TTSEngine.ESPEAK_NG:
                        engine_config = configure_espeak_ng()
                    else:
                        print(f"Configuration not available for {engine.value}")
                        continue

                    if engine_config:
                        config[engine.value] = engine_config
                        print(f"✓ {engine.value} configured")
                else:
                    print("Invalid engine number")
            except ValueError:
                print("Invalid input")
        elif choice == 't':
            # Test engine
            try:
                engine_num = int(input("Enter engine number to test: ")) - 1
                if 0 <= engine_num < len(TTSEngine):
                    engine = list(TTSEngine)[engine_num]
                    engine_config = config.get(engine.value, {})
                    test_engine(engine, engine_config)
                else:
                    print("Invalid engine number")
            except ValueError:
                print("Invalid input")
        elif choice == 'r':
            # Remove configuration
            try:
                engine_num = int(input("Enter engine number to remove: ")) - 1
                if 0 <= engine_num < len(TTSEngine):
                    engine = list(TTSEngine)[engine_num]
                    if engine.value in config:
                        del config[engine.value]
                        print(f"✓ {engine.value} configuration removed")
                    else:
                        print(f"{engine.value} not configured")
                else:
                    print("Invalid engine number")
            except ValueError:
                print("Invalid input")
        else:
            print("Invalid choice")

    # Save before exit
    if config:
        save_config(config)


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        return

    interactive_configuration()


if __name__ == "__main__":
    main()