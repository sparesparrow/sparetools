#!/bin/bash
# Docker Launcher for Enhanced Static Analysis MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Docker configuration
IMAGE_NAME="sparetools-mcp-static-analysis"
CONTAINER_NAME="sparetools-mcp-static-analysis-server"
DOCKERFILE="$PROJECT_ROOT/docker/Dockerfile"

# Default values
HOST="0.0.0.0"
PORT="8001"
MODE="production"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --build)
      BUILD_ONLY=true
      shift
      ;;
    --rebuild)
      REBUILD=true
      shift
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --detach|-d)
      DETACH=true
      shift
      ;;
    --help|-h)
      echo "Docker Launcher for Enhanced Static Analysis MCP Server"
      echo ""
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --build          Build Docker image only"
      echo "  --rebuild        Rebuild Docker image"
      echo "  --host HOST      Server host [default: 0.0.0.0]"
      echo "  --port PORT      Server port [default: 8001]"
      echo "  --mode MODE      Deployment mode [default: production]"
      echo "  --detach, -d     Run in detached mode"
      echo "  --help, -h       Show this help message"
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

# Build Docker image if requested or if it doesn't exist
if [[ "$REBUILD" == "true" ]] || [[ "$BUILD_ONLY" == "true" ]] || ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "Building Docker image: $IMAGE_NAME"

  # Create docker directory if it doesn't exist
  mkdir -p "$PROJECT_ROOT/docker"

  # Create Dockerfile if it doesn't exist
  if [[ ! -f "$DOCKERFILE" ]]; then
    cat > "$DOCKERFILE" << 'EOF'
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    cppcheck \
    valgrind \
    gdb \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/.mcp && \
    chown -R app:app /app

# Switch to app user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Set environment
ENV PYTHONPATH=/app/src
ENV STATIC_ANALYSIS_MODE=production

# Run the server
CMD ["python", "-m", "sparetools.mcp_servers.static_analysis.static_analysis_mcp_server"]
EOF
  fi

  # Build the image
  docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" "$PROJECT_ROOT"

  if [[ "$BUILD_ONLY" == "true" ]]; then
    echo "Docker image built successfully: $IMAGE_NAME"
    exit 0
  fi
fi

# Stop existing container if running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
  echo "Stopping existing container: $CONTAINER_NAME"
  docker stop "$CONTAINER_NAME" >/dev/null
fi

# Remove existing container
if docker ps -a -q -f name="$CONTAINER_NAME" | grep -q .; then
  echo "Removing existing container: $CONTAINER_NAME"
  docker rm "$CONTAINER_NAME" >/dev/null
fi

# Prepare environment variables
ENV_VARS=(
  "--env" "STATIC_ANALYSIS_MODE=$MODE"
  "--env" "STATIC_ANALYSIS_HOST=$HOST"
  "--env" "STATIC_ANALYSIS_PORT=$PORT"
)

# Add MCP-Prompts environment variables if set
if [[ -n "$MCP_PROMPTS_SERVER_URL" ]]; then
  ENV_VARS+=("--env" "MCP_PROMPTS_SERVER_URL=$MCP_PROMPTS_SERVER_URL")
fi

if [[ -n "$MCP_PROMPTS_API_KEY" ]]; then
  ENV_VARS+=("--env" "MCP_PROMPTS_API_KEY=$MCP_PROMPTS_API_KEY")
fi

# Prepare run command
RUN_CMD=(
  docker run
  --name "$CONTAINER_NAME"
  --publish "$PORT:$PORT"
  --mount "type=bind,source=$PROJECT_ROOT/config,target=/app/config,readonly"
  --mount "type=volume,source=sparetools-mcp-data,target=/app/data"
  "${ENV_VARS[@]}"
)

# Add detach flag if requested
if [[ "$DETACH" == "true" ]]; then
  RUN_CMD+=("--detach")
fi

# Add image name
RUN_CMD+=("$IMAGE_NAME")

echo "Starting container: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME"
echo "Port: $PORT"
echo "Mode: $MODE"
echo ""

# Run the container
"${RUN_CMD[@]}"

if [[ "$DETACH" == "true" ]]; then
  echo "Container started in detached mode"
  echo "To view logs: docker logs $CONTAINER_NAME"
  echo "To stop: docker stop $CONTAINER_NAME"
else
  echo "Container started. Press Ctrl+C to stop."
fi