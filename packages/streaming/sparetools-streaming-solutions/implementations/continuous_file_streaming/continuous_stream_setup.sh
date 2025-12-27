#!/bin/bash
# Continuous Stream Setup Script
# Setup optimized continuous streaming environment

echo "Setting up continuous file streaming environment..."

# Update package list
sudo apt update

# Install required tools
echo "Installing required tools..."
sudo apt install -y ffmpeg inotify-tools

# Install Python dependencies
pip3 install --user psutil

# Create continuous streaming directory
mkdir -p /var/lib/continuous-stream
sudo chown $USER:$USER /var/lib/continuous-stream

# Create optimized MiniDLNA configuration
sudo tee /etc/minidlna/continuous-stream.conf > /dev/null <<EOF
# Continuous Stream Configuration
media_dir=V,/var/lib/continuous-stream
friendly_name=Sparrow-Continuous-Stream
port=8200
presentation_url=http://$(hostname -I | awk '{print $1}'):8200/
inotify=yes
enable_subtitles=no
strict_dlna=no
EOF

# Create systemd service for continuous streaming
sudo tee /etc/systemd/system/continuous-stream.service > /dev/null <<EOF
[Unit]
Description=Continuous Screen Stream Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/lib/continuous-stream
ExecStart=/home/$USER/continuous_file_streaming/optimized_continuous_cast.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable continuous-stream.service

echo "Continuous stream setup complete!"
echo "Service: continuous-stream.service"
echo "Configuration: /etc/minidlna/continuous-stream.conf"
echo "Stream directory: /var/lib/continuous-stream"