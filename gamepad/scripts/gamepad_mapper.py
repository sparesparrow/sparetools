#!/usr/bin/env python3
"""
Gamepad mapper for Sony DualShock 4 controller
Reads from Linux input devices and maps buttons to keyboard/mouse actions
"""

import struct
import subprocess
import fcntl
import os
from pathlib import Path

# Input event structure
EVENT_FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

# DualShock 4 button codes (from linux/input-event-codes.h)
DS4_BUTTONS = {
    304: 'CROSS',      # X button
    305: 'CIRCLE',     # O button
    307: 'TRIANGLE',   # Triangle button
    308: 'SQUARE',     # Square button
    310: 'L1',         # Left bumper
    311: 'R1',         # Right bumper
    312: 'L2',         # Left trigger (pressed)
    313: 'R2',         # Right trigger (pressed)
    314: 'SHARE',      # Share button
    315: 'OPTIONS',    # Options button
    316: 'L3',         # Left stick click
    317: 'R3',         # Right stick click
    318: 'DPAD_UP',    # D-pad up
    319: 'DPAD_DOWN',  # D-pad down
    320: 'DPAD_LEFT',  # D-pad left
    321: 'DPAD_RIGHT', # D-pad right
}

# Axis codes for analog sticks
DS4_AXES = {
    0: 'LEFT_X',       # Left stick X
    1: 'LEFT_Y',       # Left stick Y
    2: 'RIGHT_X',      # Right stick X
    3: 'RIGHT_Y',      # Right stick Y
    4: 'L2_ANALOG',    # Left trigger analog
    5: 'R2_ANALOG',    # Right trigger analog
}

# Key mappings with geometric modifier combinations
KEY_MAPPINGS = {
    'CROSS': ['ctrl', 'Tab'],              # Ctrl+Tab (next tab)
    'CIRCLE': ['ctrl', 'shift', 'Tab'],    # Ctrl+Shift+Tab (previous tab)
    'TRIANGLE': ['alt', 'Tab'],            # Alt+Tab (window switch)
    'SQUARE': ['alt', 'shift', 'Tab'],     # Alt+Shift+Tab (reverse window switch)
    'L1': ['ctrl', 'alt', 'Tab'],          # Ctrl+Alt+Tab
    'R1': ['ctrl', 'alt', 'shift', 'Tab'], # Ctrl+Alt+Shift+Tab
    'SHARE': ['shift', 'Tab'],             # Shift+Tab
    'OPTIONS': ['alt', 'ctrl', 'shift'],   # Alt+Ctrl+Shift (multi-modifier)
    'DPAD_UP': ['up'],                     # Up arrow
    'DPAD_DOWN': ['down'],                 # Down arrow
    'DPAD_LEFT': ['left'],                 # Left arrow
    'DPAD_RIGHT': ['right'],               # Right arrow
    'L2': ['mouse1'],                      # Left click
    'R2': ['mouse3'],                      # Right click
}

def send_keys(keys):
    """Send keyboard/mouse events using xdotool"""
    try:
        if len(keys) == 1 and keys[0].startswith('mouse'):
            button = keys[0][-1]  # mouse1, mouse3, etc.
            subprocess.run(['xdotool', 'click', button], check=True, capture_output=True)
        else:
            # Send key combination
            cmd = ['xdotool', 'key']
            cmd.extend(keys)
            subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending keys {keys}: {e}")

def move_mouse_relative(x, y):
    """Move mouse cursor relatively"""
    try:
        # Scale down the movement for better control
        x = int(x / 1500)  # Adjust divisor for sensitivity
        y = int(y / 1500)

        if abs(x) > 0 or abs(y) > 0:
            subprocess.run(['xdotool', 'mousemove_relative', '--', str(x), str(y)],
                         check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error moving mouse: {e}")

# Track previous axis values to detect changes
axis_values = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
DEADZONE = 8000  # Ignore small movements

def find_ds4_device():
    """Find the DualShock 4 input device"""
    # Try known event numbers for Bluetooth gamepads
    candidates = ['/dev/input/event11', '/dev/input/event12', '/dev/input/event13']

    for device_path in candidates:
        if os.path.exists(device_path):
            try:
                with open(device_path, 'rb') as f:
                    # Try to read some data to see if it's responsive
                    data = f.read(100)
                    if data:
                        return device_path, "Wireless Controller (DualShock 4)"
            except:
                continue

    return None, None

def main():
    device_path, device_name = find_ds4_device()
    if not device_path:
        print("DualShock 4 controller not found!")
        print("Make sure the controller is connected via Bluetooth.")
        return

    print(f"Found {device_name} at {device_path}")
    print("Starting gamepad mapper... (Ctrl+C to stop)")
    print("Button mappings:")
    for button, keys in KEY_MAPPINGS.items():
        print(f"  {button}: {keys}")

    try:
        with open(device_path, 'rb') as device:
            while True:
                event_data = device.read(EVENT_SIZE)
                if not event_data:
                    break

                tv_sec, tv_usec, ev_type, code, value = struct.unpack(EVENT_FORMAT, event_data)

                # Button events (type 1)
                if ev_type == 1 and code in DS4_BUTTONS:
                    button_name = DS4_BUTTONS[code]

                    if value == 1:  # Button pressed
                        print(f"Button pressed: {button_name}")
                        if button_name in KEY_MAPPINGS:
                            send_keys(KEY_MAPPINGS[button_name])
                        else:
                            print(f"No mapping for {button_name}")

                # Axis events (type 3) - joystick movement
                elif ev_type == 3 and code in DS4_AXES:
                    axis_name = DS4_AXES[code]
                    prev_value = axis_values[code]

                    # Only process significant changes (outside deadzone)
                    if abs(value) > DEADZONE or abs(prev_value) > DEADZONE:
                        axis_values[code] = value

                        # Map left stick to mouse movement
                        if code == 0:  # LEFT_X
                            move_mouse_relative(value, 0)
                        elif code == 1:  # LEFT_Y
                            move_mouse_relative(0, value)

    except KeyboardInterrupt:
        print("\nStopping gamepad mapper...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()