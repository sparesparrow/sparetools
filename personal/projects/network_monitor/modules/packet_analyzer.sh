# Advanced Packet Analysis Module
# "The TV business is uglier than most things.
# It is normally perceived as some kind of cruel joke." - Hunter S. Thompson

# Global variables for destination tracking
declare -A DESTINATION_COUNTS
declare -A DESTINATION_TIMESTAMPS
declare -A HOTSPOT_DEVICES
LAST_DESTINATION_UPDATE=0

# Analyze packets with tcpdump
analyze_packets_tcpdump() {
    local iface="$1"
    local duration="${2:-$PACKET_CAPTURE_DURATION}"

    # Capture packets with tcpdump
    local capture_file="/tmp/packet_capture_$$.pcap"
    local analysis_file="/tmp/packet_analysis_$$.txt"

    # Start packet capture
    timeout "$duration" tcpdump -i "$iface" -w "$capture_file" -c "$MAX_PACKETS_PER_CAPTURE" "$PACKET_FILTER" >/dev/null 2>&1

    if [[ -f "$capture_file" ]] && [[ -s "$capture_file" ]]; then
        # Analyze captured packets
        tcpdump -r "$capture_file" -n -q 2>/dev/null | head -20 > "$analysis_file"

        # Look for suspicious patterns
        local suspicious_count=$(grep -c -E "(syn|rst|fin)" "$analysis_file" 2>/dev/null || echo "0")
        local port_scan_count=$(grep -c -E ">[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" "$analysis_file" 2>/dev/null || echo "0")

        # Alert on anomalies
        if (( suspicious_count > 10 )); then
            gonzo_multi_alert "packet_anomaly" "HIGH TCP FLAG ACTIVITY ON $iface: $suspicious_count packets"
            echo "$(date '+%Y-%m-%d %H:%M:%S') PACKET_ANOMALY $iface tcp_flags $suspicious_count" >> "$LOGS_DIR/threats.log"
        fi

        if (( port_scan_count > 5 )); then
            gonzo_multi_alert "threat_detected" "PORT SCAN DETECTED ON $iface: $port_scan_count connections"
            echo "$(date '+%Y-%m-%d %H:%M:%S') PORT_SCAN $iface $port_scan_count" >> "$LOGS_DIR/threats.log"
        fi

        # Log packet summary
        local total_packets=$(tcpdump -r "$capture_file" 2>/dev/null | wc -l)
        echo "$(date '+%Y-%m-%d %H:%M:%S') PACKET_CAPTURE $iface $total_packets packets" >> "$LOGS_DIR/network_events.log"

        # Clean up
        rm -f "$capture_file" "$analysis_file"
    fi
}

# Deep packet inspection with tshark
analyze_packets_tshark() {
    local iface="$1"

    # Use tshark for detailed protocol analysis
    local protocols=$(timeout 10 tshark -i "$iface" -a duration:10 -q -z conv,ip 2>/dev/null | head -10)

    if [[ -n "$protocols" ]]; then
        # Analyze protocol distribution
        local http_count=$(echo "$protocols" | grep -c "80\|443" || echo "0")
        local dns_count=$(echo "$protocols" | grep -c "53" || echo "0")
        local ssh_count=$(echo "$protocols" | grep -c "22" || echo "0")

        # Alert on unusual protocol activity
        if (( http_count > 50 )); then
            gonzo_speak "HIGH HTTP/HTTPS TRAFFIC DETECTED" "network" "normal"
        fi

        if (( dns_count > 20 )); then
            gonzo_speak "INTENSE DNS ACTIVITY" "network" "normal"
        fi

        # Log protocol analysis
        echo "$(date '+%Y-%m-%d %H:%M:%S') PROTOCOL_ANALYSIS $iface HTTP:$http_count DNS:$dns_count SSH:$ssh_count" >> "$LOGS_DIR/network_events.log"
    fi
}

# Monitor for packet storms
detect_packet_storms() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        # Get packet rate over 5 seconds
        local packets_before=$(ip -s link show "$iface" | grep "RX:" | head -1 | awk '{print $2}')
        sleep 5
        local packets_after=$(ip -s link show "$iface" | grep "RX:" | head -1 | awk '{print $2}')

        local packet_rate=$(( (packets_after - packets_before) / 5 ))

        if (( packet_rate > 1000 )); then
            gonzo_multi_alert "packet_anomaly" "PACKET STORM ON $iface: $packet_rate packets/sec"
            echo "$(date '+%Y-%m-%d %H:%M:%S') PACKET_STORM $iface $packet_rate" >> "$LOGS_DIR/threats.log"
        fi
    done
}

# Analyze packet sizes for anomalies
analyze_packet_sizes() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        local large_packets=$(timeout 10 tcpdump -i "$iface" -c 50 -n "greater 1400" 2>/dev/null | wc -l)

        if (( large_packets > 10 )); then
            gonzo_speak "LARGE PACKETS DETECTED ON $iface: $large_packets oversized packets" "network" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') LARGE_PACKETS $iface $large_packets" >> "$LOGS_DIR/network_events.log"
        fi
    done
}

