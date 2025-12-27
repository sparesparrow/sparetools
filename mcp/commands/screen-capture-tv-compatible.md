# screen-capture-tv-compatible

Capture screen with TV-compatible video encoding

## Usage

```bash
./screen_capture_tv_compatible.sh
```

## Description

Captures the current screen and saves it as an MP4 file optimized for TV playback. Uses H.264 baseline profile and yuv420p color space that are compatible with most smart TVs and media players.

## Technical Details

- **Video Codec**: H.264 Constrained Baseline Profile (Level 3.0)
- **Resolution**: 1280x720 (720p)
- **Color Space**: yuv420p (TV-compatible)
- **Container**: MP4
- **Frame Rate**: 29.97 fps

## Output

- **File**: `screen_test_tv.mp4` in MiniDLNA media directory
- **Location**: `/var/lib/minidlna/screen_cast/screen_test_tv.mp4`
- **DLNA Access**: Available through `sparrow-DLNA` media server

## Compatibility

Compatible with:
- Smart TVs (Samsung, LG, Hisense, etc.)
- Media players (VLC, Kodi, Plex)
- Streaming devices (Roku, Fire TV, Chromecast)
- Mobile devices

## Troubleshooting

### File Not Supported Error
- Original file used incompatible H.264 High profile
- TV-compatible version uses Baseline profile
- Ensure TV firmware is up to date

### DLNA Not Visible
- Check MiniDLNA service: `sudo systemctl status minidlna`
- Force rescan: `sudo minidlnad -R`
- Verify network connectivity

## Related Commands

- `continuous_screen_cast.sh`: Automated segmented screen casting
- `rtsp_screen_stream.sh`: Real-time RTSP streaming
- `upnp_discovery.py`: Discover DLNA/UPnP devices