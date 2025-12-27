# continuous-screen-cast

Continuous screen casting with segmented video

## Usage

```bash
./continuous_screen_cast.sh
```

## Description

Continuously captures screen in short segments (30 seconds each) and makes them available through DLNA. Provides near real-time screen sharing by constantly updating video segments in the media library.

## How It Works

1. Captures 30-second video segments
2. Saves to MiniDLNA media directory
3. Forces DLNA rescan to make new segment available
4. Cleans up old segments (keeps last 3)
5. Repeats continuously

## Technical Details

- **Segment Duration**: 30 seconds
- **Video Codec**: H.264 Baseline profile
- **Resolution**: 1280x720
- **Color Space**: yuv420p
- **Storage**: `/var/lib/minidlna/screen_cast/`

## File Naming

- `live_screen_1.mp4` (current segment)
- `live_screen_2.mp4` (previous segment)
- `live_screen_3.mp4` (oldest kept segment)

## Advantages

- ✅ Works with any DLNA-compatible device
- ✅ No special client software required
- ✅ Automatic cleanup of old segments
- ✅ TV-compatible video encoding

## Limitations

- 30-second delay between segments
- Storage usage for multiple segments
- Not true real-time (segmented)

## Control

- **Start**: Run the script
- **Stop**: Ctrl+C to interrupt
- **Monitor**: Check `/var/lib/minidlna/screen_cast/` directory

## Related Commands

- `screen_capture_tv_compatible.sh`: Single screen capture
- `rtsp_screen_stream.sh`: True real-time RTSP streaming
- `upnp_discovery.py`: Find DLNA devices on network