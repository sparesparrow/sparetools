#!/bin/bash

# Gamepad Button Monitoring Script with Voice Alerts
# Monitors Sony DualShock controller button presses

LOG_FILE="$HOME/gamepad_monitor.log"
VOICE_ENGINE="espeak-ng"
EVENT_DEVICE="/dev/input/event11"  # From /proc/bus/input/devices

# DualShock 4 button mappings (approximate - may need adjustment)
declare -A BUTTON_NAMES=(
    [304]="Cross (X)"
    [305]="Circle (O)"
    [306]="Triangle"
    [307]="Square"
    [308]="L1"
    [309]="R1"
    [310]="L2"
    [311]="R2"
    [312]="Share"
    [313]="Options"
    [314]="PS Button"
    [315]="Left Stick Click"
    [316]="Right Stick Click"
    [317]="DPad Up"
    [318]="DPad Down"
    [319]="DPad Left"
    [320]="DPad Right"
)

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

# Check if device exists
if [ ! -c "$EVENT_DEVICE" ]; then
    log_message "Gamepad device $EVENT_DEVICE not found"
    speak_alert "Gamepad device not found"
    exit 1
fi

log_message "Gamepad monitoring started on $EVENT_DEVICE"
speak_alert "Gamepad monitoring started"

# Monitor button presses using evtest
timeout 3600 evtest "$EVENT_DEVICE" 2>/dev/null | while read -r line; do
    # Look for button press events (type 1, value 1)
    if [[ $line =~ type\ 1\ \(EV_KEY\),\ code\ ([0-9]+)\ \(.*\),\ value\ 1 ]]; then
        button_code="${BASH_REMATCH[1]}"
        button_name="${BUTTON_NAMES[$button_code]}"

        if [ -n "$button_name" ]; then
            MESSAGE="Gamepad button pressed: $button_name"
            log_message "$MESSAGE"
            speak_alert "$button_name pressed"
        else
            MESSAGE="Unknown gamepad button pressed (code: $button_code)"
            log_message "$MESSAGE"
            speak_alert "Unknown button $button_code pressed"
        fi
    fi
done

log_message "Gamepad monitoring stopped"
speak_alert "Gamepad monitoring stopped"