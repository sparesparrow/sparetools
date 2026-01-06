# Network Monitor & Hotspot Suite

Complete network management solution including WiFi hotspot, screen casting, and network monitoring.

## 🚀 Quick Start

```bash
# Main launcher (recommended)
./launcher.sh

# Quick WiFi hotspot setup
./quick_setup.sh

# Full network management
./network_manager.sh
```

## 📁 Directory Structure

```
~/network_monitor/
├── launcher.sh                    # Main entry point
├── quick_setup.sh                 # Quick WiFi hotspot setup
├── network_manager.sh             # Full network management
├── setup_wifi_hotspot.sh          # WiFi hotspot configuration
├── fix_authentication.sh          # Authentication troubleshooting
├── wifi-hotspot.service           # Systemd service file
├── rtsp_*.sh                      # Real-time RTSP streaming
├── rtsp_*.py                      # RTSP discovery and monitoring
├── continuous_screen_cast.*       # DLNA screen casting
├── monitor_screen_cast.sh         # Screen cast monitoring
├── test_continuous_screen_cast.sh # Screen cast testing
└── README.md                      # This file
```

## 🌐 WiFi Hotspot

### Features
- **SSID**: STUDIJKO
- **Password**: pppppppp
- **IP Range**: 192.168.200.0/24
- **Internet Sharing**: eth0 → wlan0
- **Local Network Access**: Full access to 192.168.200.0/24

### Usage
```bash
# Start hotspot
sudo ./setup_wifi_hotspot.sh

# Stop hotspot
sudo ./setup_wifi_hotspot.sh --stop

# Check status
sudo ./setup_wifi_hotspot.sh --status

# Using systemd service
sudo systemctl start wifi-hotspot.service
sudo systemctl stop wifi-hotspot.service
```

## 📺 Screen Casting

### Real-Time RTSP Streaming
```bash
# Start RTSP server
./rtsp_screen_stream.sh

# Test RTSP client
./rtsp_client_test.sh

# RTSP launcher
./rtsp_launcher.sh
```

### Continuous DLNA Casting
```bash
# Start continuous casting
./continuous_screen_cast.sh

# Monitor segments
./monitor_screen_cast.sh

# Test casting
./test_continuous_screen_cast.sh
```

## 🔧 Service Management

### Services
- **hostapd**: WiFi access point
- **dnsmasq**: DHCP and DNS server
- **minidlna**: DLNA media server
- **wifi-hotspot**: Custom hotspot service

### Commands
```bash
# Check service status
systemctl status hostapd dnsmasq minidlna wifi-hotspot.service

# Start services
sudo systemctl start hostapd dnsmasq

# Stop services
sudo systemctl stop hostapd dnsmasq

# Enable services
sudo systemctl enable wifi-hotspot.service
```

## 🧪 Testing & Diagnostics

### Authentication
```bash
./fix_authentication.sh
```

### Network Connectivity
```bash
# Test internet
ping -c 3 8.8.8.8
ping -c 3 google.com

# Test RTSP
./rtsp_client_test.sh

# Test DLNA
python3 rtsp_discovery.py
```

### System Health
```bash
# Service status
systemctl status hostapd dnsmasq minidlna

# Disk usage
df -h

# Memory usage
free -h

# Network interfaces
ip addr show
```

## 📊 Monitoring

### Network Status
- Interface configuration
- Routing table
- Service status
- Connected devices
- Internet connectivity

### Screen Cast Monitoring
- Segment status
- File sizes and ages
- DLNA URLs
- System resources

### RTSP Monitoring
- Stream quality
- Latency measurement
- Bitrate monitoring
- Error tracking

## 🔐 Authentication

### Sudo Issues
If you encounter authentication problems:

1. **Check authentication**: `./fix_authentication.sh`
2. **Manual start**: `sudo ./setup_wifi_hotspot.sh`
3. **Alternative**: `pkexec ./setup_wifi_hotspot.sh`

### Password Reset
If you forgot your password:
1. Boot into recovery mode
2. Mount root: `mount -o remount,rw /`
3. Change password: `passwd sparrow`
4. Reboot: `reboot`

## 🌐 Network Configuration

### Interfaces
- **eth0**: Internet connection (192.168.200.160/24)
- **wlan0**: WiFi hotspot (192.168.200.1/24)

### Routing
- **NAT**: Internet sharing from eth0 to wlan0
- **Local Access**: Full access to 192.168.200.0/24
- **DHCP**: Automatic IP assignment for clients
- **DNS**: Forwarding to 8.8.8.8, 1.1.1.1

### Firewall
- **IP Forwarding**: Enabled
- **NAT Rules**: MASQUERADE on eth0
- **Forward Rules**: wlan0 ↔ eth0
- **Local Access**: 192.168.200.0/24 ↔ 192.168.200.0/24

## 🚨 Troubleshooting

### Common Issues

1. **WiFi hotspot not starting**
   - Check authentication: `./fix_authentication.sh`
   - Check prerequisites: hostapd, dnsmasq, iptables
   - Check interfaces: `ip addr show`

2. **No internet on connected devices**
   - Check IP forwarding: `cat /proc/sys/net/ipv4/ip_forward`
   - Check iptables rules: `iptables -L -n`
   - Check dnsmasq: `systemctl status dnsmasq`

3. **Screen casting not working**
   - Check MiniDLNA: `systemctl status minidlna`
   - Check file permissions: `ls -la /var/lib/minidlna/`
   - Check DLNA access: `curl http://localhost:8200/`

4. **RTSP streaming issues**
   - Check ffmpeg: `ffmpeg -version`
   - Check port availability: `netstat -tulpn | grep 8554`
   - Check firewall: `iptables -L -n`

### Logs
```bash
# System logs
journalctl -u hostapd
journalctl -u dnsmasq
journalctl -u minidlna

# Service logs
sudo journalctl -u wifi-hotspot.service
```

## 📱 Device Compatibility

### WiFi Hotspot
- ✅ Smartphones (Android, iOS)
- ✅ Tablets (Android, iPad)
- ✅ Laptops (Windows, Mac, Linux)
- ✅ Smart TVs
- ✅ IoT devices (Arduino, ESP32)
- ✅ Chromecast devices

### Screen Casting
- ✅ DLNA-compatible TVs
- ✅ RTSP clients (VLC, FFplay)
- ✅ Web browsers (HLS)
- ✅ Mobile apps

## 🔄 Updates

To update the network monitor suite:

1. **Backup configuration**: `cp -r ~/network_monitor ~/network_monitor.backup`
2. **Update scripts**: Replace with new versions
3. **Reload services**: `sudo systemctl daemon-reload`
4. **Test functionality**: `./launcher.sh`

## 📞 Support

For issues or questions:

1. Check this README
2. Run diagnostics: `./launcher.sh` → Test & Diagnostics
3. Check logs: `journalctl -u [service-name]`
4. Verify prerequisites: `./fix_authentication.sh`

## 📄 License

This project is part of the continuous file streaming solution for CTF challenges.