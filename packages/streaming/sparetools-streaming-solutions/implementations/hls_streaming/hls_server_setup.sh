#!/bin/bash
# HLS Server Setup Script
# Install and configure HLS server dependencies

echo "Setting up HLS streaming environment..."

# Update package list
sudo apt update

# Install FFmpeg for HLS generation
echo "Installing FFmpeg..."
sudo apt install -y ffmpeg

# Install Python HTTP server dependencies
sudo apt install -y python3-pip
pip3 install --user flask flask-cors

# Install nginx for production HLS serving (optional)
sudo apt install -y nginx

# Create HLS server directory
mkdir -p /var/lib/hls-server
mkdir -p /var/lib/hls-server/segments
sudo chown $USER:$USER /var/lib/hls-server
sudo chown $USER:$USER /var/lib/hls-server/segments

# Create nginx configuration for HLS
sudo tee /etc/nginx/sites-available/hls-server > /dev/null <<EOF
server {
    listen 8080;
    server_name localhost;
    
    location /hls/ {
        alias /var/lib/hls-server/;
        add_header Cache-Control no-cache;
        add_header Access-Control-Allow-Origin *;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/hls-server /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "HLS server setup complete!"
echo "Available tools:"
echo "- ffmpeg (HLS generation)"
echo "- nginx (HTTP server on port 8080)"
echo "- Python Flask server"