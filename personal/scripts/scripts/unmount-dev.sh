#!/bin/bash
# SSHFS unmount script for development server

MOUNT_POINT="$HOME/mnt/dev-server"

if mountpoint -q "$MOUNT_POINT"; then
    echo "Unmounting dev-server from $MOUNT_POINT..."
    fusermount -u "$MOUNT_POINT"
    if [ $? -eq 0 ]; then
        echo "Successfully unmounted dev-server"
    else
        echo "Failed to unmount dev-server"
        exit 1
    fi
else
    echo "Dev-server is not mounted at $MOUNT_POINT"
fi
