# Continuous File Streaming Solution

## Context
This directory contains the continuous file streaming solution for real-time screen casting to the Hisense TV. This approach uses DLNA/UPnP with continuous file overwriting to simulate real-time streaming.

## Purpose
- **Primary Goal**: Achieve pseudo-real-time streaming using DLNA with continuous file updates
- **Target Device**: Hisense TV (192.168.200.44) - already confirmed working with DLNA
- **Stream Source**: Linux desktop screen capture with audio
- **Latency Target**: 5-15 seconds (limited by file processing and DLNA rescan)

## Technical Approach
1. **Continuous Capture**: Capture screen in very short segments (5-10 seconds)
2. **File Overwrite**: Continuously overwrite the same file name
3. **DLNA Rescan**: Force MiniDLNA to rescan after each update
4. **TV Refresh**: TV automatically detects file changes and updates
5. **Optimization**: Minimize file size and processing time

## Files in this Directory
- `continuous_stream_setup.sh` - Setup continuous streaming environment
- `optimized_continuous_cast.sh` - Optimized continuous casting script
- `dlna_refresh_monitor.py` - Monitor and manage DLNA refreshes
- `file_watcher.py` - Monitor file changes and TV updates
- `stream_optimizer.py` - Optimize video encoding for minimal latency
- `tv_connection_manager.py` - Manage TV connection and playback
- `continuous_monitor.sh` - Monitor streaming status and performance
- `stream_config.conf` - Continuous streaming configuration
- `test_continuous_stream.sh` - Test continuous streaming functionality

## Advantages
- Uses existing DLNA infrastructure
- TV already confirmed working
- Simple implementation
- No new protocols needed

## Challenges
- Not true real-time (file-based)
- Latency due to file processing
- DLNA rescan overhead
- May cause playback interruptions

## Success Criteria
- TV shows updated content within 15 seconds
- Smooth transitions between segments
- No playback errors or freezes
- Acceptable user experience for CTF challenge