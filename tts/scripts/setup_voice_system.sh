#!/bin/bash
# Mr. Robot Voice System Setup Script
# Installs required voice synthesis engines for the Mr. Robot monitor

set -e

echo "🔧 Setting up Mr. Robot Voice Alert System..."
echo "=============================================="

# Check if running on supported OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Linux detected"

    # Update package lists
    echo "📦 Updating package lists..."
    sudo apt-get update

    # Install espeak-ng (primary voice engine)
    echo "🎤 Installing espeak-ng (primary voice engine)..."
    if ! command -v espeak-ng &> /dev/null; then
        sudo apt-get install -y espeak-ng
        echo "✓ espeak-ng installed"
    else
        echo "✓ espeak-ng already installed"
    fi

    # Install spd-say (fallback voice engine)
    echo "🎤 Installing speech-dispatcher (fallback voice engine)..."
    if ! command -v spd-say &> /dev/null; then
        sudo apt-get install -y speech-dispatcher
        echo "✓ speech-dispatcher installed"
    else
        echo "✓ speech-dispatcher already installed"
    fi

    # Install additional voice packages for better quality
    echo "🎵 Installing additional voice packages..."
    sudo apt-get install -y espeak-ng-data mbrola mbrola-us1 mbrola-us2 mbrola-us3

    # Install Festival TTS
    echo "🎤 Installing Festival TTS..."
    if ! command -v festival &> /dev/null; then
        sudo apt-get install -y festival festvox-kallpc16k
        echo "✓ Festival installed"
    else
        echo "✓ Festival already installed"
    fi

    # Install Python TTS dependencies
    echo "🐍 Installing Python TTS libraries..."
    pip3 install --user pyttsx3 gtts pygame 2>/dev/null || echo "⚠️  Some Python packages may require manual installation"

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected"

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

    # Install espeak-ng
    echo "🎤 Installing espeak-ng..."
    if ! command -v espeak-ng &> /dev/null; then
        brew install espeak-ng
        echo "✓ espeak-ng installed"
    else
        echo "✓ espeak-ng already installed"
    fi

    # Install Python TTS dependencies
    echo "🐍 Installing Python TTS libraries..."
    pip3 install --user pyttsx3 gtts pygame 2>/dev/null || echo "⚠️  Some Python packages may require manual installation"

else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "This script supports Linux and macOS only."
    exit 1
fi

# Make the monitor script executable
echo "🔧 Making monitor script executable..."
chmod +x mr_robot_monitor.py

# Test the voice system
echo "🧪 Testing voice system..."
if python3 mr_robot_monitor.py --test-voice; then
    echo "✓ Voice system test passed"
else
    echo "⚠️  Voice system test failed - some features may not work"
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "Usage:"
echo "  # Test voice system:"
echo "  python3 mr_robot_monitor.py --test-voice"
echo ""
echo "  # Run system monitoring once:"
echo "  python3 mr_robot_monitor.py"
echo ""
echo "  # Run in daemon mode (continuous monitoring):"
echo "  python3 mr_robot_monitor.py --daemon"
echo ""
echo "Voice engines installed:"
if command -v espeak-ng &> /dev/null; then
    echo "  ✓ espeak-ng (primary)"
fi
if command -v spd-say &> /dev/null; then
    echo "  ✓ spd-say (fallback)"
fi
echo ""
echo "Happy hacking! 🤖"