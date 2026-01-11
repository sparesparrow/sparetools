#!/usr/bin/env python3
"""
Simple gamepad mapper that reads from Linux input devices and sends keystrokes
"""

import struct
import time
import subprocess
from pathlib import Path

# Input event structure (from linux/input.h)
EVENT_FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

# DualShock 4 button codes (from input-event-codes.h)
BUTTON_CODES = {
    304: 'CROSS',      # X button
    305: 'CIRCLE',     # O button
    307: 'TRIANGLE',   # Triangle button
    308: 'SQUARE',     # Square button
    310: 'L1',         # Left bumper
    311: 'R1',         # Right bumper
    312: 'L2',         # Left trigger
    313: 'R2',         # Right trigger
    314: 'SHARE',      # Share button
    315: 'OPTIONS',    # Options button
    316: 'L3',         # Left stick click
    317: 'R3',         # Right stick click
    318: 'HAT_UP',     # D-pad up
    319: 'HAT_DOWN',   # D-pad down
    320: 'HAT_LEFT',   # D-pad left
    321: 'HAT_RIGHT',  # D-pad right
}

# Key mappings for Cursor IDE
KEY_MAPPINGS = {
    'CROSS': ['enter'],                    # Enter key
    'CIRCLE': ['escape'],                  # Escape key
    'TRIANGLE': ['ctrl', 'p'],             # Ctrl+P (command palette)
    'SQUARE': ['ctrl', 'space'],           # Ctrl+Space (suggestions)
    'L1': ['alt', 'left'],                 # Alt+Left (previous tab)
    'R1': ['alt', 'right'],                # Alt+Right (next tab)
    'SHARE': ['ctrl', 'w'],                # Ctrl+W (close tab)
    'OPTIONS': ['ctrl', 'b'],              # Ctrl+B (toggle sidebar)
    'HAT_UP': ['up'],                      # Up arrow
    'HAT_DOWN': ['down'],                  # Down arrow
    'HAT_LEFT': ['left'],                  # Left arrow
    'HAT_RIGHT': ['right'],                # Right arrow
    'L2': ['mouse_left_click'],            # Left mouse click
    'R2': ['mouse_right_click'],           # Right mouse click
}

def send_key_press(keys):
    """Send a key press using xdotool"""
    try:
        if keys == ['mouse_left_click']:
            subprocess.run(['xdotool', 'click', '1'], check=True)
        elif keys == ['mouse_right_click']:
            subprocess.run(['xdotool', 'click', '3'], check=True)
        else:
            # Build xdotool command
            cmd = ['xdotool']
            for key in keys:
                cmd.extend(['keydown', key])
            cmd.append('keyup')
            for key in reversed(keys):
                cmd.extend(['keyup', key])

            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending key press: {e}")

def read_input_events(device_path):
    """Read input events from device and map to keys"""
    print(f"Reading from {device_path}")

    try:
        with open(device_path, 'rb') as device:
            print("Gamepad mapper started. Press buttons to test...")

            while True:
                event_data = device.read(EVENT_SIZE)
                if not event_data:
                    break

                tv_sec, tv_usec, ev_type, code, value = struct.unpack(EVENT_FORMAT, event_data)

                # Only process button events (type 1)
                if ev_type == 1 and code in BUTTON_CODES:
                    button_name = BUTTON_CODES[code]

                    if value == 1:  # Button pressed
                        print(f"Button pressed: {button_name}")
                        if button_name in KEY_MAPPINGS:
                            send_key_press(KEY_MAPPINGS[button_name])

    except KeyboardInterrupt:
        print("Stopping gamepad mapper...")
    except Exception as e:
        print(f"Error reading device: {e}")

def find_gamepad_device():
    """Find the gamepad input device"""
    input_dir = Path('/dev/input')
    for event_file in input_dir.glob('event*'):
        try:
            with open(event_file, 'rb') as f:
                # Get device name
                name = b'\x00' * 256
                import fcntl
                import termios
                name = fcntl.ioctl(f.fileno(), 0x80004506, name)  # EVIOCGNAME
                name = name.decode('utf-8', errors='ignore').rstrip('\x00')

                if 'Wireless Controller' in name or 'DualShock' in name:
                    return str(event_file)
        except:
            continue
    return None

if __name__ == '__main__':
    device = find_gamepad_device()
    if device:
        print(f"Found gamepad device: {device}")
        read_input_events(device)
    else:
        print("No gamepad device found!")