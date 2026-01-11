# KDE Connect Troubleshooting Guide

## Current Status
✅ **Server (studijko)**: KDE Connect daemon running, 3 devices visible
✅ **Network**: Client connected to hotspot (192.168.200.24)
✅ **Connectivity**: Ping successful, port 1716 open
❌ **Discovery**: Client not visible in KDE Connect

## Troubleshooting Steps

### 1. Check Client Device

**On the client device (192.168.200.24):**

```bash
# Install KDE Connect if not installed
sudo apt install kdeconnect

# Start KDE Connect daemon
kdeconnectd &

# Check if daemon is running
pgrep -f kdeconnectd

# List available devices
kdeconnect-cli --list-devices

# Check if ports are open
netstat -tulpn | grep -E "(1714|1715|1716|9090)"
```

### 2. Check mDNS/Bonjour Services

**On both devices:**

```bash
# Install avahi tools if needed
sudo apt install avahi-utils

# Browse for services
avahi-browse -a -t

# Look for KDE Connect services
avahi-browse -a -t | grep -i kde
```

### 3. Check Firewall Settings

**On client device:**

```bash
# Check if firewall is blocking KDE Connect
sudo ufw status
sudo iptables -L -n | grep -E "(1714|1715|1716|9090)"

# If firewall is active, allow KDE Connect ports
sudo ufw allow 1714:1764/tcp
sudo ufw allow 9090/tcp
sudo ufw allow 5353/udp
```

### 4. Check Network Configuration

**Verify both devices are on same network:**

```bash
# Check IP addresses
ip addr show

# Check routing
ip route show

# Test connectivity
ping 192.168.200.1  # Server
ping 192.168.200.24 # Client
```

### 5. Restart Services

**On both devices:**

```bash
# Stop KDE Connect
pkill -f kdeconnectd

# Start KDE Connect
kdeconnectd &

# Wait a few seconds
sleep 3

# Check devices
kdeconnect-cli --list-devices
```

### 6. Check D-Bus

**On both devices:**

```bash
# Check if D-Bus is running
systemctl status dbus

# Restart D-Bus if needed
sudo systemctl restart dbus

# Check KDE Connect D-Bus service
qdbus --session org.kde.kdeconnect
```

### 7. Manual Connection

**If automatic discovery fails:**

```bash
# On server, try to connect manually
kdeconnect-cli --pair --device 192.168.200.24

# Or use device ID if known
kdeconnect-cli --pair --device <device-id>
```

### 8. Check Logs

**On both devices:**

```bash
# Check KDE Connect logs
journalctl -u kdeconnectd

# Check system logs
journalctl | grep kdeconnect

# Check avahi logs
journalctl -u avahi-daemon
```

## Common Issues and Solutions

### Issue: "No devices found"
**Solution**: 
- Ensure both devices are on same network
- Check firewall settings
- Restart KDE Connect on both devices
- Verify mDNS is working

### Issue: "Device not reachable"
**Solution**:
- Check network connectivity (ping)
- Verify firewall rules
- Check if KDE Connect daemon is running
- Try manual connection

### Issue: "Pairing failed"
**Solution**:
- Ensure both devices have KDE Connect running
- Check that both devices can see each other
- Try restarting services
- Check D-Bus connectivity

### Issue: "Connection lost"
**Solution**:
- Check network stability
- Verify both devices are still connected
- Restart KDE Connect
- Check for network changes

## Testing Commands

### Server (studijko):
```bash
# Check status
~/network_monitor/kdeconnect_helper.sh

# List devices
kdeconnect-cli --list-devices

# Check network
ip neigh show | grep "192.168.200"

# Test connectivity
ping -c 3 192.168.200.24
```

### Client (192.168.200.24):
```bash
# Check KDE Connect
kdeconnect-cli --list-devices

# Check services
avahi-browse -a -t

# Test connectivity
ping -c 3 192.168.200.1
```

## Next Steps

1. **Install KDE Connect on client** if not already installed
2. **Start KDE Connect daemon** on client device
3. **Check firewall settings** on client device
4. **Restart services** on both devices
5. **Try manual pairing** if automatic discovery fails

## Additional Resources

- KDE Connect documentation: https://kdeconnect.kde.org/
- Troubleshooting guide: https://userbase.kde.org/KDEConnect
- Network requirements: https://kdeconnect.kde.org/page/network-requirements