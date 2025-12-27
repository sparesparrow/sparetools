# Multi-Interface Network Monitor
# "The possibility of physical and mental collapse is now very real.
# No sympathy for the devil, keep that in mind." - Hunter S. Thompson

# Detect active network interfaces
detect_interfaces() {
    local interfaces_found=0

    # Get all interfaces (excluding loopback and excluded ones)
    while IFS= read -r line; do
        local iface=$(echo "$line" | awk '{print $2}' | sed 's/://')

        # Skip excluded interfaces
        local skip=false
        for excluded in "${EXCLUDED_INTERFACES[@]}"; do
            if [[ "$iface" == "$excluded" ]]; then
                skip=true
                break
            fi
        done

        if [[ "$skip" == false ]] && [[ -n "$iface" ]]; then
            # Check if interface is up
            if echo "$line" | grep -q "UP"; then
                ACTIVE_INTERFACES["$iface"]=1
                ((interfaces_found++))
                echo "Interface $iface is active"
            fi
        fi
    done < <(ip link show | grep -E "^[0-9]+:")

    gonzo_speak "FOUND $interfaces_found ACTIVE INTERFACES" "system" "normal"
}

# Monitor gateway status for all interfaces
monitor_gateways() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        local current_gateway=$(ip route show dev "$iface" 2>/dev/null | grep default | awk '{print $3}' | head -1)
        local previous_status="${GATEWAY_STATUS[$iface]}"

        if [[ -n "$current_gateway" ]] && [[ "$previous_status" != "up:$current_gateway" ]]; then
            # Gateway found or changed
            if [[ -n "$previous_status" ]]; then
                gonzo_multi_alert "gateway_breach" "GATEWAY CHANGED ON $iface: $previous_status -> $current_gateway"
            else
                gonzo_multi_alert "gateway_found" "GATEWAY FOUND ON $iface: $current_gateway"
            fi
            GATEWAY_STATUS["$iface"]="up:$current_gateway"

            # Log event
            echo "$(date '+%Y-%m-%d %H:%M:%S') GATEWAY $iface $current_gateway" >> "$LOGS_DIR/network_events.log"

        elif [[ -z "$current_gateway" ]] && [[ "$previous_status" == up:* ]]; then
            # Gateway lost
            local old_gateway=$(echo "$previous_status" | cut -d: -f2)
            gonzo_multi_alert "gateway_breach" "GATEWAY LOST ON $iface: $old_gateway"
            GATEWAY_STATUS["$iface"]="down"

            # Log event
            echo "$(date '+%Y-%m-%d %H:%M:%S') GATEWAY_LOST $iface $old_gateway" >> "$LOGS_DIR/network_events.log"
        fi
    done
}

# Monitor ARP table for device discovery
monitor_devices() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        # Get current ARP table for this interface
        local current_devices=$(arp -n -i "$iface" 2>/dev/null | grep -v incomplete | awk '{print $1}' | sort)
        local known_devices="${KNOWN_DEVICES[$iface]}"

        if [[ -z "$known_devices" ]]; then
            # First run - initialize known devices
            KNOWN_DEVICES["$iface"]="$current_devices"
            continue
        fi

        # Find new devices
        local new_devices=""
        while IFS= read -r device; do
            if ! echo "$known_devices" | grep -q "^$device$"; then
                new_devices="$new_devices $device"
            fi
        done <<< "$current_devices"

        # Find disappeared devices
        local gone_devices=""
        while IFS= read -r device; do
            if ! echo "$current_devices" | grep -q "^$device$"; then
                gone_devices="$gone_devices $device"
            fi
        done <<< "$known_devices"

        # Alert for new devices
        if [[ -n "$new_devices" ]]; then
            for device in $new_devices; do
                gonzo_multi_alert "new_device_discovered" "NEW DEVICE ON $iface: $device"
                echo "$(date '+%Y-%m-%d %H:%M:%S') NEW_DEVICE $iface $device" >> "$LOGS_DIR/network_events.log"
            done
            # Update known devices
            KNOWN_DEVICES["$iface"]="$current_devices"
        fi

        # Alert for disappeared devices
        if [[ -n "$gone_devices" ]]; then
            gonzo_speak "DEVICES DISAPPEARED FROM $iface!" "device" "ominous"
            for device in $gone_devices; do
                echo "$(date '+%Y-%m-%d %H:%M:%S') DEVICE_GONE $iface $device" >> "$LOGS_DIR/network_events.log"
            done
            # Update known devices
            KNOWN_DEVICES["$iface"]="$current_devices"
        fi
    done
}

# Monitor DHCP activity
monitor_dhcp() {
    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        # Check for DHCP server responses (BOOTP/DHCP packets)
        local dhcp_activity=$(tcpdump -i "$iface" -c 1 -n port 67 or port 68 2>/dev/null | wc -l)

        if (( dhcp_activity > 0 )); then
            gonzo_speak "DHCP ACTIVITY DETECTED ON $iface" "network" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') DHCP $iface" >> "$LOGS_DIR/network_events.log"
        fi
    done
}

# Main interface monitoring function
monitor_interfaces() {
    monitor_gateways
    monitor_devices
    monitor_dhcp
}

# Save known devices to persistent storage
save_known_devices() {
    > "$DATA_DIR/known_devices.db"
    for iface in "${!KNOWN_DEVICES[@]}"; do
        echo "$iface=${KNOWN_DEVICES[$iface]}" >> "$DATA_DIR/known_devices.db"
    done
}

# Get interface statistics
get_interface_stats() {
    local iface="$1"
    local stats=$(ip -s link show "$iface" 2>/dev/null)

    if [[ -n "$stats" ]]; then
        local rx_packets=$(echo "$stats" | grep "RX:" | head -1 | awk '{print $2}')
        local tx_packets=$(echo "$stats" | grep "TX:" | head -1 | awk '{print $2}')
        local rx_bytes=$(echo "$stats" | grep "RX:" | head -1 | awk '{print $6}')
        local tx_bytes=$(echo "$stats" | grep "TX:" | head -1 | awk '{print $6}')

        echo "Interface: $iface"
        echo "RX: $rx_packets packets, $rx_bytes bytes"
        echo "TX: $tx_packets packets, $tx_bytes bytes"
    fi
}

# Monitor interface status changes
monitor_interface_status() {
    local current_interfaces=$(ip link show | grep -E "^[0-9]+:" | grep "UP" | awk '{print $2}' | sed 's/://' | grep -v lo)

    for iface in "${!ACTIVE_INTERFACES[@]}"; do
        if ! echo "$current_interfaces" | grep -q "^$iface$"; then
            # Interface went down
            gonzo_speak "INTERFACE $iface WENT DOWN!" "threat" "urgent"
            unset ACTIVE_INTERFACES["$iface"]
            echo "$(date '+%Y-%m-%d %H:%M:%S') INTERFACE_DOWN $iface" >> "$LOGS_DIR/network_events.log"
        fi
    done

    # Check for newly activated interfaces
    for iface in $current_interfaces; do
        if [[ ! -v ACTIVE_INTERFACES["$iface"] ]]; then
            # New interface activated
            ACTIVE_INTERFACES["$iface"]=1
            gonzo_speak "NEW INTERFACE ACTIVATED: $iface" "system" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') INTERFACE_UP $iface" >> "$LOGS_DIR/network_events.log"
        fi
    done
}