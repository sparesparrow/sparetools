# Enhanced Network Monitor Configuration
# "The edge... there is no honest way to explain it
# because the only people who really know where it is
# are the ones who have gone over." - Hunter S. Thompson

# Basic settings
MONITOR_INTERVAL=5          # Main loop interval in seconds
PACKET_CAPTURE_DURATION=10  # Packet capture duration in seconds
SCAN_INTERVAL=300          # Nmap scan interval in iterations (5 minutes)
THREAT_THRESHOLD=3         # Threshold for escalating alerts

# Interface settings - Prioritize hotspot interface
SUPPORTED_INTERFACES=("wlan0" "eth0" "docker0" "br-*")
EXCLUDED_INTERFACES=("lo")

# Packet analysis settings
PACKET_FILTER="not port 22 and not arp and host "  # Exclude SSH and ARP for cleaner output
MAX_PACKETS_PER_CAPTURE=1000

# Hotspot monitoring settings
HOTSPOT_INTERFACE="wlan0"                    # Primary hotspot interface
HOTSPOT_DESTINATION_TRACKING=true           # Enable destination address tracking
HOTSPOT_DEVICE_MONITORING=true             # Monitor device connections
HOTSPOT_VISUALIZATION_INTERVAL=10           # Destination visualization update interval

# Nftables settings
NFTABLES_TABLES=("inet" "ip" "bridge")
NFTABLES_CHAINS=("input" "forward")

# Nmap settings
NMAP_TARGETS="192.168.201.0/24 192.168.200.1"
NMAP_OPTIONS="-sn -T4 --max-retries 1 --host-timeout 5s"

# Gonzo alert settings
GONZO_VOICES=(
    "male1:-20:80"      # System alerts - deep, slow
    "female1:0:90"      # Device alerts - normal, high energy
    "male2:10:70"       # Threat alerts - fast, urgent
    "female2:-10:85"    # Status alerts - measured, confident
)

# Alert escalation levels
ALERT_LEVELS=(
    "info"      # Blue - informational
    "warning"   # Yellow - concerning
    "alert"     # Orange - active threat
    "critical"  # Red - immediate danger
)

# Sound effects (beep patterns)
BEEP_PATTERNS=(
    "info:1:0.1"        # Single beep
    "warning:2:0.15"    # Double beep
    "alert:3:0.2"       # Triple beep
    "critical:5:0.1"    # Rapid fire
)

# Logging settings
LOG_LEVEL="warning"          # debug, info, warning, error
LOG_MAX_SIZE=10485760     # 10MB max log size
LOG_ROTATION_COUNT=5      # Keep 5 rotated logs

# Data persistence
DATA_RETENTION_DAYS=30    # Keep historical data for 30 days
TOPOLOGY_UPDATE_INTERVAL=60  # Update topology every minute

# Docker integration (if available)
DOCKER_MONITOR_ENABLED=false
DOCKER_NETWORKS=("bridge" "host" "none")

# SDR integration (if available)
SDR_ENABLED=false
SDR_FREQUENCIES=("433.92e6" "868e6" "915e6")  # Common IoT frequencies

# Advanced features
EVENT_CORRELATION_ENABLED=true
ANOMALY_DETECTION_ENABLED=true
HISTORICAL_ANALYSIS_ENABLED=true

# Performance tuning
MAX_CONCURRENT_PROCESSES=4
CPU_USAGE_LIMIT=50        # Max CPU percentage
MEMORY_LIMIT=100          # Max memory in MB
