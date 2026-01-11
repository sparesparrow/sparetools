# Gonzo Alert System
# "Buy the ticket, take the ride." - Hunter S. Thompson

# Gonzo alert personas and their characteristics
declare -A GONZO_PERSONAS=(
    ["system"]="male1:-20:80"      # Deep, authoritative, paranoid
    ["device"]="female1:0:90"      # Energetic, suspicious, excited
    ["threat"]="male2:10:70"       # Fast, urgent, conspiratorial
    ["status"]="female2:-10:85"    # Measured, confident, omniscient
    ["network"]="male3:5:75"       # Technical, intense, dramatic
)

# Gonzo alert messages with personality - Hunter S. Thompson style
declare -A ALERT_MESSAGES=(
    # System events
    ["system_start"]="NETWORK MONITOR BOOTING UP - WE'RE LEAVING THE ROAD NOW, BABY"
    ["system_online"]="SYSTEM ONLINE - EYES WIDE OPEN IN THE DIGITAL BADLANDS"
    ["system_shutdown"]="SHUTTING DOWN THE SURVEILLANCE STATE - BUT THE SHADOWS REMAIN"

    # Gateway events
    ["gateway_found"]="GATEWAY DETECTED! THE DIGITAL PORTAL HAS OPENED! SOMETHING WILD IS COMING THROUGH!"
    ["gateway_lost"]="GATEWAY VANISHED INTO THE ETHER! THE WALLS HAVE BREACHED! ALL HANDS ON DECK!"

    # Device events
    ["new_device"]="NEW DEVICE ON THE WIRE! WHO'S THIS GHOST IN THE MACHINE? KEEP YOUR WITS ABOUT YOU!"
    ["device_gone"]="DEVICE GONE! VANISHED LIKE A BAD ACID TRIP! THE PLOT THICKENS!"
    ["device_suspicious"]="SUSPICIOUS DEVICE ACTIVITY! THIS ONE SMELLS LIKE TROUBLE - STAY FROSTY!"

    # Network events
    ["packet_storm"]="PACKET STORM RAGING! THE WIRES ARE BURNING WITH COSMIC FIRE!"
    ["port_scan"]="PORT SCAN DETECTED! SOMEONE'S PROBING OUR DEFENSES LIKE A BAD DOCTOR!"
    ["anomaly"]="NETWORK ANOMALY! SOMETHING WEIRD IS HAPPENING - THE UNIVERSE IS OUT OF ALIGNMENT!"

    # Threat levels
    ["threat_low"]="MINOR THREAT DETECTED - KEEP YOUR EYES OPEN, THE NIGHT IS YOUNG"
    ["threat_medium"]="THREAT LEVEL YELLOW - SOMETHING'S NOT RIGHT IN THE WIRES"
    ["threat_high"]="THREAT LEVEL ORANGE - LOCK DOWN THE HATCHES! THE STORM IS COMING!"
    ["threat_critical"]="CRITICAL THREAT! RED ALERT! THIS IS NOT A DRILL - IT'S THE REAL THING!"

    # Docker events
    ["container_new"]="NEW CONTAINER SPAWNED! WHAT'S BREWING IN THIS DIGITAL CAULDRON?"
    ["container_stopped"]="CONTAINER TERMINATED! CLEANUP IN THE MATRIX - THE PARTY'S OVER!"

    # SDR events
    ["rf_signal"]="RADIO FREQUENCY SIGNAL DETECTED! THE AIRWAVES ARE ALIVE WITH COSMIC VIBRATIONS!"
    ["iot_device"]="IOT DEVICE DETECTED! THE MACHINES ARE TALKING IN TONGUES!"

    # SSH events
    ["ssh_new"]="SSH CONNECTION ESTABLISHED! REMOTE OPERATOR DIALED IN - TRUST NO ONE!"
    ["ssh_brute"]="SSH BRUTE FORCE ATTACK! SOMEONE'S BASHING AT OUR DIGITAL DOOR!"
    ["ssh_tunnel"]="SSH TUNNELS DETECTED! UNDERGROUND RAILROADS THROUGH THE NETWORK!"

    # Hotspot events
    ["hotspot_device_connected"]="HOTSPOT BREACH! NEW DEVICE HAS JOINED THE WIRELESS WARD - EYES ON TARGET!"
    ["hotspot_device_disconnected"]="HOTSPOT EXFILTRATION! DEVICE HAS GONE DARK - THE GHOST HAS LEFT THE MACHINE!"
    ["hotspot_destination_tracking"]="HOTSPOT TRAFFIC ANALYSIS ACTIVE! TRACKING WHERE THE PACKETS GO IN THE DIGITAL WILDERNESS!"
    ["hotspot_threat_detected"]="HOTSPOT UNDER ATTACK! SUSPICIOUS ACTIVITY ON THE WIRELESS FRONTIER!"

    # Advanced threats
    ["correlated_attack"]="COORDINATED ATTACK DETECTED! THIS IS NO ACCIDENT - IT'S A CONSPIRACY!"
    ["recon_activity"]="RECONNAISSANCE ACTIVITY! SOMEONE'S MAPPING OUR TERRITORY!"
    ["anomalous_activity"]="ANOMALOUS ACTIVITY SPIKE! THE UNIVERSE IS OUT OF WHACK!"
)

