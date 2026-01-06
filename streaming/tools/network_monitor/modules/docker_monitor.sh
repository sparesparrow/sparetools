# Docker Network Monitor
# "The highways are crowded with people who drive as if they know where they're going."
# - Hunter S. Thompson

# Docker network monitoring variables
declare -A DOCKER_NETWORKS
declare -A DOCKER_CONTAINERS
DOCKER_MONITOR_ACTIVE=false

# Initialize Docker monitoring
init_docker_monitor() {
    if ! command -v docker >/dev/null 2>&1; then
        gonzo_speak "DOCKER NOT FOUND - CONTAINER SURVEILLANCE UNAVAILABLE" "system" "normal"
        return 1
    fi

    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        gonzo_speak "DOCKER DAEMON NOT RUNNING - CONTAINERS BEYOND OUR REACH" "system" "ominous"
        return 1
    fi

    DOCKER_MONITOR_ACTIVE=true
    gonzo_speak "DOCKER SURVEILLANCE ENGAGED - WATCHING THE CONTAINERS" "system" "intense"

    # Initialize container tracking
    update_docker_inventory
    return 0
}

# Update Docker inventory
update_docker_inventory() {
    # Get running containers
    while IFS= read -r line; do
        local container_id=$(echo "$line" | awk '{print $1}')
        local container_name=$(echo "$line" | awk '{print $2}' | sed 's/\///')
        local status=$(echo "$line" | awk '{print $5}')

        DOCKER_CONTAINERS["$container_id"]="$container_name:$status"
    done < <(docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}" | tail -n +2)

    # Get Docker networks
    while IFS= read -r line; do
        local network_name=$(echo "$line" | awk '{print $2}')
        local driver=$(echo "$line" | awk '{print $3}')

        if [[ "$driver" != "null" ]]; then
            DOCKER_NETWORKS["$network_name"]="$driver"
        fi
    done < <(docker network ls --format "table {{.ID}}\t{{.Name}}\t{{.Driver}}" | tail -n +2)
}

# Monitor container lifecycle events
monitor_container_events() {
    # Get recent container events
    local events=$(docker events --since "30s" --until "0s" --format "{{.Time}} {{.Type}} {{.Action}} {{.Actor.Attributes.name}}" 2>/dev/null | tail -10)

    while IFS= read -r event; do
        [[ -z "$event" ]] && continue

        local timestamp=$(echo "$event" | awk '{print $1}')
        local event_type=$(echo "$event" | awk '{print $2}')
        local action=$(echo "$event" | awk '{print $3}')
        local container_name=$(echo "$event" | awk '{print $4}')

        case "$action" in
            "start")
                gonzo_multi_alert "container_new" "CONTAINER LAUNCHED: $container_name has entered the network battlefield"
                echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_CONTAINER_START $container_name" >> "$LOGS_DIR/network_events.log"
                ;;
            "stop"|"die")
                gonzo_multi_alert "container_stopped" "CONTAINER TERMINATED: $container_name has vanished from the digital ether"
                echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_CONTAINER_STOP $container_name" >> "$LOGS_DIR/network_events.log"
                ;;
            "create")
                gonzo_speak "NEW CONTAINER CREATED: $container_name - what's cooking in there?" "network" "normal"
                ;;
            "destroy")
                gonzo_speak "CONTAINER DESTROYED: $container_name - cleanup on aisle infinity" "network" "normal"
                ;;
        esac
    done <<< "$events"
}

# Monitor Docker network activity
monitor_docker_networks() {
    for network in "${!DOCKER_NETWORKS[@]}"; do
        # Get network details
        local network_info=$(docker network inspect "$network" 2>/dev/null)

        if [[ -n "$network_info" ]]; then
            # Check for containers in this network
            local container_count=$(echo "$network_info" | grep -c '"Name":')

            if (( container_count > 0 )); then
                # Get network traffic (if possible)
                local connected_containers=$(echo "$network_info" | grep '"Name":' | sed 's/.*"Name": "\([^"]*\)".*/\1/' | tr '\n' ' ')

                # Log network activity
                echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_NETWORK $network containers:$container_count connected:$connected_containers" >> "$LOGS_DIR/network_events.log"
            fi
        fi
    done
}

