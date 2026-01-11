# Continuous Screen Casting with Segmented Video

A system for continuously capturing screen content in short segments and making them available through DLNA for near real-time screen sharing.

## Overview

This system captures your desktop screen in 30-second segments and makes them available through a DLNA media server. The segments are automatically rotated, keeping only the most recent ones, providing a pseudo-real-time streaming experience.

## Features

- ✅ **30-second segments** for near real-time experience
- ✅ **Automatic segment rotation** (keeps last 3 segments)
- ✅ **TV-compatible encoding** (H.264 baseline profile)
- ✅ **DLNA integration** with automatic rescan
- ✅ **Real-time monitoring** of segment status
- ✅ **Configurable settings** via configuration file
- ✅ **Error handling** and retry logic

## Files

- `continuous_screen_cast.sh` - Main continuous casting script
- `monitor_screen_cast.sh` - Real-time segment monitoring
- `test_continuous_screen_cast.sh` - Test script for verification
- `continuous_screen_cast.conf` - Configuration file
- `README_continuous_screen_cast.md` - This documentation

## Quick Start

### 1. Setup

```bash
# Make scripts executable
chmod +x continuous_screen_cast.sh
chmod +x monitor_screen_cast.sh
chmod +x test_continuous_screen_cast.sh

# Run setup (if not already done)
bash continuous_stream_setup.sh
```

### 2. Test the System

```bash
# Run quick test
./test_continuous_screen_cast.sh -q

# Run full test (2 minutes)
./test_continuous_screen_cast.sh
```

### 3. Start Continuous Casting

```bash
# Start with default settings
./continuous_screen_cast.sh

# Start with custom settings
./continuous_screen_cast.sh -d 60 -s 5 -r 1920x1080
```

### 4. Monitor Segments

```bash
# Monitor in real-time
./monitor_screen_cast.sh

# Monitor with custom refresh rate
./monitor_screen_cast.sh -i 2
```

## Usage

### Basic Usage

```bash
./continuous_screen_cast.sh
```

### Advanced Usage

```bash
# 60-second segments, keep 5 segments
./continuous_screen_cast.sh -d 60 -s 5

# Full HD resolution
./continuous_screen_cast.sh -r 1920x1080

# Custom segment duration and resolution
./continuous_screen_cast.sh -d 45 -r 1600x900
```

### Command Line Options

- `-h, --help` - Show help message
- `-d, --duration` - Set segment duration in seconds (default: 30)
- `-s, --segments` - Set maximum segments to keep (default: 3)
- `-r, --resolution` - Set video resolution (default: 1280x720)

## Configuration

Edit `continuous_screen_cast.conf` to customize settings:

```ini
[General]
segment_duration=30
max_segments=3
video_width=1280
video_height=720
video_bitrate=2000k

[DLNA]
dlna_port=8200
auto_rescan=true

[Monitoring]
monitor_interval=5
verbose_logging=false
```

## How It Works

### 1. Segment Creation
- Captures screen in 30-second segments
- Uses H.264 baseline profile for TV compatibility
- Includes audio capture from default ALSA device

### 2. Segment Rotation
- `live_screen_1.mp4` - Current segment (newest)
- `live_screen_2.mp4` - Previous segment
- `live_screen_3.mp4` - Oldest kept segment

### 3. DLNA Integration
- Automatically rescans MiniDLNA after each segment
- Makes segments available via HTTP
- Compatible with any DLNA client

### 4. Cleanup
- Removes segments beyond the maximum count
- Prevents disk space issues
- Maintains only recent content

## Technical Details

### Video Encoding
- **Codec**: H.264 (libx264)
- **Profile**: Baseline
- **Level**: 3.0
- **Pixel Format**: yuv420p
- **Preset**: slow (for quality)
- **Bitrate**: 2000k (configurable)

### Audio Encoding
- **Codec**: AAC
- **Bitrate**: 128k
- **Source**: Default ALSA device

### File Structure
```
/var/lib/minidlna/screen_cast/
├── live_screen_1.mp4  (current)
├── live_screen_2.mp4  (previous)
└── live_screen_3.mp4  (oldest)
```

## Monitoring

### Real-time Monitor
```bash
./monitor_screen_cast.sh
```

Shows:
- Current segment status
- File sizes and ages
- DLNA URLs
- System status
- Disk usage

### Test Script
```bash
./test_continuous_screen_cast.sh
```

Tests:
- Prerequisites
- Screen capture
- DLNA connectivity
- Segment creation
- Continuous operation

## Troubleshooting

### Common Issues

1. **No X11 display available**
   ```bash
   export DISPLAY=:0.0
   ```

2. **ffmpeg not found**
   ```bash
   sudo apt install ffmpeg
   ```

3. **MiniDLNA not running**
   ```bash
   sudo systemctl start minidlna
   ```

4. **Permission denied**
   ```bash
   sudo chown $USER:$USER /var/lib/minidlna/screen_cast
   ```

### Debug Mode

Enable verbose logging in `continuous_screen_cast.conf`:
```ini
[Monitoring]
verbose_logging=true
log_file=/var/log/continuous_screen_cast.log
```

### Check Logs

```bash
# Check system logs
journalctl -u minidlna

# Check custom logs
tail -f /var/log/continuous_screen_cast.log
```

## Performance

### System Requirements
- **CPU**: Multi-core recommended for encoding
- **RAM**: 2GB+ available
- **Disk**: 1GB+ for segments
- **Network**: 100Mbps+ for streaming

### Optimization
- Use hardware acceleration if available
- Adjust bitrate based on network capacity
- Monitor disk usage for segment cleanup
- Use faster presets for lower CPU usage

## Integration

### With Existing Systems
- Compatible with existing MiniDLNA setup
- Works alongside other DLNA services
- Can be integrated with monitoring systems

### With TV Control
- Use `upnp_control.py` to control TV playback
- Automatically switch to new segments
- Integrate with voice alerts

## Security Considerations

- Screen content is stored in plain video files
- Ensure proper file permissions
- Consider network security for DLNA access
- Monitor disk usage to prevent space issues

## Limitations

- **Not true real-time** (30-second delay)
- **Storage usage** for multiple segments
- **CPU intensive** for continuous encoding
- **Network dependent** for DLNA access

## Alternatives

For true real-time streaming, consider:
- RTSP streaming (`rtsp_streaming/`)
- HLS streaming (`hls_streaming/`)
- WebRTC for web-based streaming

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test script for diagnostics
3. Check system logs for errors
4. Verify prerequisites are met

## License

This project is part of the continuous file streaming solution for CTF challenges.