# Gonzo sound effects
gonzo_beep() {
    local level="$1"
    case "$level" in
        "info")
            printf '\a'; sleep 0.1
            ;;
        "warning")
            printf '\a'; sleep 0.1; printf '\a'; sleep 0.15
            ;;
        "alert")
            printf '\a'; sleep 0.2; printf '\a'; sleep 0.2; printf '\a'; sleep 0.1
            ;;
        "critical")
            for i in {1..5}; do printf '\a'; sleep 0.1; done
            ;;
    esac
}

# Main gonzo speaking function
# Gonzo speaking function - enhanced for gonzo journalism style
gonzo_speak() {
    local message_key="$1"
    local persona="${2:-system}"
    local intensity="${3:-normal}"

    # Get the actual message from ALERT_MESSAGES if it's a key
    local message="${ALERT_MESSAGES[$message_key]}"
    if [[ -z "$message" ]]; then
        message="$message_key"  # Use as literal message if not a key
    fi

    # Get persona settings
    local voice_settings="${GONZO_PERSONAS[$persona]}"
    IFS=':' read -r voice pitch speed <<< "$voice_settings"

    # Adjust settings based on intensity
    case "$intensity" in
        "dramatic")
            pitch=$((pitch - 10))
            speed=$((speed - 10))
            ;;
        "intense")
            speed=$((speed + 10))
            ;;
        "ominous")
            pitch=$((pitch - 5))
            speed=$((speed - 15))
            ;;
        "urgent")
            speed=$((speed + 15))
            ;;
    esac

    # Add gonzo flair to the message - Thompson style
    local gonzo_message
    case "$persona" in
        "system")
            gonzo_message="*** NETWORK BULLETIN *** $message *** STAY TUNED ***"
            ;;
        "threat")
            gonzo_message="🚨 BREAKING: $message 🚨 THE WIRES ARE LIVE! 🚨"
            ;;
        "device")
            gonzo_message="👁️  EYES ON: $message 👁️  SOMETHING'S MOVING OUT THERE 👁️"
            ;;
        "network")
            gonzo_message="🌐 WIRES REPORT: $message 🌐 THE NETWORK SPEAKS 🌐"
            ;;
        *)
            gonzo_message="$message"
            ;;
    esac

    # Log the alert with gonzo flair
    echo "$(date '+%Y-%m-%d %H:%M:%S') [GONZO-$persona:$intensity] $gonzo_message" >> "$LOGS_DIR/gonzo_alerts.log"

    # Speak the alert (if spd-say is available)
    if command -v spd-say >/dev/null 2>&1; then
        spd-say -t "$voice" -p "$pitch" -r "$speed" "$gonzo_message" 2>/dev/null &
    fi

    # Visual alert with ASCII art flair
    case "$persona" in
        "threat")
            echo "╔══════════════════════════════════════════════════════════════════════════════╗"
            echo "║ $gonzo_message ║"
            echo "╚══════════════════════════════════════════════════════════════════════════════╝"
            ;;
        "system")
            echo "*** $gonzo_message ***"
            ;;
        *)
            echo "$gonzo_message"
            ;;
    esac
}

