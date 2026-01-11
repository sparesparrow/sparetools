# Nmap Network Scanner Module
# "There is nothing more helpless and irresponsible than a man in the depths
# of an ether binge." - Hunter S. Thompson

# Perform network discovery scan
network_discovery_scan() {
    local target_network="$1"
    local scan_results="/tmp/nmap_discovery_$$.txt"

    gonzo_speak "INITIATING NETWORK DISCOVERY SCAN" "network" "intense"

    # Run nmap ping scan
    nmap $NMAP_OPTIONS "$target_network" > "$scan_results" 2>&1

    # Parse results
    local hosts_up=$(grep -c "Nmap scan report for" "$scan_results" || echo "0")
    local new_hosts=0

    # Check for new hosts
    while IFS= read -r line; do
        if echo "$line" | grep -q "Nmap scan report for"; then
            local host_ip=$(echo "$line" | awk '{print $5}')

            # Check if this is a new host
            if ! grep -q "$host_ip" "$DATA_DIR/known_hosts" 2>/dev/null; then
                gonzo_multi_alert "new_device_discovered" "NEW HOST DISCOVERED: $host_ip"
                echo "$(date '+%Y-%m-%d %H:%M:%S') NEW_HOST $host_ip" >> "$LOGS_DIR/network_events.log"
                echo "$host_ip" >> "$DATA_DIR/known_hosts"
                ((new_hosts++))
            fi
        fi
    done < "$scan_results"

    gonzo_speak "DISCOVERY COMPLETE: $hosts_up HOSTS UP, $new_hosts NEW" "status" "normal"

    # Clean up
    rm -f "$scan_results"
}

# Perform service detection scan on known hosts
service_scan() {
    local target="$1"
    local scan_results="/tmp/nmap_service_$$.txt"

    # Run service detection scan
    nmap -sV --version-intensity 3 -T4 --max-retries 1 "$target" > "$scan_results" 2>&1

    # Parse open ports
    local open_ports=$(grep -E "^[0-9]+/.*open" "$scan_results" | wc -l)

    if (( open_ports > 0 )); then
        gonzo_speak "SERVICE SCAN COMPLETE FOR $target: $open_ports OPEN PORTS" "network" "normal"

        # Check for suspicious services
        if grep -q -E "(telnet|ftp|rlogin)" "$scan_results"; then
            gonzo_multi_alert "threat_detected" "INSECURE SERVICE DETECTED ON $target"
            echo "$(date '+%Y-%m-%d %H:%M:%S') INSECURE_SERVICE $target" >> "$LOGS_DIR/threats.log"
        fi

        # Log service information
        grep -E "^[0-9]+/.*open" "$scan_results" | while IFS= read -r line; do
            echo "$(date '+%Y-%m-%d %H:%M:%S') OPEN_PORT $target $line" >> "$LOGS_DIR/network_events.log"
        done
    fi

    # Clean up
    rm -f "$scan_results"
}

# Perform vulnerability scan (basic)
vulnerability_scan() {
    local target="$1"
    local scan_results="/tmp/nmap_vuln_$$.txt"

    # Run basic vulnerability scan
    nmap --script vuln -T4 --max-retries 1 "$target" > "$scan_results" 2>&1

    # Check for vulnerabilities
    local vuln_count=$(grep -c "VULNERABLE\|vulnerable" "$scan_results" || echo "0")

    if (( vuln_count > 0 )); then
        gonzo_multi_alert "threat_detected" "VULNERABILITIES DETECTED ON $target: $vuln_count issues"
        echo "$(date '+%Y-%m-%d %H:%M:%S') VULNERABILITIES $target $vuln_count" >> "$LOGS_DIR/threats.log"

        # Log specific vulnerabilities
        grep -A 2 -B 1 "VULNERABLE\|vulnerable" "$scan_results" >> "$LOGS_DIR/vulnerabilities.log"
    fi

    # Clean up
    rm -f "$scan_results"
}

