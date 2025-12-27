# ASCII Network Topology Visualization
# "The highways are crowded with people who drive as if they know where they're going."
# - Hunter S. Thompson

# Generate ASCII network topology
generate_topology_ascii() {
    local topology_file="$DATA_DIR/topology_$(date +%Y%m%d_%H%M%S).txt"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" > "$topology_file"
    echo "║                        NETWORK TOPOLOGY MAP                               ║" >> "$topology_file"
    echo "║                        $(date)                              ║" >> "$topology_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$topology_file"
    echo "" >> "$topology_file"

    # Get gateway information
    echo "🌐 GATEWAYS:" >> "$topology_file"
    for iface in "${!GATEWAY_STATUS[@]}"; do
        local status="${GATEWAY_STATUS[$iface]}"
        if [[ "$status" == up:* ]]; then
            local gateway_ip=$(echo "$status" | cut -d: -f2)
            echo "   └─ $iface → $gateway_ip [ONLINE]" >> "$topology_file"
        else
            echo "   └─ $iface → [OFFLINE]" >> "$topology_file"
        fi
    done
    echo "" >> "$topology_file"

    # Get device information
    echo "🖥️  DEVICES:" >> "$topology_file"
    local device_count=0
    for iface in "${!KNOWN_DEVICES[@]}"; do
        echo "   └─ $iface:" >> "$topology_file"
        local devices="${KNOWN_DEVICES[$iface]}"

        if [[ -n "$devices" ]]; then
            while IFS= read -r device; do
                [[ -z "$device" ]] && continue
                echo "      ├─ $device" >> "$topology_file"
                ((device_count++))
            done <<< "$devices"
        else
            echo "      ├─ (no devices)" >> "$topology_file"
        fi
    done
    echo "   Total Devices: $device_count" >> "$topology_file"
    echo "" >> "$topology_file"

    # Network services status
    echo "🔧 SERVICES:" >> "$topology_file"
    if command -v tcpdump >/dev/null 2>&1; then
        echo "   ├─ Packet Capture: ✅ ACTIVE" >> "$topology_file"
    else
        echo "   ├─ Packet Capture: ❌ UNAVAILABLE" >> "$topology_file"
    fi

    if command -v tshark >/dev/null 2>&1; then
        echo "   ├─ Deep Analysis: ✅ ACTIVE" >> "$topology_file"
    else
        echo "   ├─ Deep Analysis: ❌ UNAVAILABLE" >> "$topology_file"
    fi

    if command -v nft >/dev/null 2>&1; then
        echo "   ├─ Firewall Monitor: ✅ ACTIVE" >> "$topology_file"
    else
        echo "   ├─ Firewall Monitor: ❌ UNAVAILABLE" >> "$topology_file"
    fi

    if command -v nmap >/dev/null 2>&1; then
        echo "   └─ Network Scanner: ✅ ACTIVE" >> "$topology_file"
    else
        echo "   └─ Network Scanner: ❌ UNAVAILABLE" >> "$topology_file"
    fi
    echo "" >> "$topology_file"

    # Threat level indicator
    local threat_level="green"
    local threat_count=$(wc -l < "$LOGS_DIR/threats.log" 2>/dev/null || echo "0")

    if (( threat_count > 10 )); then
        threat_level="red"
    elif (( threat_count > 5 )); then
        threat_level="yellow"
    fi

    echo "🚨 THREAT LEVEL:" >> "$topology_file"
    case "$threat_level" in
        "red")
            echo "   ┌─ DANGER ─┐" >> "$topology_file"
            echo "   │  🔴 RED  │ $threat_count threats detected" >> "$topology_file"
            echo "   └─────────┘" >> "$topology_file"
            ;;
        "yellow")
            echo "   ┌─ CAUTION ─┐" >> "$topology_file"
            echo "   │  🟡 YELLOW │ $threat_count threats detected" >> "$topology_file"
            echo "   └───────────┘" >> "$topology_file"
            ;;
        "green")
            echo "   ┌─ NORMAL ─┐" >> "$topology_file"
            echo "   │  🟢 GREEN  │ All clear" >> "$topology_file"
            echo "   └─────────┘" >> "$topology_file"
            ;;
    esac
    echo "" >> "$topology_file"

    # Recent activity
    echo "📊 RECENT ACTIVITY:" >> "$topology_file"
    tail -5 "$LOGS_DIR/network_events.log" 2>/dev/null | while IFS= read -r line; do
        echo "   └─ $line" >> "$topology_file"
    done
    echo "" >> "$topology_file"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" >> "$topology_file"
    echo "║ \"The edge... there is no honest way to explain it because the only       ║" >> "$topology_file"
    echo "║  people who really know where it is are the ones who have gone over.\"    ║" >> "$topology_file"
    echo "║                           - Hunter S. Thompson                           ║" >> "$topology_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$topology_file"

    # Display the topology
    cat "$topology_file"

    gonzo_speak "NETWORK TOPOLOGY UPDATED" "status" "normal"
}

