#!/bin/bash
# SSHFS mount script for development server

MOUNT_POINT="$HOME/mnt/dev-server"
REMOTE_PATH="/home/sparrow"

# Create mount point if it doesn't exist
mkdir -p "$MOUNT_POINT"

# Check if already mounted
if mountpoint -q "$MOUNT_POINT"; then
    echo "Already mounted at $MOUNT_POINT"
    exit 0
fi

# Mount using SSHFS
echo "Mounting dev-server at $MOUNT_POINT..."
sshfs sshfs-dev:"$REMOTE_PATH" "$MOUNT_POINT" \
    -o allow_other \
    -o uid=$(id -u) \
    -o gid=$(id -g) \
    -o follow_symlinks

if [ $? -eq 0 ]; then
    echo "Successfully mounted dev-server at $MOUNT_POINT"
    echo "Access your files at: $MOUNT_POINT"
else
    echo "Failed to mount dev-server"
    exit 1
fi
