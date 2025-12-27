# cast-test-urls

Test Google Cast protocol endpoints

## Usage

```bash
# Manual testing - open URLs in browser
# See cast_test_urls.txt for complete list

# Automated testing
python3 automated_cast_test.py
```

## Description

Tests Google Cast protocol endpoints discovered through network analysis. Provides comprehensive testing of Cast receiver APIs and WebSocket connections.

## Test URLs

### Cast Setup Endpoints
- `http://192.168.200.44:8008/setup` - TV Cast setup
- `http://192.168.200.84:8008/setup` - Android Cast setup

### Receiver Status
- `http://192.168.200.44:8008/receiver/status` - TV receiver status
- `http://192.168.200.84:8008/receiver/status` - Android receiver status

### Cast Applications
- `http://192.168.200.44:8008/apps/YouTube` - YouTube Cast receiver
- `http://192.168.200.44:8008/apps/674A0243` - Discovered Cast device
- `http://192.168.200.44:8008/apps/233637DE` - Discovered Cast device
- `http://192.168.200.44:8008/apps/8E6C866D` - Discovered Cast device

## Testing Method

### Browser Testing
1. Open Chrome/Firefox Developer Tools (F12)
2. Go to Network tab
3. Visit each URL in address bar
4. Check for:
   - HTTP response codes
   - JSON responses
   - WebSocket connections (ws:// port 8009)
   - Cast API calls

### Automated Testing
```bash
python3 automated_cast_test.py
```
- Tests all URLs automatically
- Reports success/failure
- Checks WebSocket availability
- Saves results to JSON file

## Expected Results

### Successful Cast Endpoints
```json
{
  "status_code": 200,
  "content-type": "application/json",
  "response": {
    "name": "Hisense VIDAA TV",
    "capabilities": ["video", "audio"],
    "status": "ready"
  }
}
```

### WebSocket Connections
- `ws://192.168.200.44:8009/` - Real-time Cast control
- Persistent connection for media control
- Binary protocol for commands/status

## Troubleshooting

### Connection Refused
- Cast services only activate during active casting
- Try testing while YouTube app is casting to TV

### WebSocket Not Available
- Port 8009 may be closed when not casting
- Services start on-demand

### No JSON Response
- Endpoint may require specific headers
- Cast protocol may use different ports

## Packet Analysis Integration

Based on captured network traffic:
- Android device queries for Cast devices
- Specific device IDs: 674A0243, 233637DE, 8E6C866D
- mDNS queries on port 5353
- UPnP discovery on port 1900

## Related Commands

- `cast_monitor.py`: Monitor for active Cast sessions
- `upnp_discovery.py`: Discover DLNA/UPnP devices
- `continuous_screen_cast.sh`: Alternative screen streaming