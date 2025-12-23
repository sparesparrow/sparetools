# SpareTools Conan Docker Environment

This directory contains Docker configurations for running Conan package management commands in a consistent, isolated environment.

## Quick Start

### Prerequisites
- Docker installed and running
- Git (for cloning repositories)

### Basic Usage

1. **Start the Conan environment:**
   ```bash
   ./scripts/run-conan-docker.sh
   ```

2. **Run Conan commands:**
   ```bash
   # Check Conan version
   ./scripts/run-conan-docker.sh --version

   # List available packages
   ./scripts/run-conan-docker.sh list "sparetools-*"

   # Create a package
   ./scripts/run-conan-docker.sh create packages/foundation/sparetools-base --version=2.0.3

   # Upload packages
   ./scripts/run-conan-docker.sh upload "sparetools-base/2.0.3" -r sparesparrow-conan --confirm
   ```

## Environment Setup

### 1. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.conan.example .env
```

Edit `.env` and add your Cloudsmith API key:
```bash
CLOUDSMITH_API_KEY=your_actual_api_key_here
```

### 2. Build and Run

The first run will automatically build the Docker image and start the container:

```bash
# This will build the image and start the container
./scripts/run-conan-docker.sh --version
```

### 3. Interactive Shell

Enter the Docker container for interactive Conan work:

```bash
./scripts/run-conan-docker.sh
```

This will give you a bash shell inside the container where you can run multiple Conan commands.

## Available Commands

### Package Management
```bash
# List local packages
./scripts/run-conan-docker.sh list "sparetools-*"

# List remote packages
./scripts/run-conan-docker.sh list "sparetools-*" -r sparesparrow-conan

# Search for packages
./scripts/run-conan-docker.sh search "sparetools-*" -r sparesparrow-conan

# Show package information
./scripts/run-conan-docker.sh inspect sparetools-base/2.0.3
```

### Package Creation
```bash
# Create a package
./scripts/run-conan-docker.sh create packages/foundation/sparetools-base --version=2.0.3 --build=missing

# Create with specific options
./scripts/run-conan-docker.sh create packages/embedded/sparetools-hal-sunton --version=1.0.0 -o with_lvgl=False --build=missing
```

### Publishing
```bash
# Authenticate with Cloudsmith
./scripts/run-conan-docker.sh remote login sparesparrow-conan spare-sparrow --password "$CLOUDSMITH_API_KEY"

# Upload packages
./scripts/run-conan-docker.sh upload "sparetools-base/2.0.3" -r sparesparrow-conan --confirm

# Upload all sparetools packages
./scripts/run-conan-docker.sh upload "sparetools-*/*" -r sparesparrow-conan --confirm
```

### Cache Management
```bash
# Show cache location
./scripts/run-conan-docker.sh cache path

# Clean cache
./scripts/run-conan-docker.sh cache clean

# List cached packages
./scripts/run-conan-docker.sh cache list "sparetools-*"
```

## Docker Configuration

### Files Overview

- `Dockerfile.conan` - Docker image definition with all required dependencies
- `docker-compose.conan.yml` - Docker Compose configuration (alternative to manual container management)
- `scripts/run-conan-docker.sh` - Convenience script for running Conan commands
- `.env.conan.example` - Environment variables template

### Included Dependencies

The Docker image includes:
- **Python 3.12** with pip
- **Conan 2.21.0** package manager
- **Build tools**: CMake, Ninja, GCC, Clang
- **Development libraries**: OpenSSL, zlib, etc.
- **Git** for repository operations
- **Pre-configured Conan remotes**:
  - `conancenter` (official ConanCenter)
  - `sparesparrow-conan` (SpareTools Cloudsmith repository)

### Volume Mounts

- `/workspace` - Mounted to your project root
- `conan-cache` - Persistent Conan cache volume

## Advanced Usage

### Using Docker Compose (Alternative)

```bash
# Start the container
docker-compose -f docker-compose.conan.yml up -d

# Run commands
docker-compose -f docker-compose.conan.yml exec conan-env conan --version

# Stop the container
docker-compose -f docker-compose.conan.yml down
```

### Building Custom Images

To modify the Docker image:

```bash
# Edit Dockerfile.conan
vim Dockerfile.conan

# Rebuild the image
docker build -f Dockerfile.conan -t sparetools-conan-env .

# Or use the script (it will rebuild automatically)
./scripts/run-conan-docker.sh --version
```

### Debugging

Enable verbose logging:
```bash
export CONAN_TRACE_FILE=/workspace/conan-debug.log
./scripts/run-conan-docker.sh --version
```

Check container logs:
```bash
docker logs sparetools-conan
```

Enter container manually:
```bash
docker exec -it sparetools-conan /bin/bash
```

## Troubleshooting

### Container Won't Start
```bash
# Check Docker is running
docker info

# Remove existing container
docker rm -f sparetools-conan

# Try again
./scripts/run-conan-docker.sh --version
```

### Conan Authentication Issues
```bash
# Check API key is set
echo $CLOUDSMITH_API_KEY

# Re-authenticate
./scripts/run-conan-docker.sh remote logout sparesparrow-conan
./scripts/run-conan-docker.sh remote login sparesparrow-conan spare-sparrow --password "$CLOUDSMITH_API_KEY"
```

### Build Failures
```bash
# Check available disk space
docker system df

# Clear Docker cache
docker system prune -f

# Rebuild image
docker rmi sparetools-conan-env
./scripts/run-conan-docker.sh --version
```

## Integration with CI/CD

This Docker setup is designed to work with CI/CD pipelines. Example GitHub Actions usage:

```yaml
- name: Build Package in Docker
  run: |
    ./scripts/run-conan-docker.sh create packages/foundation/sparetools-base --version=2.0.3 --build=missing

- name: Publish Package
  run: |
    ./scripts/run-conan-docker.sh upload "sparetools-base/2.0.3" -r sparesparrow-conan --confirm
  env:
    CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

## Security Notes

- The Cloudsmith API key is passed as an environment variable
- The Conan cache is persisted in a Docker volume
- No sensitive data is baked into the Docker image
- Use `.env` files for local development (add to `.gitignore`)

## Contributing

When modifying the Docker environment:
1. Update `Dockerfile.conan` for dependency changes
2. Test with `./scripts/run-conan-docker.sh --version`
3. Update this README if the interface changes
4. Ensure backward compatibility

---

For questions or issues, see the main SpareTools documentation or create an issue in the repository.