# Monitor Docker bridge interface
monitor_docker_bridge() {
    local docker_iface="docker0"

    if ip link show "$docker_iface" >/dev/null 2>&1; then
        # Monitor Docker bridge traffic
        local bridge_stats=$(ip -s link show "$docker_iface" 2>/dev/null | grep "RX:\|TX:" | tail -2)

        if [[ -n "$bridge_stats" ]]; then
            local rx_packets=$(echo "$bridge_stats" | head -1 | awk '{print $2}')
            local tx_packets=$(echo "$bridge_stats" | tail -1 | awk '{print $2}')

            # Alert on high container traffic
            if (( rx_packets > 10000 || tx_packets > 10000 )); then
                gonzo_speak "DOCKER BRIDGE BURNING: $rx_packets RX, $tx_packets TX packets - containers are chatty" "network" "intense"
            fi

            echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_BRIDGE_STATS rx:$rx_packets tx:$tx_packets" >> "$LOGS_DIR/network_events.log"
        fi
    fi
}

# Check for Docker security issues
audit_docker_security() {
    local security_issues=0

    # Check for privileged containers
    local privileged_containers=$(docker ps --filter "status=running" --format "{{.Names}}" | xargs -I {} docker inspect {} --format '{{.Name}}: privileged={{.HostConfig.Privileged}}' 2>/dev/null | grep "true" | wc -l)

    if (( privileged_containers > 0 )); then
        gonzo_multi_alert "threat_detected" "PRIVILEGED CONTAINERS DETECTED: $privileged_containers containers running with elevated privileges"
        echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_SECURITY_PRIVILEGED $privileged_containers" >> "$LOGS_DIR/threats.log"
        ((security_issues++))
    fi

    # Check for containers with host networking
    local host_network_containers=$(docker ps --filter "network=host" --format "{{.Names}}" | wc -l)

    if (( host_network_containers > 0 )); then
        gonzo_multi_alert "threat_detected" "HOST NETWORK CONTAINERS: $host_network_containers containers using host networking"
        echo "$(date '+%Y-%m-%d %H:%M:%S') DOCKER_SECURITY_HOSTNET $host_network_containers" >> "$LOGS_DIR/threats.log"
        ((security_issues++))
    fi

    # Check for exposed ports without restrictions
    local exposed_ports=$(docker ps --format "{{.Ports}}" | grep -v "->" | wc -l)

    if (( exposed_ports > 0 )); then
        gonzo_speak "EXPOSED CONTAINER PORTS DETECTED: $exposed_ports ports open to the world" "threat" "ominous"
        ((security_issues++))
    fi

    if (( security_issues == 0 )); then
        gonzo_speak "DOCKER SECURITY AUDIT: All quiet on the container front" "status" "normal"
    fi
}

# Generate Docker network report
generate_docker_report() {
    local report_file="$LOGS_DIR/docker_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "=== DOCKER NETWORK INTELLIGENCE ===" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"

    echo "ACTIVE CONTAINERS:" >> "$report_file"
    if [[ ${#DOCKER_CONTAINERS[@]} -gt 0 ]]; then
        for container in "${!DOCKER_CONTAINERS[@]}"; do
            echo "  $container: ${DOCKER_CONTAINERS[$container]}" >> "$report_file"
        done
    else
        echo "  No active containers" >> "$report_file"
    fi
    echo "" >> "$report_file"

    echo "DOCKER NETWORKS:" >> "$report_file"
    if [[ ${#DOCKER_NETWORKS[@]} -gt 0 ]]; then
        for network in "${!DOCKER_NETWORKS[@]}"; do
            echo "  $network (${DOCKER_NETWORKS[$network]})" >> "$report_file"
        done
    else
        echo "  No custom networks" >> "$report_file"
    fi
    echo "" >> "$report_file"

    echo "SECURITY STATUS:" >> "$report_file"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "$report_file"

    gonzo_speak "DOCKER INTELLIGENCE REPORT FILED" "network" "normal"
}

# Main Docker monitoring function
monitor_docker() {
    if [[ "$DOCKER_MONITOR_ACTIVE" != true ]]; then
        return
    fi

    update_docker_inventory
    monitor_container_events
    monitor_docker_networks
    monitor_docker_bridge

    # Security audit every 10 minutes
    if (( $(date +%M) % 10 == 0 )); then
        audit_docker_security
        generate_docker_report
    fi
}