# Threat Assessment and Event Correlation
# "The possibility of physical and mental collapse is now very real.
# No sympathy for the devil, keep that in mind." - Hunter S. Thompson

# Threat levels
declare -A THREAT_SCORES=(
    ["new_device"]=2
    ["device_gone"]=1
    ["gateway_lost"]=4
    ["packet_anomaly"]=3
    ["port_scan"]=5
    ["brute_force"]=5
    ["suspicious_payload"]=4
    ["firewall_breach"]=5
    ["unauthorized_host"]=4
    ["insecure_service"]=3
    ["packet_storm"]=4
    ["large_packets"]=2
    ["broadcast_storm"]=3
)

# Current threat state
CURRENT_THREAT_LEVEL=0
THREAT_HISTORY=()

# Assess threat level based on recent events
assess_threat_level() {
    local recent_threats=$(tail -20 "$LOGS_DIR/threats.log" 2>/dev/null)
    local new_threat_level=0

    # Analyze recent threats
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue

        # Extract threat type from log line
        local threat_type=""
        if echo "$line" | grep -q "NEW_DEVICE"; then
            threat_type="new_device"
        elif echo "$line" | grep -q "GATEWAY_LOST\|MISSING_AUTHORIZED"; then
            threat_type="gateway_lost"
        elif echo "$line" | grep -q "PACKET_ANOMALY\|PACKET_STORM"; then
            threat_type="packet_anomaly"
        elif echo "$line" | grep -q "PORT_SCAN"; then
            threat_type="port_scan"
        elif echo "$line" | grep -q "BRUTE_FORCE"; then
            threat_type="brute_force"
        elif echo "$line" | grep -q "SUSPICIOUS_PAYLOAD"; then
            threat_type="suspicious_payload"
        elif echo "$line" | grep -q "FIREWALL_OPEN\|RULESET_CHANGED"; then
            threat_type="firewall_breach"
        elif echo "$line" | grep -q "UNAUTHORIZED_HOST"; then
            threat_type="unauthorized_host"
        fi

        if [[ -n "$threat_type" ]]; then
            local score="${THREAT_SCORES[$threat_type]}"
            ((new_threat_level += score))
        fi
    done <<< "$recent_threats"

    # Factor in threat frequency (more threats = higher level)
    local threat_count=$(echo "$recent_threats" | wc -l)
    ((new_threat_level += threat_count / 2))

    # Cap at maximum threat level
    (( new_threat_level > 10 )) && new_threat_level=10

    # Update threat level if changed
    if (( new_threat_level != CURRENT_THREAT_LEVEL )); then
        escalate_threat_level "$CURRENT_THREAT_LEVEL" "$new_threat_level" "Recent network activity analysis"
        CURRENT_THREAT_LEVEL="$new_threat_level"
    fi

    # Add to threat history
    THREAT_HISTORY+=("$new_threat_level")
    # Keep only last 100 entries
    if (( ${#THREAT_HISTORY[@]} > 100 )); then
        THREAT_HISTORY=("${THREAT_HISTORY[@]:1}")
    fi
}

# Correlate related events
correlate_events() {
    local time_window=300  # 5 minutes in seconds
    local current_time=$(date +%s)

    # Look for patterns in recent events
    local recent_events=$(awk -v time="$((current_time - time_window))" '
        BEGIN { FS = " " }
        {
            # Parse timestamp (assuming format: YYYY-MM-DD HH:MM:SS)
            split($1, date_parts, "-")
            split($2, time_parts, ":")
            event_time = mktime(date_parts[1] " " date_parts[2] " " date_parts[3] " " time_parts[1] " " time_parts[2] " " time_parts[3])

            if (event_time >= time) {
                print $0
            }
        }
    ' "$LOGS_DIR/network_events.log" 2>/dev/null)

    # Look for correlation patterns
    local device_events=$(echo "$recent_events" | grep -c "NEW_DEVICE\|DEVICE_GONE")
    local network_events=$(echo "$recent_events" | grep -c "PACKET_\|PORT_")
    local gateway_events=$(echo "$recent_events" | grep -c "GATEWAY")

    # Detect potential attack patterns
    if (( device_events > 5 )) && (( network_events > 10 )); then
        gonzo_multi_alert "threat_detected" "COORDINATED ATTACK PATTERN DETECTED: Multiple device and network events"
        echo "$(date '+%Y-%m-%d %H:%M:%S') CORRELATED_ATTACK device_events:$device_events network_events:$network_events" >> "$LOGS_DIR/threats.log"
    fi

    if (( gateway_events > 2 )); then
        gonzo_multi_alert "threat_detected" "GATEWAY INSTABILITY: Multiple gateway events detected"
        echo "$(date '+%Y-%m-%d %H:%M:%S') GATEWAY_INSTABILITY events:$gateway_events" >> "$LOGS_DIR/threats.log"
    fi

    # Look for reconnaissance patterns
    local recon_events=$(echo "$recent_events" | grep -c "PORT_SCAN\|SERVICE_SCAN\|OS_DETECT")
    if (( recon_events > 3 )); then
        gonzo_multi_alert "threat_detected" "RECONNAISSANCE ACTIVITY DETECTED: Multiple scanning events"
        echo "$(date '+%Y-%m-%d %H:%M:%S') RECONNAISSANCE events:$recon_events" >> "$LOGS_DIR/threats.log"
    fi
}

# Analyze threat trends
analyze_threat_trends() {
    if (( ${#THREAT_HISTORY[@]} < 10 )); then
        return  # Need more data
    fi

    # Calculate trend (simple moving average)
    local recent_avg=0
    local older_avg=0

    local half_point=$((${#THREAT_HISTORY[@]} / 2))
    local i

    for ((i = half_point; i < ${#THREAT_HISTORY[@]}; i++)); do
        ((recent_avg += THREAT_HISTORY[i]))
    done
    ((recent_avg /= (${#THREAT_HISTORY[@]} - half_point)))

    for ((i = 0; i < half_point; i++)); do
        ((older_avg += THREAT_HISTORY[i]))
    done
    ((older_avg /= half_point))

    # Detect trends
    local trend=$((recent_avg - older_avg))

    if (( trend > 2 )); then
        gonzo_speak "THREAT LEVEL TREND: INCREASING - Heightened vigilance required" "threat" "urgent"
    elif (( trend < -2 )); then
        gonzo_speak "THREAT LEVEL TREND: DECREASING - Situation improving" "status" "normal"
    fi

    # Log trend analysis
    echo "$(date '+%Y-%m-%d %H:%M:%S') THREAT_TREND recent_avg:$recent_avg older_avg:$older_avg trend:$trend" >> "$LOGS_DIR/network_events.log"
}

# Generate threat intelligence report
generate_threat_report() {
    local report_file="$LOGS_DIR/threat_intelligence_$(date +%Y%m%d_%H%M%S).txt"

    echo "=== THREAT INTELLIGENCE REPORT ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "Current Threat Level: $CURRENT_THREAT_LEVEL/10" >> "$report_file"
    echo "" >> "$report_file"

    echo "THREAT HISTORY (Last 100 assessments):" >> "$report_file"
    printf '%s\n' "${THREAT_HISTORY[@]}" >> "$report_file"
    echo "" >> "$report_file"

    echo "TOP THREAT TYPES:" >> "$report_file"
    if [[ -f "$LOGS_DIR/threats.log" ]]; then
        grep -oE "(NEW_DEVICE|GATEWAY_LOST|PACKET_ANOMALY|PORT_SCAN|BRUTE_FORCE|SUSPICIOUS_PAYLOAD|FIREWALL_OPEN|UNAUTHORIZED_HOST)" "$LOGS_DIR/threats.log" | sort | uniq -c | sort -nr >> "$report_file"
    fi
    echo "" >> "$report_file"

    echo "RECOMMENDED ACTIONS:" >> "$report_file"
    if (( CURRENT_THREAT_LEVEL >= 7 )); then
        echo "- IMMEDIATE ACTION REQUIRED: Isolate affected systems" >> "$report_file"
        echo "- Consider network segmentation" >> "$report_file"
        echo "- Review firewall rules immediately" >> "$report_file"
    elif (( CURRENT_THREAT_LEVEL >= 4 )); then
        echo "- Increase monitoring frequency" >> "$report_file"
        echo "- Review recent device connections" >> "$report_file"
        echo "- Check for unauthorized services" >> "$report_file"
    else
        echo "- Continue normal monitoring" >> "$report_file"
        echo "- Maintain regular security assessments" >> "$report_file"
    fi

    gonzo_speak "THREAT INTELLIGENCE REPORT GENERATED" "threat" "ominous"
}

# Anomaly detection using statistical analysis
detect_anomalies() {
    # Simple statistical anomaly detection
    if [[ -f "$LOGS_DIR/network_events.log" ]]; then
        local total_events=$(wc -l < "$LOGS_DIR/network_events.log")
        local hour_ago=$(date -d '1 hour ago' +%Y-%m-%d\ %H:%M:%S 2>/dev/null || date -v-1H +%Y-%m-%d\ %H:%M:%S 2>/dev/null)

        if [[ -n "$hour_ago" ]]; then
            local recent_events=$(awk -v start="$hour_ago" '$0 > start' "$LOGS_DIR/network_events.log" | wc -l)
            local avg_events_per_hour=$((total_events / 24))  # Rough estimate

            if (( recent_events > avg_events_per_hour * 3 )); then
                gonzo_speak "ANOMALOUS ACTIVITY DETECTED: $recent_events events in last hour (avg: $avg_events_per_hour)" "threat" "urgent"
                echo "$(date '+%Y-%m-%d %H:%M:%S') ANOMALOUS_ACTIVITY events:$recent_events avg:$avg_events_per_hour" >> "$LOGS_DIR/threats.log"
            fi
        fi
    fi
}

# Main threat assessment function
assess_threats() {
    assess_threat_level
    correlate_events
    analyze_threat_trends
    detect_anomalies

    # Generate reports periodically
    if (( $(date +%M) % 30 == 0 )); then  # Every 30 minutes
        generate_threat_report
    fi
}