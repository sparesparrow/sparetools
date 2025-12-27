# SSH Connection Monitor
# "The TV business is uglier than most things. It is normally perceived as some kind
# of cruel joke." - Hunter S. Thompson

# SSH monitoring variables
declare -A SSH_CONNECTIONS
declare -A SSH_FAILED_ATTEMPTS
SSH_MONITOR_ACTIVE=true

# Monitor SSH connections
monitor_ssh_connections() {
    # Get current SSH connections
    local current_ssh=$(netstat -tnp 2>/dev/null | grep ":22 " | grep ESTABLISHED | awk '{print $5}' | cut -d: -f1 | sort | uniq)

    # Clear old connections
    SSH_CONNECTIONS=()

    # Track current connections
    while IFS= read -r ip; do
        [[ -z "$ip" ]] && continue
        SSH_CONNECTIONS["$ip"]=$(date +%s)

        # Check if this is a new connection
        if ! grep -q "^$ip$" "$DATA_DIR/known_ssh_connections" 2>/dev/null; then
            gonzo_multi_alert "new_device_discovered" "SSH CONNECTION ESTABLISHED: Remote host $ip has dialed into our matrix"
            echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_CONNECTION_NEW $ip" >> "$LOGS_DIR/network_events.log"
            echo "$ip" >> "$DATA_DIR/known_ssh_connections"
        fi
    done <<< "$current_ssh"

    # Update known connections file
    > "$DATA_DIR/known_ssh_connections"
    for ip in "${!SSH_CONNECTIONS[@]}"; do
        echo "$ip" >> "$DATA_DIR/known_ssh_connections"
    done
}

