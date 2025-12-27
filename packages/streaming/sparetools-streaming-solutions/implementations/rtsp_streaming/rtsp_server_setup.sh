#!/bin/bash
# RTSP Server Setup Script
# Install and configure RTSP server dependencies

echo "Setting up RTSP streaming environment..."

# Update package list
sudo apt update

# Install GStreamer and RTSP server components
echo "Installing GStreamer and RTSP components..."
sudo apt install -y gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav

# Install GStreamer RTSP server
sudo apt install -y gstreamer1.0-rtsp

# Install FFmpeg for alternative RTSP server
sudo apt install -y ffmpeg

# Install Python GStreamer bindings
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0

# Install additional codecs
sudo apt install -y gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad

# Create RTSP server directory
mkdir -p /var/lib/rtsp-server
sudo chown $USER:$USER /var/lib/rtsp-server

# Create systemd service directory
sudo mkdir -p /etc/systemd/system

echo "RTSP server setup complete!"
echo "Available tools:"
echo "- gst-launch-1.0 (GStreamer)"
echo "- ffmpeg (FFmpeg RTSP server)"
echo "- Python GStreamer bindings"