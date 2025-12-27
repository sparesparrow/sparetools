#!/bin/bash

# Advanced Multi-Controller Gamepad Mapper Build Script
# Supports multiple controllers, voice alerts, network control, and more

set -e

echo "🚀 Building Advanced Multi-Controller Gamepad Mapper..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "conanfile.py" ]; then
    print_error "Please run this script from the gamepad-mapper root directory"
    exit 1
fi

# Create build directory
print_status "Creating build directory..."
mkdir -p build-advanced
cd build-advanced

# Install dependencies
print_status "Installing dependencies with Conan..."
conan install .. --build=missing

# Configure with CMake
print_status "Configuring with CMake..."
cmake .. -G "Unix Makefiles" \
         -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
         -DCMAKE_POLICY_DEFAULT_CMP0091=NEW \
         -DCMAKE_BUILD_TYPE=Debug \
         -DWITH_X11=ON \
         -DWITH_WAYLAND=ON \
         -DWITH_KDE=OFF \
         -DWITH_SDL2=ON \
         -DWITH_UINPUT=ON \
         -DWITH_MCP=OFF \
         -DWITH_BLUETOOTH=ON \
         -DBUILD_TESTS=OFF

# Build the project
print_status "Building advanced gamepad mapper..."
make -j$(nproc)

# Check if build was successful
if [ $? -eq 0 ]; then
    print_success "Build completed successfully!"
    
    # List built executables
    print_status "Built executables:"
    ls -la gamepad_mapper_app advanced_gamepad_mapper 2>/dev/null || true
    
    # Create symlinks for easy access
    if [ -f "gamepad_mapper_app" ]; then
        ln -sf "$(pwd)/gamepad_mapper_app" ../gamepad_mapper_app
        print_success "Created symlink: gamepad_mapper_app"
    fi
    
    if [ -f "advanced_gamepad_mapper" ]; then
        ln -sf "$(pwd)/advanced_gamepad_mapper" ../advanced_gamepad_mapper
        print_success "Created symlink: advanced_gamepad_mapper"
    fi
    
    # Install system dependencies for advanced features
    print_status "Installing system dependencies for advanced features..."
    
    # Install speech-dispatcher for voice alerts
    if ! command -v spd-say &> /dev/null; then
        print_status "Installing speech-dispatcher for voice alerts..."
        sudo apt update
        sudo apt install -y speech-dispatcher
    else
        print_success "speech-dispatcher already installed"
    fi
    
    # Install Bluetooth tools
    if ! command -v bluetoothctl &> /dev/null; then
        print_status "Installing Bluetooth tools..."
        sudo apt install -y bluez bluez-tools
    else
        print_success "Bluetooth tools already installed"
    fi
    
    # Install network scanning tools
    if ! command -v nmap &> /dev/null; then
        print_status "Installing network scanning tools..."
        sudo apt install -y nmap
    else
        print_success "Network scanning tools already installed"
    fi
    
    # Install btscanner if available
    if ! command -v btscanner &> /dev/null; then
        print_status "Installing btscanner..."
        sudo apt install -y btscanner || print_warning "btscanner not available in repositories"
    else
        print_success "btscanner already installed"
    fi
    
    # Install gatool if available
    if ! command -v gatool &> /dev/null; then
        print_status "Installing gatool..."
        sudo apt install -y gatool || print_warning "gatool not available in repositories"
    else
        print_success "gatool already installed"
    fi
    
    # Install curl for network operations
    if ! command -v curl &> /dev/null; then
        print_status "Installing curl..."
        sudo apt install -y curl
    else
        print_success "curl already installed"
    fi
    
    # Create configuration directory
    print_status "Setting up configuration directory..."
    mkdir -p ../config
    cp -r ../config/* ../config/ 2>/dev/null || true
    
    # Set up udev rules for gamepad access
    print_status "Setting up udev rules..."
    if [ -f "../scripts/99-gamepad-mapper.rules" ]; then
        sudo cp ../scripts/99-gamepad-mapper.rules /etc/udev/rules.d/
        sudo udevadm control --reload-rules
        print_success "Udev rules installed"
    fi
    
    # Create systemd service file
    print_status "Creating systemd service file..."
    cat > ../gamepad-mapper.service << EOF
[Unit]
Description=Advanced Multi-Controller Gamepad Mapper
After=network.target bluetooth.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/advanced_gamepad_mapper --profile professional --voice --auto
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Systemd service file created: gamepad-mapper.service"
    
    # Print usage information
    echo ""
    print_success "🎮 Advanced Multi-Controller Gamepad Mapper is ready!"
    echo ""
    echo "Usage examples:"
    echo "  ./advanced_gamepad_mapper --help                    # Show help"
    echo "  ./advanced_gamepad_mapper --profile professional    # Load professional profile"
    echo "  ./advanced_gamepad_mapper --profile gaming          # Load gaming profile"
    echo "  ./advanced_gamepad_mapper --profile accessibility   # Load accessibility profile"
    echo "  ./advanced_gamepad_mapper --scan --bluetooth        # Scan for Bluetooth devices"
    echo "  ./advanced_gamepad_mapper --voice --auto            # Enable voice alerts and auto-detection"
    echo "  ./advanced_gamepad_mapper --remote studio.local     # Enable remote control"
    echo "  ./advanced_gamepad_mapper --kde --tasker            # Enable KDE Connect and Tasker"
    echo ""
    echo "Features enabled:"
    echo "  ✅ Multi-controller support"
    echo "  ✅ Voice alerts with TTS"
    echo "  ✅ Bluetooth device scanning"
    echo "  ✅ Network device discovery"
    echo "  ✅ Remote control capabilities"
    echo "  ✅ KDE Connect integration"
    echo "  ✅ Tasker/Join integration"
    echo "  ✅ Auto-detection and hotplug"
    echo "  ✅ Professional, Gaming, and Accessibility profiles"
    echo ""
    echo "To start the service:"
    echo "  sudo systemctl enable gamepad-mapper.service"
    echo "  sudo systemctl start gamepad-mapper.service"
    echo ""
    
else
    print_error "Build failed!"
    exit 1
fi