# Generate real-time packet flow visualization
generate_packet_flow() {
    local flow_file="/tmp/packet_flow_$$.txt"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" > "$flow_file"
    echo "║                         PACKET FLOW MONITOR                               ║" >> "$flow_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$flow_file"
    echo "" >> "$flow_file"

    # Get current packet statistics
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        local stats=$(ip -s link show "$iface" 2>/dev/null | grep "RX:\|TX:" | tail -2)

        if [[ -n "$stats" ]]; then
            echo "Interface: $iface" >> "$flow_file"
            echo "$stats" >> "$flow_file"
            echo "" >> "$flow_file"
        fi
    done

    # Show recent packet captures (if available)
    if [[ -f "$LOGS_DIR/network_events.log" ]]; then
        echo "Recent Packet Events:" >> "$flow_file"
        grep "PACKET_\|PORT_\|BROADCAST" "$LOGS_DIR/network_events.log" | tail -5 >> "$flow_file"
    fi

    cat "$flow_file"
    rm -f "$flow_file"
}

# Generate threat visualization
generate_threat_map() {
    local threat_file="$DATA_DIR/threat_map_$(date +%Y%m%d_%H%M%S).txt"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" > "$threat_file"
    echo "║                           THREAT INTELLIGENCE                             ║" >> "$threat_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$threat_file"
    echo "" >> "$threat_file"

    # Threat statistics
    local total_threats=$(wc -l < "$LOGS_DIR/threats.log" 2>/dev/null || echo "0")
    local recent_threats=$(grep -c "$(date +%Y-%m-%d)" "$LOGS_DIR/threats.log" 2>/dev/null || echo "0")

    echo "📈 THREAT STATISTICS:" >> "$threat_file"
    echo "   └─ Total Threats: $total_threats" >> "$threat_file"
    echo "   └─ Today's Threats: $recent_threats" >> "$threat_file"
    echo "" >> "$threat_file"

    # Threat types breakdown
    echo "🎯 THREAT TYPES:" >> "$threat_file"
    if [[ -f "$LOGS_DIR/threats.log" ]]; then
        local port_scans=$(grep -c "PORT_SCAN" "$LOGS_DIR/threats.log")
        local anomalies=$(grep -c "PACKET_ANOMALY\|PACKET_STORM" "$LOGS_DIR/threats.log")
        local brute_force=$(grep -c "BRUTE_FORCE" "$LOGS_DIR/threats.log")
        local suspicious=$(grep -c "SUSPICIOUS_PAYLOAD\|INSECURE_SERVICE" "$LOGS_DIR/threats.log")

        echo "   ├─ Port Scans: $port_scans" >> "$threat_file"
        echo "   ├─ Packet Anomalies: $anomalies" >> "$threat_file"
        echo "   ├─ Brute Force Attempts: $brute_force" >> "$threat_file"
        echo "   └─ Suspicious Activity: $suspicious" >> "$threat_file"
    fi
    echo "" >> "$threat_file"

    # Recent threats
    echo "🚨 RECENT THREATS:" >> "$threat_file"
    tail -10 "$LOGS_DIR/threats.log" 2>/dev/null | while IFS= read -r line; do
        echo "   └─ $line" >> "$threat_file"
    done

    cat "$threat_file"
    gonzo_speak "THREAT MAP UPDATED" "threat" "ominous"
}

