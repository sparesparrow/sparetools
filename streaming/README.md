# Streaming Solutions

This directory contains tools and utilities for real-time screen streaming to DLNA/UPnP compatible devices, particularly Hisense TVs.

## Directory Structure

```
streaming/
├── scripts/          # Core streaming scripts
│   ├── screen_capture.sh
│   └── automated_cast_test.py
├── tools/            # Supporting tools
│   ├── cast_monitor.py
│   └── network_monitor/  # Network monitoring utilities
├── data/             # Sample data and test files
│   ├── cast_test_urls.txt
│   ├── cast_capture.pcap
│   ├── screen_current_flag.mp4
│   ├── screen_live_test.mp4
│   └── yt.mp4
└── README.md
```

## Components

### Screen Capture (`screen_capture.sh`)
Basic screen capture script using ffmpeg for X11 display capture with H.264 encoding.

### Automated Cast Testing (`automated_cast_test.py`)
Comprehensive testing suite for Cast/DLNA streaming functionality.

### Cast Monitor (`cast_monitor.py`)
Monitors for Cast service availability with voice alerts.

### Network Monitor
Complete network monitoring suite with device discovery, traffic analysis, and UPnP control.

## Usage

### Basic Screen Capture
```bash
./scripts/screen_capture.sh
```

### Test Streaming
```bash
python3 scripts/automated_cast_test.py
```

### Monitor Cast Services
```bash
python3 tools/cast_monitor.py
```

## Requirements

- ffmpeg
- Python 3
- UPnP/DLNA compatible devices
- X11 display server

## Target Device

- Hisense TV (192.168.200.44)
- MiniDLNA server (192.168.200.160)

## Protocols

- RTSP (Real-Time Streaming Protocol)
- HLS (HTTP Live Streaming)
- UPnP/DLNA for device discovery and control