#!/bin/bash

# SDR Device Monitoring Script
# Monitors USB SDR device connection status

LOG_FILE="$HOME/sdr_monitor.log"
VOICE_ENGINE="espeak-ng"
DEVICE_ID="1df7:2500"  # SDRplay RSP1
DEVICE_NAME="SDRplay RSP1"

# Function to log messages
log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
    echo "$(date): $1"
}

# Function to speak alert
speak_alert() {
    if command -v "$VOICE_ENGINE" &> /dev/null; then
        "$VOICE_ENGINE" "$1" 2>/dev/null
    else
        echo "Voice engine not found, falling back to echo"
        echo "$1"
    fi
}

# Initialize
PREVIOUS_STATE="unknown"
log_message "SDR monitoring started for $DEVICE_NAME"

while true; do
    # Check if SDR device is connected
    if lsusb | grep -q "$DEVICE_ID"; then
        CURRENT_STATE="connected"
    else
        CURRENT_STATE="disconnected"
    fi

    # Alert on state change
    if [ "$CURRENT_STATE" != "$PREVIOUS_STATE" ]; then
        if [ "$CURRENT_STATE" = "connected" ]; then
            MESSAGE="$DEVICE_NAME connected"
            speak_alert "$DEVICE_NAME is now connected"
        else
            MESSAGE="$DEVICE_NAME disconnected"
            speak_alert "Warning: $DEVICE_NAME has been disconnected"
        fi

        log_message "$MESSAGE"
    fi

    PREVIOUS_STATE="$CURRENT_STATE"
    sleep 10  # Check every 10 seconds
done