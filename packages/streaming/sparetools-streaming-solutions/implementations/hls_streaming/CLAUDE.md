# HLS Streaming Solution

## Context
This directory contains the HLS (HTTP Live Streaming) solution for real-time screen casting to the Hisense TV. HLS is an HTTP-based adaptive bitrate streaming communications protocol developed by Apple.

## Purpose
- **Primary Goal**: Establish a real-time screen streaming solution using HLS protocol
- **Target Device**: Hisense TV (192.168.200.44) - needs to support HLS client
- **Stream Source**: Linux desktop screen capture with audio
- **Latency Target**: 3-10 seconds (HLS has inherent latency due to segmenting)

## Technical Approach
1. **HLS Server**: Use FFmpeg to create HLS segments and playlist
2. **Screen Capture**: Real-time X11 screen capture with audio
3. **Video Encoding**: H.264 baseline profile for TV compatibility
4. **Segment Generation**: Create short video segments (2-10 seconds)
5. **HTTP Server**: Serve HLS playlist and segments via HTTP
6. **Client Connection**: TV connects to HLS playlist URL

## Files in this Directory
- `hls_server_setup.sh` - Install and configure HLS server dependencies
- `ffmpeg_hls_server.sh` - FFmpeg-based HLS server script
- `hls_http_server.py` - Python HTTP server for HLS content
- `hls_playlist_generator.py` - Dynamic playlist management
- `hls_client_test.py` - Test HLS stream connectivity
- `hls_tv_connection.py` - Specific TV connection and control
- `hls_monitor.sh` - Monitor HLS server status and segments
- `hls_config.conf` - HLS server configuration
- `hls_test_stream.sh` - Test stream generation

## Advantages
- Works over standard HTTP (no special protocols)
- Adaptive bitrate streaming
- Good browser support
- Reliable delivery over HTTP

## Challenges
- Inherent latency due to segmenting (3-10 seconds)
- TV must support HLS client
- Requires HTTP server setup
- More complex than simple file serving

## Success Criteria
- TV can connect to HLS stream
- Latency < 10 seconds
- Smooth playback without buffering
- Audio and video synchronization