# Monitor SSH authentication failures
monitor_ssh_failures() {
    # Check auth log for SSH failures
    local auth_log="/var/log/auth.log"
    local secure_log="/var/log/secure"

    local log_file=""
    if [[ -f "$auth_log" ]]; then
        log_file="$auth_log"
    elif [[ -f "$secure_log" ]]; then
        log_file="$secure_log"
    else
        return  # No auth log available
    fi

    # Get recent SSH failures (last 5 minutes)
    local recent_failures=$(grep -E "sshd.*Failed|sshd.*Invalid" "$log_file" 2>/dev/null | awk -v now="$(date +%s)" '
        {
            # Extract timestamp and IP
            match($0, /([0-9]{2}:[0-9]{2}:[0-9]{2})/, time_match)
            if (time_match[1]) {
                split(time_match[1], time_parts, ":")
                event_time = systime() - (time_parts[1] * 3600 + time_parts[2] * 60 + time_parts[3])
                if (systime() - event_time < 300) {  # Last 5 minutes
                    match($0, /([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/, ip_match)
                    if (ip_match[1]) {
                        print ip_match[1]
                    }
                }
            }
        }
    ')

    # Count failures per IP
    declare -A failure_counts
    while IFS= read -r ip; do
        [[ -z "$ip" ]] && continue
        ((failure_counts["$ip"]++))
    done <<< "$recent_failures"

    # Alert on brute force attempts
    for ip in "${!failure_counts[@]}"; do
        local count="${failure_counts[$ip]}"

        if (( count > 5 )); then
            gonzo_multi_alert "threat_detected" "SSH BRUTE FORCE ATTACK: $ip attempted $count failed logins - someone's trying to break into our digital fortress"
            echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_BRUTE_FORCE $ip attempts:$count" >> "$LOGS_DIR/threats.log"
        elif (( count > 2 )); then
            gonzo_speak "SUSPICIOUS SSH ACTIVITY: $ip has $count failed login attempts" "threat" "ominous"
        fi

        # Track failed attempts
        SSH_FAILED_ATTEMPTS["$ip"]=$count
    done
}

# Monitor SSH key authentication
monitor_ssh_keys() {
    # Check for SSH key usage in recent logins
    local auth_log="/var/log/auth.log"
    if [[ -f "$auth_log" ]]; then
        local key_logins=$(grep -c "Accepted publickey" "$auth_log" 2>/dev/null || echo "0")

        if (( key_logins > 0 )); then
            gonzo_speak "$key_logins SUCCESSFUL SSH KEY AUTHENTICATIONS - secure connections established" "status" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_KEY_LOGINS $key_logins" >> "$LOGS_DIR/network_events.log"
        fi
    fi
}

# Monitor SSH tunnel activity
monitor_ssh_tunnels() {
    # Look for SSH tunnels (port forwarding)
    local tunnels=$(netstat -tlnp 2>/dev/null | grep "sshd:" | grep -v ":22 " | wc -l)

    if (( tunnels > 0 )); then
        gonzo_speak "SSH TUNNELS DETECTED: $tunnels active tunnels - someone is building underground railroads through our network" "network" "intense"
        echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_TUNNELS $tunnels" >> "$LOGS_DIR/network_events.log"

        # List tunnel details
        netstat -tlnp 2>/dev/null | grep "sshd:" | grep -v ":22 " | while IFS= read -r line; do
            echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_TUNNEL_DETAIL $line" >> "$LOGS_DIR/network_events.log"
        done
    fi
}

# Check SSH server configuration
audit_ssh_config() {
    local sshd_config="/etc/ssh/sshd_config"

    if [[ -f "$sshd_config" ]]; then
        local security_issues=0

        # Check for insecure settings
        if grep -q "^PermitRootLogin yes" "$sshd_config" 2>/dev/null; then
            gonzo_multi_alert "threat_detected" "SSH SECURITY RISK: Root login is permitted - this is like leaving your front door wide open"
            ((security_issues++))
        fi

        if grep -q "^PasswordAuthentication yes" "$sshd_config" 2>/dev/null && ! grep -q "^PermitEmptyPasswords no" "$sshd_config" 2>/dev/null; then
            gonzo_speak "SSH PASSWORD AUTHENTICATION ENABLED - passwords are the weakest link in the chain" "threat" "ominous"
            ((security_issues++))
        fi

        if ! grep -q "^UsePAM yes" "$sshd_config" 2>/dev/null; then
            gonzo_speak "SSH PAM NOT ENABLED - authentication could be compromised" "threat" "ominous"
            ((security_issues++))
        fi

        if (( security_issues == 0 )); then
            gonzo_speak "SSH CONFIGURATION AUDIT: All quiet on the SSH front" "status" "normal"
        fi

        echo "$(date '+%Y-%m-%d %H:%M:%S') SSH_CONFIG_AUDIT issues:$security_issues" >> "$LOGS_DIR/network_events.log"
    fi
}

# Generate SSH security report
generate_ssh_report() {
    local report_file="$LOGS_DIR/ssh_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "=== SSH CONNECTION INTELLIGENCE ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"

    echo "ACTIVE SSH CONNECTIONS:" >> "$report_file"
    if [[ ${#SSH_CONNECTIONS[@]} -gt 0 ]]; then
        for ip in "${!SSH_CONNECTIONS[@]}"; do
            local connect_time="${SSH_CONNECTIONS[$ip]}"
            local duration=$(( $(date +%s) - connect_time ))
            echo "  $ip: connected for ${duration}s" >> "$report_file"
        done
    else
        echo "  No active SSH connections" >> "$report_file"
    fi
    echo "" >> "$report_file"

    echo "RECENT FAILED ATTEMPTS:" >> "$report_file"
    if [[ ${#SSH_FAILED_ATTEMPTS[@]} -gt 0 ]]; then
        for ip in "${!SSH_FAILED_ATTEMPTS[@]}"; do
            echo "  $ip: ${SSH_FAILED_ATTEMPTS[$ip]} failed attempts" >> "$report_file"
        done
    else
        echo "  No recent failed attempts" >> "$report_file"
    fi
    echo "" >> "$report_file"

    echo "SSH SERVICE STATUS:" >> "$report_file"
    if systemctl is-active --quiet sshd 2>/dev/null; then
        echo "  SSH service: RUNNING" >> "$report_file"
    elif systemctl is-active --quiet ssh 2>/dev/null; then
        echo "  SSH service: RUNNING" >> "$report_file"
    else
        echo "  SSH service: NOT RUNNING OR NOT FOUND" >> "$report_file"
    fi

    gonzo_speak "SSH INTELLIGENCE REPORT FILED" "network" "normal"
}

# Remote SSH monitoring (if we have SSH access to other hosts)
monitor_remote_ssh() {
    local remote_hosts_file="$DATA_DIR/remote_ssh_hosts"

    if [[ ! -f "$remote_hosts_file" ]]; then
        return  # No remote hosts configured
    fi

    while IFS= read -r host_line; do
        [[ "$host_line" =~ ^#.*$ ]] && continue  # Skip comments
        [[ -z "$host_line" ]] && continue       # Skip empty lines

        local host=$(echo "$host_line" | awk '{print $1}')
        local user=$(echo "$host_line" | awk '{print $2}')

        # Attempt to monitor remote host (requires passwordless SSH key setup)
        local remote_connections=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "$user@$host" "netstat -tn | grep ':22 ' | wc -l" 2>/dev/null)

        if [[ -n "$remote_connections" ]]; then
            gonzo_speak "REMOTE SSH MONITOR: $host has $remote_connections active connections" "network" "normal"
            echo "$(date '+%Y-%m-%d %H:%M:%S') REMOTE_SSH $host connections:$remote_connections" >> "$LOGS_DIR/network_events.log"
        fi
    done < "$remote_hosts_file"
}

# Main SSH monitoring function
monitor_ssh() {
    monitor_ssh_connections
    monitor_ssh_failures
    monitor_ssh_keys
    monitor_ssh_tunnels

    # Remote monitoring every 5 minutes
    if (( $(date +%M) % 5 == 0 )); then
        monitor_remote_ssh
    fi

    # Security audit every 30 minutes
    if (( $(date +%M) % 30 == 0 )); then
        audit_ssh_config
        generate_ssh_report
    fi
}