# Generate gonzo-style incident report
generate_incident_report() {
    local incident_file="$LOGS_DIR/incident_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "╔══════════════════════════════════════════════════════════════════════════════╗" > "$incident_file"
    echo "║                    GONZO NETWORK INCIDENT REPORT                          ║" >> "$incident_file"
    echo "║                    \"Fear and Loathing in Cyberspace\"                      ║" >> "$incident_file"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝" >> "$incident_file"
    echo "" >> "$incident_file"
    echo "INCIDENT COMMANDER: Enhanced Network Monitor v2.0" >> "$incident_file"
    echo "REPORT DATE: $(date)" >> "$incident_file"
    echo "CLASSIFICATION: TOP SECRET - EYES ONLY" >> "$incident_file"
    echo "" >> "$incident_file"

    echo "EXECUTIVE SUMMARY:" >> "$incident_file"
    echo "The wires have been burning with activity. We've been watching the traffic" >> "$incident_file"
    echo "flow like a paranoid hawk, and here's what we've seen in the shadows..." >> "$incident_file"
    echo "" >> "$incident_file"

    # Network status
    local iface_count="${#ACTIVE_INTERFACES[@]}"
    echo "NETWORK STATUS:" >> "$incident_file"
    echo "Active interfaces under surveillance: $iface_count" >> "$incident_file"
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        echo "  - $iface: OPERATIONAL" >> "$incident_file"
    done
    echo "" >> "$incident_file"

    # Critical events
    echo "CRITICAL EVENTS:" >> "$incident_file"
    if [[ -f "$LOGS_DIR/threats.log" ]] && [[ -s "$LOGS_DIR/threats.log" ]]; then
        tail -20 "$LOGS_DIR/threats.log" | while IFS= read -r line; do
            echo "  ⚠️  $line" >> "$incident_file"
        done
    else
        echo "  ✅ No critical threats detected. The network sleeps... for now." >> "$incident_file"
    fi
    echo "" >> "$incident_file"

    echo "RECOMMENDATIONS:" >> "$incident_file"
    echo "1. Keep watching the wires - they never stop talking." >> "$incident_file"
    echo "2. Trust no one, suspect everyone on the network." >> "$incident_file"
    echo "3. When in doubt, capture more packets." >> "$incident_file"
    echo "4. The edge is always closer than you think." >> "$incident_file"
    echo "" >> "$incident_file"

    echo "END OF REPORT" >> "$incident_file"
    echo "Stay paranoid. Stay vigilant." >> "$incident_file"
    echo "" >> "$incident_file"
    echo "- The Network Monitor" >> "$incident_file"

    cat "$incident_file"
    gonzo_speak "GONZO INCIDENT REPORT FILED" "threat" "dramatic"
}

# Update topology visualization
update_topology() {
    generate_topology_ascii
    generate_threat_map
    generate_incident_report
}

# Display current status in terminal
display_status() {
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                   ENHANCED NETWORK MONITOR - ACTIVE                       ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Status: $(date)"
    echo "Active Interfaces: ${#ACTIVE_INTERFACES[@]}"
    echo "Known Devices: $(cat "${KNOWN_DEVICES[@]}" 2>/dev/null | wc -w || echo "0")"
    echo "Threats Detected: $(wc -l < "$LOGS_DIR/threats.log" 2>/dev/null || echo "0")"
    echo ""
    echo "Recent Events:"
    tail -5 "$LOGS_DIR/network_events.log" 2>/dev/null || echo "No events yet"
    echo ""
    echo "Press Ctrl+C to exit"
}