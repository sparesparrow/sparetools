# Nftables Firewall Monitor
# "The mind is its own place, and in itself can make a heaven of hell,
# a hell of heaven." - John Milton (but Hunter S. Thompson would agree)

# Monitor nftables rules and events
monitor_nftables_rules() {
    # Get current nftables configuration
    local current_rules=$(nft list ruleset 2>/dev/null)

    if [[ -z "$current_rules" ]]; then
        return  # nftables not configured or not running
    fi

    # Check for suspicious rules
    local drop_rules=$(echo "$current_rules" | grep -c "drop\|reject" || echo "0")
    local accept_rules=$(echo "$current_rules" | grep -c "accept" || echo "0")

    # Alert if firewall is too permissive
    if (( accept_rules > drop_rules * 2 )); then
        gonzo_speak "FIREWALL LOOKS PERMISSIVE - TOO MANY ACCEPT RULES" "threat" "ominous"
        echo "$(date '+%Y-%m-%d %H:%M:%S') FIREWALL_PERMISSIVE accept:$accept_rules drop:$drop_rules" >> "$LOGS_DIR/threats.log"
    fi

    # Check for rules allowing everything
    if echo "$current_rules" | grep -q "accept.*0.0.0.0/0"; then
        gonzo_multi_alert "threat_detected" "FIREWALL RULE ALLOWS ALL TRAFFIC FROM ANYWHERE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') FIREWALL_OPEN accept_all" >> "$LOGS_DIR/threats.log"
    fi
}

# Monitor firewall counters
monitor_nftables_counters() {
    for table in "${NFTABLES_TABLES[@]}"; do
        for chain in "${NFTABLES_CHAINS[@]}"; do
            # Get chain counters
            local counters=$(nft list chain "$table" "$chain" 2>/dev/null | grep -E "packets.*bytes" || true)

            if [[ -n "$counters" ]]; then
                local packets=$(echo "$counters" | awk '{print $1}')
                local bytes=$(echo "$counters" | awk '{print $3}')

                # Alert on high packet counts (potential attack)
                if [[ -n "$packets" ]] && (( packets > 10000 )); then
                    gonzo_speak "HIGH PACKET COUNT IN $table/$chain: $packets packets" "threat" "urgent"
                    echo "$(date '+%Y-%m-%d %H:%M:%S') HIGH_PACKETS $table $chain $packets" >> "$LOGS_DIR/threats.log"
                fi

                # Log counters periodically
                echo "$(date '+%Y-%m-%d %H:%M:%S') COUNTERS $table $chain packets:$packets bytes:$bytes" >> "$LOGS_DIR/network_events.log"
            fi
        done
    done
}

# Monitor for firewall rule changes
monitor_rule_changes() {
    local current_rules_file="/tmp/current_nftables_rules_$$"
    local previous_rules_file="$DATA_DIR/previous_nftables_rules"

    # Save current ruleset
    nft list ruleset > "$current_rules_file" 2>/dev/null

    if [[ -f "$previous_rules_file" ]]; then
        # Compare with previous ruleset
        if ! diff -q "$current_rules_file" "$previous_rules_file" >/dev/null 2>&1; then
            gonzo_multi_alert "threat_detected" "NFTABLES RULESET CHANGED!"
            echo "$(date '+%Y-%m-%d %H:%M:%S') RULESET_CHANGED" >> "$LOGS_DIR/threats.log"

            # Show what changed
            diff "$previous_rules_file" "$current_rules_file" >> "$LOGS_DIR/nftables_changes.log"
        fi
    fi

    # Save current rules for next comparison
    mv "$current_rules_file" "$previous_rules_file"
}

# Monitor dropped packets
monitor_dropped_packets() {
    # Use nftables tracing if available (kernel 5.13+)
    local dropped_packets=$(dmesg | grep -c "nf_tables.*drop" 2>/dev/null || echo "0")

    if (( dropped_packets > 0 )); then
        gonzo_speak "$dropped_packets PACKETS DROPPED BY FIREWALL" "threat" "normal"
        echo "$(date '+%Y-%m-%d %H:%M:%S') PACKETS_DROPPED $dropped_packets" >> "$LOGS_DIR/network_events.log"
    fi

    # Also check syslog for nftables messages
    local syslog_drops=$(journalctl -u nftables --since "5 minutes ago" 2>/dev/null | grep -c "drop\|reject" || echo "0")

    if (( syslog_drops > 0 )); then
        echo "$(date '+%Y-%m-%d %H:%M:%S') SYSLOG_DROPS $syslog_drops" >> "$LOGS_DIR/network_events.log"
    fi
}

# Check for brute force attempts (failed connections)
monitor_brute_force() {
    # Look for repeated connection attempts to the same port
    for port in 22 80 443; do
        local failed_attempts=$(netstat -tuln 2>/dev/null | grep ":$port " | grep -c "SYN_SENT\|CLOSE_WAIT" || echo "0")

        if (( failed_attempts > 10 )); then
            gonzo_multi_alert "threat_detected" "BRUTE FORCE ATTEMPT DETECTED ON PORT $port: $failed_attempts failed connections"
            echo "$(date '+%Y-%m-%d %H:%M:%S') BRUTE_FORCE port:$port attempts:$failed_attempts" >> "$LOGS_DIR/threats.log"
        fi
    done
}

# Monitor NAT/Masquerade rules
monitor_nat_rules() {
    local nat_rules=$(nft list table ip nat 2>/dev/null | grep -c "masquerade\|dnat\|snat" || echo "0")

    if (( nat_rules > 0 )); then
        gonzo_speak "NAT/MASQUERADE ACTIVE: $nat_rules rules" "network" "normal"
        echo "$(date '+%Y-%m-%d %H:%M:%S') NAT_ACTIVE $nat_rules" >> "$LOGS_DIR/network_events.log"
    fi
}

# Generate firewall report
generate_firewall_report() {
    local report_file="$LOGS_DIR/firewall_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "=== NFTABLES FIREWALL REPORT ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"

    echo "Current Ruleset:" >> "$report_file"
    nft list ruleset >> "$report_file" 2>/dev/null || echo "Unable to list ruleset" >> "$report_file"

    echo "" >> "$report_file"
    echo "Recent Firewall Events:" >> "$report_file"
    grep -E "(DROPPED|BRUTE_FORCE|FIREWALL)" "$LOGS_DIR/threats.log" | tail -10 >> "$report_file"

    gonzo_speak "FIREWALL REPORT GENERATED" "status" "normal"
}

# Main nftables monitoring function
monitor_nftables() {
    monitor_nftables_rules
    monitor_nftables_counters
    monitor_rule_changes
    monitor_dropped_packets
    monitor_brute_force
    monitor_nat_rules
}