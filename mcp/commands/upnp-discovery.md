# upnp-discovery

Discover UPnP/DLNA devices on the network

## Usage

```bash
python3 upnp_discovery.py
```

## Description

Scans the network for UPnP (Universal Plug and Play) and DLNA (Digital Living Network Alliance) compatible devices. Essential for finding media servers, TVs, and other streaming devices.

## What It Finds

- **Media Servers**: MiniDLNA, Plex, Emby, etc.
- **Media Renderers**: Smart TVs, streaming boxes
- **Media Players**: Network audio/video players
- **Network Gateways**: Routers with UPnP services

## Sample Output

```
🔍 Starting UPnP device discovery...
📡 Found 15 UPnP responses

📱 Device: 192.168.200.44
   ST: upnp:rootdevice
   Server: Platform 1.0 His/1.0 UPnP/1.0 DLNADOC/1.50
   Location: http://192.168.200.44:38400/MediaServer/rendererdevicedesc.xml
   ✅ Reachable

📱 Device: 192.168.200.160
   ST: uuid:4d696e69-444c-164e-9d41-98eecb26ec82
   Server: Debian DLNADOC/1.50 UPnP/1.0 MiniDLNA/1.3.3
   Location: http://192.168.200.160:8200/rootDesc.xml
   ✅ Reachable

🎬 Media Servers found: 1
   - 192.168.200.160: sparrow-DLNA

📺 Media Renderers/TVs found: 1
   - 192.168.200.44: Hisense VIDAA TV
```

## Key Information Provided

- **Device IP**: Network address of discovered device
- **Device Type**: Media server, renderer, TV, etc.
- **Server Info**: Software and version details
- **Service URLs**: Endpoints for control and streaming
- **Reachability**: Whether device responds to HTTP requests

## Use Cases

### Screen Casting Setup
```bash
# Find TVs and media servers
python3 upnp_discovery.py

# Note the IP addresses for casting targets
# Use with screen casting scripts
```

### Network Troubleshooting
```bash
# Check if DLNA devices are visible
python3 upnp_discovery.py

# Verify MiniDLNA server is running
# Check firewall settings
```

### Device Inventory
```bash
# Catalog all UPnP devices on network
python3 upnp_discovery.py > network_devices.txt

# Use for network documentation
```

## Dependencies

- Python 3.x
- requests library
- socket library (built-in)

## Troubleshooting

### No Devices Found
- Check network connectivity
- Verify devices support UPnP/DLNA
- Check firewall settings (port 1900 UDP)
- Try running as root/sudo

### Connection Refused
- Device may be powered off
- Firewall blocking access
- Service not running on device

## Related Commands

- `screen_capture_tv_compatible.sh`: Capture screen for DLNA
- `continuous_screen_cast.sh`: Stream to DLNA devices
- `rtsp_screen_stream.sh`: RTSP streaming alternative