# Gonzo multi-alert for complex events - enhanced Thompson style
gonzo_multi_alert() {
    local event="$1"
    local details="$2"

    case "$event" in
        "new_device_discovered")
            gonzo_speak "new_device" "device" "intense"
            sleep 1
            gonzo_speak "$details - WHO'S THIS SHADOW IN THE MACHINE?" "network" "normal"
            gonzo_beep "warning"
            ;;

        "threat_detected")
            gonzo_speak "THREAT DETECTED! SOMETHING WICKED THIS WAY COMES!" "threat" "urgent"
            sleep 0.5
            gonzo_speak "$details - THE HUNT IS ON!" "threat" "intense"
            gonzo_beep "critical"
            ;;

        "gateway_breach")
            gonzo_speak "gateway_lost" "threat" "dramatic"
            sleep 1
            gonzo_speak "THE PERIMETER HAS BEEN COMPROMISED! ALL POSTS REPORT!" "threat" "intense"
            gonzo_beep "critical"
            ;;

        "packet_anomaly")
            gonzo_speak "packet_storm" "network" "intense"
            sleep 0.5
            gonzo_speak "$details - THE WIRES ARE SCREAMING!" "network" "normal"
            gonzo_beep "alert"
            ;;

        "ssh_attack")
            gonzo_speak "ssh_brute" "threat" "urgent"
            sleep 0.5
            gonzo_speak "$details - SOMEONE'S BASHING AT OUR DIGITAL DOOR WITH A SLEDGEHAMMER!" "threat" "intense"
            gonzo_beep "critical"
            ;;

        "container_alert")
            gonzo_speak "container_new" "network" "intense"
            sleep 0.5
            gonzo_speak "$details - WHAT'S BREWING IN THIS DIGITAL CAULDRON?" "network" "normal"
            gonzo_beep "warning"
            ;;

        "correlated_attack")
            gonzo_speak "correlated_attack" "threat" "dramatic"
            sleep 1
            gonzo_speak "$details - THIS IS NO COINCIDENCE - IT'S A COORDINATED ASSAULT!" "threat" "intense"
            gonzo_beep "critical"
            ;;

        "recon_detected")
            gonzo_speak "recon_activity" "threat" "ominous"
            sleep 0.5
            gonzo_speak "$details - SOMEONE'S MAPPING OUR TERRITORY LIKE A BAD LAND SURVEYOR!" "threat" "normal"
            gonzo_beep "alert"
            ;;

        "hotspot_new_device")
            gonzo_speak "hotspot_device_connected" "device" "intense"
            sleep 1
            gonzo_speak "$details - THE WIRELESS WARD HAS A NEW RESIDENT!" "network" "normal"
            gonzo_beep "warning"
            ;;

        "hotspot_device_gone")
            gonzo_speak "hotspot_device_disconnected" "device" "normal"
            sleep 0.5
            gonzo_speak "$details - DEVICE HAS LEFT THE HOTSPOT - TRACKING TERMINATED!" "network" "normal"
            gonzo_beep "info"
            ;;

        "hotspot_tracking_active")
            gonzo_speak "hotspot_destination_tracking" "network" "normal"
            sleep 0.5
            gonzo_speak "$details - MAPPING THE DIGITAL HIGHWAYS!" "network" "normal"
            gonzo_beep "info"
            ;;

        "anomaly_spike")
            gonzo_speak "anomalous_activity" "network" "intense"
            sleep 0.5
            gonzo_speak "$details - THE UNIVERSE HAS GONE OFF THE RAILS!" "network" "normal"
            gonzo_beep "alert"
            ;;
    esac
}

# Threat level escalation with dramatic flair
escalate_threat_level() {
    local current_level="$1"
    local new_level="$2"
    local reason="$3"

    if [[ "$new_level" != "$current_level" ]]; then
        gonzo_speak "THREAT LEVEL ESCALATION!" "threat" "dramatic"
        sleep 1
        gonzo_speak "FROM $current_level TO $new_level - $reason" "threat" "intense"
        gonzo_beep "critical"
    fi
}

# Dramatic system status reports
gonzo_status_report() {
    local status_type="$1"

    case "$status_type" in
        "interfaces")
            local iface_count="${#ACTIVE_INTERFACES[@]}"
            gonzo_speak "$iface_count INTERFACES UNDER SURVEILLANCE" "status" "normal"
            ;;

        "devices")
            local total_devices=0
            for devices in "${KNOWN_DEVICES[@]}"; do
                total_devices=$((total_devices + $(echo "$devices" | wc -w)))
            done
            gonzo_speak "$total_devices DEVICES BEING MONITORED" "status" "normal"
            ;;

        "threats")
            local threat_count=$(wc -l < "$LOGS_DIR/threats.log" 2>/dev/null || echo "0")
            if (( threat_count > 0 )); then
                gonzo_speak "$threat_count THREATS LOGGED - STAY ALERT" "threat" "ominous"
            else
                gonzo_speak "ALL CLEAR - FOR NOW" "status" "normal"
            fi
            ;;
    esac
}