# Monitor broadcast/multicast traffic
monitor_broadcast_traffic() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        local broadcast_count=$(timeout 10 tcpdump -i "$iface" -c 100 "broadcast or multicast" 2>/dev/null | wc -l)

        if (( broadcast_count > 20 )); then
            gonzo_speak "HIGH BROADCAST/MULTICAST TRAFFIC ON $iface: $broadcast_count packets" "network" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') BROADCAST_TRAFFIC $iface $broadcast_count" >> "$LOGS_DIR/network_events.log"
        fi
    done
}

# Extract and analyze packet payloads (carefully)
analyze_packet_payloads() {
    local iface="$1"

    # Look for suspicious strings in packets (basic pattern matching)
    local suspicious_patterns=("password" "admin" "root" "exploit" "shell" "cmd")

    for pattern in "${suspicious_patterns[@]}"; do
        local matches=$(timeout 10 tcpdump -i "$iface" -c 100 -X -s 256 "tcp" 2>/dev/null | grep -i "$pattern" | wc -l)

        if (( matches > 0 )); then
            gonzo_multi_alert "threat_detected" "SUSPICIOUS PAYLOAD DETECTED: '$pattern' found in $matches packets on $iface"
            echo "$(date '+%Y-%m-%d %H:%M:%S') SUSPICIOUS_PAYLOAD $iface $pattern $matches" >> "$LOGS_DIR/threats.log"
        fi
    done
}

# Track destination addresses for hotspot monitoring
track_destination_addresses() {
    local iface="$1"
    local duration="${2:-$PACKET_CAPTURE_DURATION}"

    # Capture packets and extract destination addresses
    local capture_file="/tmp/dest_capture_$$.pcap"
    local dest_file="/tmp/destinations_$$.txt"

    # Capture packets with destination IP focus
    timeout "$duration" tcpdump -i "$iface" -w "$capture_file" -c 500 "ip" >/dev/null 2>&1

    if [[ -f "$capture_file" ]] && [[ -s "$capture_file" ]]; then
        # Extract destination IPs
        tcpdump -r "$capture_file" -n -q "ip" 2>/dev/null | awk '{print $5}' | cut -d. -f1-4 | sort | uniq -c | sort -nr > "$dest_file"

        # Update destination counts
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            local count=$(echo "$line" | awk '{print $1}')
            local dest_ip=$(echo "$line" | awk '{print $2}')

            # Update global destination tracking
            if [[ -n "${DESTINATION_COUNTS[$dest_ip]}" ]]; then
                DESTINATION_COUNTS[$dest_ip]=$((DESTINATION_COUNTS[$dest_ip] + count))
            else
                DESTINATION_COUNTS[$dest_ip]=$count
            fi

            DESTINATION_TIMESTAMPS[$dest_ip]=$(date +%s)
        done < "$dest_file"

        # Log destination activity
        echo "$(date '+%Y-%m-%d %H:%M:%S') DESTINATION_TRACKING $iface $(wc -l < "$dest_file") unique destinations" >> "$LOGS_DIR/network_events.log"

        # Clean up
        rm -f "$capture_file" "$dest_file"
    fi
}

# Monitor hotspot device connections/disconnections
monitor_hotspot_devices() {
    local iface="$1"

    # Initialize hotspot tracking if not already done
    if [[ -z "${HOTSPOT_DEVICES[initialized]}" ]]; then
        HOTSPOT_DEVICES[initialized]="true"
        gonzo_multi_alert "hotspot_tracking_active" "HOTSPOT MONITORING ACTIVE ON $iface"
        echo "$(date '+%Y-%m-%d %H:%M:%S') HOTSPOT_MONITORING_STARTED $iface" >> "$LOGS_DIR/network_events.log"
    fi

    # Get current connected devices
    local current_devices=$(iw dev "$iface" station dump 2>/dev/null | grep "Station" | awk '{print $2}' | sort)

    # Check for new devices
    for device in $current_devices; do
        if [[ -z "${HOTSPOT_DEVICES[$device]}" ]]; then
            # New device connected
            HOTSPOT_DEVICES[$device]="connected"
            gonzo_multi_alert "hotspot_new_device" "HOTSPOT DEVICE CONNECTED: $device"
            echo "$(date '+%Y-%m-%d %H:%M:%S') HOTSPOT_DEVICE_CONNECTED $iface $device" >> "$LOGS_DIR/network_events.log"
        fi
    done

    # Check for disconnected devices
    for device in "${!HOTSPOT_DEVICES[@]}"; do
        if [[ "${HOTSPOT_DEVICES[$device]}" == "connected" ]] && ! echo "$current_devices" | grep -q "$device"; then
            # Device disconnected
            HOTSPOT_DEVICES[$device]="disconnected"
            gonzo_multi_alert "hotspot_device_gone" "HOTSPOT DEVICE DISCONNECTED: $device"
            echo "$(date '+%Y-%m-%d %H:%M:%S') HOTSPOT_DEVICE_DISCONNECTED $iface $device" >> "$LOGS_DIR/network_events.log"
        fi
    done
}

