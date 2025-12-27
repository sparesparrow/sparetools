#!/bin/bash

# USB Device Monitor
# Monitors USB device changes and logs them

LOG_FILE="/var/log/usb_monitor.log"
DATE_FORMAT="%Y-%m-%d %H:%M:%S"
LAST_STATE_FILE="/tmp/usb_last_state.txt"

# Function to log with timestamp
log_message() {
    echo "[$(date +"$DATE_FORMAT")] $1" | tee -a "$LOG_FILE"
}

# Function to get current USB device list
get_usb_devices() {
    lsusb | sort
}

# Function to compare USB states
compare_usb_states() {
    local current_state="$1"
    local last_state="$2"
    
    # Find new devices
    comm -13 <(echo "$last_state") <(echo "$current_state") | while read -r line; do
        if [ -n "$line" ]; then
            log_message "USB DEVICE ADDED: $line"
        fi
    done
    
    # Find removed devices
    comm -23 <(echo "$last_state") <(echo "$current_state") | while read -r line; do
        if [ -n "$line" ]; then
            log_message "USB DEVICE REMOVED: $line"
        fi
    done
}

log_message "Starting USB monitoring..."

# Initialize with current state
get_usb_devices > "$LAST_STATE_FILE"

# Monitor USB changes
while true; do
    current_devices=$(get_usb_devices)
    last_devices=$(cat "$LAST_STATE_FILE" 2>/dev/null || echo "")
    
    if [ "$current_devices" != "$last_devices" ]; then
        compare_usb_states "$current_devices" "$last_devices"
        echo "$current_devices" > "$LAST_STATE_FILE"
    fi
    
    sleep 2
done