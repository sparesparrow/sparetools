# rtsp-screen-stream

Real-time RTSP screen streaming

## Usage

```bash
./rtsp_screen_stream.sh
```

## Description

Streams the screen in real-time using RTSP (Real-Time Streaming Protocol). Provides true live screen sharing with minimal latency, suitable for remote control and monitoring applications.

## How It Works

1. Starts FFmpeg RTSP server
2. Captures screen in real-time
3. Streams to RTSP URL: `rtsp://localhost:8554/screen`
4. Clients connect to RTSP stream directly

## Technical Details

- **Protocol**: RTSP (Real-Time Streaming Protocol)
- **Transport**: RTP over RTSP
- **Video Codec**: H.264 Baseline profile
- **Resolution**: Configurable (default: 1280x720)
- **Frame Rate**: 25 fps
- **Bitrate**: Variable (adaptive)

## RTSP URL

```
rtsp://[server-ip]:8554/screen
```

Replace `[server-ip]` with your machine's IP address.

## Client Playback

### VLC Media Player
```
Media → Open Network Stream → rtsp://192.168.200.160:8554/screen
```

### FFmpeg
```bash
ffmpeg -i rtsp://192.168.200.160:8554/screen -c copy output.mp4
```

### Browser (with WebRTC bridge)
```javascript
// Requires additional WebRTC streaming setup
```

## Advantages

- ✅ True real-time streaming (< 1 second latency)
- ✅ No segmentation delays
- ✅ Professional streaming protocol
- ✅ Compatible with surveillance systems
- ✅ Low bandwidth usage

## Setup Requirements

- FFmpeg with RTSP support
- Network access to port 8554
- RTSP-compatible client software

## Related Commands

- `continuous_screen_cast.sh`: Segmented DLNA streaming
- `screen_capture_tv_compatible.sh`: Single video capture
- `upnp_discovery.py`: Network device discovery