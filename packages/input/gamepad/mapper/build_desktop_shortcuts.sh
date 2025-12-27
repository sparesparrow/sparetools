#!/bin/bash

echo "🎮 Building Gamepad Desktop Shortcuts"
echo "====================================="

# Create build directory
mkdir -p build-desktop-shortcuts
cd build-desktop-shortcuts

# Configure with CMake
echo "📋 Configuring build..."
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DWITH_X11=ON \
         -DWITH_WAYLAND=ON \
         -DWITH_KDE=ON \
         -DWITH_SDL2=ON \
         -DWITH_UINPUT=ON \
         -DWITH_CLIPBOARD=ON \
         -DWITH_BLUETOOTH=ON

if [ $? -ne 0 ]; then
    echo "❌ CMake configuration failed!"
    exit 1
fi

# Build the project
echo "🔨 Building..."
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully!"
echo ""
echo "🚀 To test the desktop shortcuts:"
echo "   ./test_desktop_shortcuts"
echo ""
echo "📋 Available configurations:"
echo "   - config/desktop_shortcuts_mappings.json (Main desktop shortcuts)"
echo "   - config/terminal_mappings.json (Terminal-specific shortcuts)"
echo "   - config/browser_mappings.json (Browser shortcuts)"
echo "   - config/professional_mappings.json (Advanced multi-controller setup)"
echo ""
echo "🎮 Connect your gamepad and enjoy desktop control!"