# OS detection scan
os_detection_scan() {
    local target="$1"
    local scan_results="/tmp/nmap_os_$$.txt"

    # Run OS detection
    nmap -O -T4 --max-retries 1 "$target" > "$scan_results" 2>&1

    # Parse OS information
    local os_info=$(grep "OS details:" "$scan_results" | head -1 | cut -d: -f2- | xargs)

    if [[ -n "$os_info" ]]; then
        gonzo_speak "OS DETECTED FOR $target: $os_info" "network" "normal"
        echo "$(date '+%Y-%m-%d %H:%M:%S') OS_DETECTED $target $os_info" >> "$LOGS_DIR/network_events.log"
    fi

    # Clean up
    rm -f "$scan_results"
}

# Monitor for unauthorized devices
monitor_unauthorized_devices() {
    local known_hosts_file="$DATA_DIR/authorized_hosts"

    if [[ ! -f "$known_hosts_file" ]]; then
        # First run - create authorized hosts file
        echo "# Authorized network hosts" > "$known_hosts_file"
        echo "# Add authorized IP addresses here, one per line" >> "$known_hosts_file"
        return
    fi

    # Get current network devices
    local current_hosts=$(arp -n | grep -v incomplete | awk '{print $1}' | sort)

    # Check for unauthorized hosts
    while IFS= read -r host; do
        [[ "$host" =~ ^#.*$ ]] && continue  # Skip comments
        [[ -z "$host" ]] && continue       # Skip empty lines

        if ! echo "$current_hosts" | grep -q "^$host$"; then
            gonzo_multi_alert "threat_detected" "AUTHORIZED HOST MISSING: $host"
            echo "$(date '+%Y-%m-%d %H:%M:%S') MISSING_AUTHORIZED $host" >> "$LOGS_DIR/threats.log"
        fi
    done < "$known_hosts_file"

    # Check for unauthorized hosts on network
    while IFS= read -r host; do
        if ! grep -q "^$host$" "$known_hosts_file"; then
            gonzo_multi_alert "threat_detected" "UNAUTHORIZED HOST DETECTED: $host"
            echo "$(date '+%Y-%m-%d %H:%M:%S') UNAUTHORIZED_HOST $host" >> "$LOGS_DIR/threats.log"
        fi
    done <<< "$current_hosts"
}

# Generate network map
generate_network_map() {
    local map_file="$DATA_DIR/network_map_$(date +%Y%m%d).txt"

    echo "=== NETWORK MAP ===" > "$map_file"
    echo "Generated: $(date)" >> "$map_file"
    echo "" >> "$map_file"

    # Get all known devices
    echo "Known Devices:" >> "$map_file"
    if [[ -f "$DATA_DIR/known_hosts" ]]; then
        cat "$DATA_DIR/known_hosts" >> "$map_file"
    fi

    echo "" >> "$map_file"
    echo "Current ARP Table:" >> "$map_file"
    arp -n >> "$map_file"

    echo "" >> "$map_file"
    echo "Network Routes:" >> "$map_file"
    ip route show >> "$map_file"

    gonzo_speak "NETWORK MAP GENERATED" "status" "normal"
}

# Main network scanning function
network_scan() {
    # Scan configured target networks
    for network in "${NMAP_TARGETS[@]}"; do
        network_discovery_scan "$network"
    done

    # Perform deeper scans on discovered hosts
    if [[ -f "$DATA_DIR/known_hosts" ]]; then
        while IFS= read -r host; do
            [[ "$host" =~ ^#.*$ ]] && continue
            [[ -z "$host" ]] && continue

            # Run scans in parallel
            service_scan "$host" &
            os_detection_scan "$host" &
            vulnerability_scan "$host" &
        done < "$DATA_DIR/known_hosts"

        # Wait for all scans to complete
        wait
    fi

    # Monitor for unauthorized devices
    monitor_unauthorized_devices

    # Generate network map periodically
    generate_network_map
}

# Initialize known hosts file
init_known_hosts() {
    touch "$DATA_DIR/known_hosts"
}