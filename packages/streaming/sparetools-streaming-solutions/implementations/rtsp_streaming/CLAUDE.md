# RTSP Streaming Solution

## Context
This directory contains the RTSP (Real-Time Streaming Protocol) solution for real-time screen casting to the Hisense TV. RTSP is a network control protocol designed for use in entertainment and communications systems to control streaming media servers.

## Purpose
- **Primary Goal**: Establish a true real-time screen streaming solution using RTSP protocol
- **Target Device**: Hisense TV (192.168.200.44) - needs to support RTSP client
- **Stream Source**: Linux desktop screen capture with audio
- **Latency Target**: < 2 seconds end-to-end

## Technical Approach
1. **RTSP Server**: Use GStreamer or FFmpeg to create an RTSP server
2. **Screen Capture**: Real-time X11 screen capture with audio
3. **Video Encoding**: H.264 baseline profile for TV compatibility
4. **Network Streaming**: RTSP protocol over TCP/UDP
5. **Client Connection**: TV connects to RTSP stream URL

## Files in this Directory
- `rtsp_server_setup.sh` - Install and configure RTSP server dependencies
- `gstreamer_rtsp_server.py` - Python-based RTSP server using GStreamer
- `ffmpeg_rtsp_server.sh` - FFmpeg-based RTSP server script
- `rtsp_client_test.py` - Test RTSP stream connectivity
- `rtsp_tv_connection.py` - Specific TV connection and control
- `rtsp_monitor.sh` - Monitor RTSP server status and connections
- `rtsp_config.conf` - RTSP server configuration
- `rtsp_test_stream.sh` - Test stream generation

## Advantages
- True real-time streaming with low latency
- Standard protocol supported by many devices
- Can handle multiple concurrent clients
- Good for live video streaming

## Challenges
- TV must support RTSP client (may need verification)
- Network configuration complexity
- Requires more system resources
- May need firewall configuration

## Success Criteria
- TV can connect to RTSP stream
- Latency < 2 seconds
- Stable streaming without interruption
- Audio and video synchronization