#!/bin/bash

# Enhanced Network Monitor - Gonzo Journalism Edition
# A paranoid, intense network surveillance system
# "When the going gets weird, the weird turn pro." - Hunter S. Thompson

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
MODULES_DIR="$SCRIPT_DIR/modules"
LOGS_DIR="$SCRIPT_DIR/logs"
DATA_DIR="$SCRIPT_DIR/data"

# Source configuration and modules
source "$CONFIG_DIR/config.sh"
source "$MODULES_DIR/gonzo_alerts.sh"
source "$MODULES_DIR/interface_monitor.sh"
source "$MODULES_DIR/packet_analyzer.sh"
source "$MODULES_DIR/nftables_monitor.sh"
source "$MODULES_DIR/nmap_scanner.sh"
source "$MODULES_DIR/visualization.sh"
source "$MODULES_DIR/threat_assessment.sh"
source "$MODULES_DIR/docker_monitor.sh"
source "$MODULES_DIR/ssh_monitor.sh"

# Global variables
declare -A ACTIVE_INTERFACES
declare -A KNOWN_DEVICES
declare -A GATEWAY_STATUS
declare -A THREAT_LEVEL

# Initialize system
init_system() {
    gonzo_speak "NETWORK MONITOR INITIALIZING" "system" "dramatic"

    # Create log files
    mkdir -p "$LOGS_DIR" "$DATA_DIR"
    touch "$LOGS_DIR/network_events.log"
    touch "$LOGS_DIR/threats.log"
    touch "$DATA_DIR/known_devices.db"
    touch "$DATA_DIR/network_topology.db"

    # Load known devices if they exist
    if [[ -f "$DATA_DIR/known_devices.db" ]]; then
        while IFS='=' read -r iface devices; do
            KNOWN_DEVICES["$iface"]="$devices"
        done < "$DATA_DIR/known_devices.db"
    fi

    # Detect active interfaces
    detect_interfaces

    # Initialize Docker monitoring
    init_docker_monitor

    # Initialize SSH monitoring
    # SSH monitoring is always active

    # Initialize SDR monitoring
    init_sdr_monitor

    gonzo_speak "system_online" "system" "intense"
}

# Main monitoring loop
main_loop() {
    local iteration=0

    while true; do
        ((iteration++))

        # Multi-interface monitoring
        monitor_interfaces

        # Packet analysis (every 10 iterations)
        if (( iteration % 10 == 0 )); then
            analyze_packets
        fi

        # Nftables monitoring (every 30 iterations)
        if (( iteration % 30 == 0 )); then
            monitor_nftables
        fi

        # Nmap scanning (every 300 iterations - every 5 minutes)
        if (( iteration % 300 == 0 )); then
            network_scan
        fi

        # Update topology visualization (every 60 iterations)
        if (( iteration % 60 == 0 )); then
            update_topology
        fi

        # Docker monitoring (every 15 iterations)
        if (( iteration % 15 == 0 )); then
            monitor_docker
        fi

        # SSH monitoring (every 20 iterations)
        if (( iteration % 20 == 0 )); then
            monitor_ssh
        fi

        # SDR monitoring (every 25 iterations)
        if (( iteration % 25 == 0 )); then
            monitor_sdr
        fi

        # Threat assessment
        assess_threats

        sleep "$MONITOR_INTERVAL"
    done
}

# Save known devices to persistent storage
save_known_devices() {
    > "$DATA_DIR/known_devices.db"
    for iface in "${!KNOWN_DEVICES[@]}"; do
        echo "$iface=${KNOWN_DEVICES[$iface]}" >> "$DATA_DIR/known_devices.db"
    done
}

# Kill any background processes
kill_background_processes() {
    # Kill any lingering tcpdump or tshark processes
    pkill -f "tcpdump.*monitor" 2>/dev/null || true
    pkill -f "tshark.*monitor" 2>/dev/null || true
}

# Cleanup function
cleanup() {
    gonzo_speak "system_shutdown" "system" "ominous"
    save_known_devices
    kill_background_processes
    exit 0
}

# Signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    init_system
    echo "Enhanced Network Monitor Active - Press Ctrl+C to exit"
    echo "Monitoring interfaces: ${!ACTIVE_INTERFACES[*]}"
    main_loop
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi