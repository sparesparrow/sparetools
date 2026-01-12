#!/bin/bash
# Enhanced Static Analysis MCP Server Launcher
# Supports different deployment modes and configuration options

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
CONFIG_DIR="$PROJECT_ROOT/src/sparetools/mcp_servers/static_analysis/config"

# Default values
MODE="development"
HOST="localhost"
PORT="8001"
LOG_LEVEL="INFO"
CONFIG_FILE="$CONFIG_DIR/default_config.yaml"
PYTHONPATH="$SRC_DIR:$PYTHONPATH"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --log-level)
      LOG_LEVEL="$2"
      shift 2
      ;;
    --config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    --production)
      MODE="production"
      LOG_LEVEL="WARNING"
      shift
      ;;
    --development|--dev)
      MODE="development"
      LOG_LEVEL="DEBUG"
      shift
      ;;
    --test)
      MODE="test"
      LOG_LEVEL="DEBUG"
      shift
      ;;
    --help|-h)
      echo "Enhanced Static Analysis MCP Server Launcher"
      echo ""
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --mode MODE          Deployment mode (development/production/test) [default: development]"
      echo "  --host HOST          Server host [default: localhost]"
      echo "  --port PORT          Server port [default: 8001]"
      echo "  --log-level LEVEL    Logging level [default: INFO]"
      echo "  --config FILE        Configuration file path"
      echo "  --production         Production mode (equivalent to --mode production --log-level WARNING)"
      echo "  --development        Development mode (equivalent to --mode development --log-level DEBUG)"
      echo "  --test               Test mode"
      echo "  --help, -h           Show this help message"
      echo ""
      echo "Environment Variables:"
      echo "  MCP_PROMPTS_SERVER_URL    MCP-Prompts server URL"
      echo "  MCP_PROMPTS_API_KEY       MCP-Prompts API key"
      echo "  STATIC_ANALYSIS_TIMEOUT   Analysis timeout in seconds"
      echo "  STATIC_ANALYSIS_MAX_WORKERS  Maximum concurrent workers"
      echo ""
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Set environment based on mode
case $MODE in
  production)
    export PYTHONPATH="$PYTHONPATH"
    export STATIC_ANALYSIS_MODE="production"
    export STATIC_ANALYSIS_LOG_LEVEL="$LOG_LEVEL"
    ;;
  development)
    export PYTHONPATH="$PYTHONPATH"
    export STATIC_ANALYSIS_MODE="development"
    export STATIC_ANALYSIS_LOG_LEVEL="$LOG_LEVEL"
    # Enable debug features
    export STATIC_ANALYSIS_DEBUG="true"
    ;;
  test)
    export PYTHONPATH="$PYTHONPATH"
    export STATIC_ANALYSIS_MODE="test"
    export STATIC_ANALYSIS_LOG_LEVEL="$LOG_LEVEL"
    export STATIC_ANALYSIS_TESTING="true"
    ;;
  *)
    echo "Invalid mode: $MODE"
    exit 1
    ;;
esac

# Validate configuration
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Warning: Configuration file not found: $CONFIG_FILE"
  echo "Using default configuration"
fi

# Set configuration environment variable
export STATIC_ANALYSIS_CONFIG_FILE="$CONFIG_FILE"

# Health check function
health_check() {
  local max_attempts=30
  local attempt=1

  echo "Waiting for server to be ready on $HOST:$PORT..."

  while [[ $attempt -le $max_attempts ]]; do
    if curl -f -s "http://$HOST:$PORT/health" > /dev/null 2>&1; then
      echo "Server is ready!"
      return 0
    fi

    echo "Attempt $attempt/$max_attempts: Server not ready yet..."
    sleep 2
    ((attempt++))
  done

  echo "Server failed to start within expected time"
  return 1
}

# Start server
echo "Starting Enhanced Static Analysis MCP Server in $MODE mode"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Log Level: $LOG_LEVEL"
echo "Config: $CONFIG_FILE"
echo ""

# Change to project directory
cd "$PROJECT_ROOT"

# Launch the server
python -m sparetools.mcp_servers.static_analysis.static_analysis_mcp_server &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"

# For production mode, perform health check
if [[ "$MODE" == "production" ]]; then
  if health_check; then
    echo "Server is running successfully"
  else
    echo "Server health check failed"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
  fi
fi

# Wait for server process
wait $SERVER_PID