# Generate real-time destination address visualization
visualize_destinations() {
    local now=$(date +%s)

    # Only update visualization every 10 seconds to avoid spam
    if (( now - LAST_DESTINATION_UPDATE < 10 )); then
        return
    fi

    LAST_DESTINATION_UPDATE=$now

    # Create destination visualization
    local viz_file="/tmp/dest_viz_$$.txt"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" > "$viz_file"
    echo "║                  HOTSPOT DESTINATION ADDRESS MONITOR                      ║" >> "$viz_file"
    echo "║                  $(date)                                     ║" >> "$viz_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$viz_file"
    echo "" >> "$viz_file"

    # Show top destinations
    echo "🎯 TOP DESTINATION ADDRESSES:" >> "$viz_file"

    local count=0
    for dest in "${!DESTINATION_COUNTS[@]}"; do
        if (( count >= 10 )); then
            break
        fi

        local packet_count="${DESTINATION_COUNTS[$dest]}"
        local last_seen="${DESTINATION_TIMESTAMPS[$dest]}"
        local age=$((now - last_seen))

        # Format age
        local age_str
        if (( age < 60 )); then
            age_str="${age}s ago"
        elif (( age < 3600 )); then
            age_str="$((age/60))m ago"
        else
            age_str="$((age/3600))h ago"
        fi

        printf "   ├─ %-15s │ %6d packets │ %s\n" "$dest" "$packet_count" "$age_str" >> "$viz_file"
        ((count++))
    done

    if (( count == 0 )); then
        echo "   ├─ No destinations tracked yet" >> "$viz_file"
    fi

    echo "" >> "$viz_file"

    # Show hotspot device status
    echo "📱 HOTSPOT DEVICES:" >> "$viz_file"
    local device_count=0
    for device in "${!HOTSPOT_DEVICES[@]}"; do
        if [[ "${HOTSPOT_DEVICES[$device]}" == "connected" ]]; then
            echo "   ├─ $device [CONNECTED]" >> "$viz_file"
            ((device_count++))
        fi
    done

    if (( device_count == 0 )); then
        echo "   ├─ No devices connected" >> "$viz_file"
    fi

    echo "   └─ Total Connected: $device_count" >> "$viz_file"
    echo "" >> "$viz_file"

    echo "🌐 PACKET FLOW ACTIVITY:" >> "$viz_file"
    local total_packets=0
    for count in "${DESTINATION_COUNTS[@]}"; do
        total_packets=$((total_packets + count))
    done
    echo "   └─ Total Packets Tracked: $total_packets" >> "$viz_file"

    # Display the visualization
    cat "$viz_file"
    rm -f "$viz_file"
}

# Main packet analysis function
analyze_packets() {
    detect_packet_storms

    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        # Check if this is the hotspot interface (wlan0 in master mode)
        local is_hotspot=false
        if [[ "$iface" == "wlan0" ]] && iwconfig "$iface" 2>/dev/null | grep -q "Mode:Master"; then
            is_hotspot=true
        fi

        # Run analyses in parallel for better performance
        analyze_packets_tcpdump "$iface" &
        analyze_packets_tshark "$iface" &
        analyze_packet_sizes "$iface" &
        monitor_broadcast_traffic "$iface" &
        analyze_packet_payloads "$iface" &

        # Add hotspot-specific monitoring
        if [[ "$is_hotspot" == "true" ]]; then
            track_destination_addresses "$iface" &
            monitor_hotspot_devices "$iface" &
        fi
    done

    # Wait for all analyses to complete (with timeout)
    wait

    # Update destination visualization for hotspot interfaces
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        if [[ "$iface" == "wlan0" ]] && iwconfig "$iface" 2>/dev/null | grep -q "Mode:Master"; then
            visualize_destinations
            break
        fi
    done
}

# Generate packet analysis report
generate_packet_report() {
    local report_file="$LOGS_DIR/packet_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "=== PACKET ANALYSIS REPORT ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"

    echo "Recent Network Events:" >> "$report_file"
    tail -20 "$LOGS_DIR/network_events.log" >> "$report_file"

    echo "" >> "$report_file"
    echo "Recent Threats:" >> "$report_file"
    tail -10 "$LOGS_DIR/threats.log" >> "$report_file"

    echo "" >> "$report_file"
    echo "Interface Statistics:" >> "$report_file"
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        echo "--- $iface ---" >> "$report_file"
        get_interface_stats "$iface" >> "$report_file"
        echo "" >> "$report_file"
    done

    gonzo_speak "PACKET ANALYSIS REPORT GENERATED" "status" "normal"
}