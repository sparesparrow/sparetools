# Text-to-Speech (TTS) Tools

This directory contains tools for text-to-speech conversion, voice alerts, and audio feedback systems.

## Directory Structure

```
tts/
├── scripts/          # TTS control scripts
│   ├── configure_tts.py
│   ├── demo_voice_alerts.py
│   └── setup_voice_system.sh
├── config/           # Configuration files
│   ├── tts_config.json
│   └── tts_config_example.py
└── README.md
```

## Components

### Configuration
- **TTS Setup**: Configure TTS engines and voices
- **System Setup**: Install and configure TTS dependencies

### Voice Alerts
- **Demo Alerts**: Example voice notification system
- **Custom Alerts**: Configurable alert messages

## Usage

### Configure TTS
```bash
python3 scripts/configure_tts.py --voice english-us --engine espeak
```

### Setup Voice System
```bash
./scripts/setup_voice_system.sh
```

### Demo Voice Alerts
```bash
python3 scripts/demo_voice_alerts.py
```

## Supported Engines

- eSpeak-ng
- Festival
- Google TTS (online)
- Microsoft TTS (online)
- Pico TTS

## Configuration

TTS settings are stored in JSON format:

```json
{
  "engine": "espeak",
  "voice": "english-us",
  "speed": 150,
  "pitch": 50,
  "volume": 100
}
```

## Features

- Multiple TTS engine support
- Voice customization (speed, pitch, volume)
- Text preprocessing
- Audio file generation
- Real-time speech synthesis

## Dependencies

- TTS engine libraries
- Python libraries (pyttsx3, gtts)
- Audio playback utilities (aplay, mpg123)

## Applications

- Accessibility tools
- Voice notifications
- Automated announcements
- Testing and debugging alerts