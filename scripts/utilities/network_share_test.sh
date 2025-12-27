#!/bin/bash

# Network File Sharing Test Script
# Run this from 192.168.200.23 to test all protocols

SERVER_IP="192.168.200.160"
USERNAME="sparrow"
PASSWORD="pppppppp"

echo "=== Network File Sharing Test ==="
echo "Server: $SERVER_IP"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo

# Test SSH/SFTP
echo "=== Testing SSH/SFTP ==="
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "echo 'SSH login successful'" || echo "SSH test failed"

echo
echo "=== Testing SFTP ==="
sshpass -p "$PASSWORD" sftp -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP << EOF
ls -la
put /dev/null test_file.txt
rm test_file.txt
bye
EOF

# Test NFS
echo
echo "=== Testing NFS ==="
sudo mkdir -p /mnt/nfs_test
sudo mount -t nfs $SERVER_IP:/home/sparrow /mnt/nfs_test
if mount | grep -q "/mnt/nfs_test"; then
    echo "NFS mount successful"
    ls -la /mnt/nfs_test | head -3
    touch /mnt/nfs_test/nfs_test_file.txt
    echo "test content" > /mnt/nfs_test/nfs_test_file.txt
    ls -la /mnt/nfs_test/nfs_test_file.txt
    rm /mnt/nfs_test/nfs_test_file.txt
    sudo umount /mnt/nfs_test
    echo "NFS test completed"
else
    echo "NFS mount failed"
fi

# Test SMB
echo
echo "=== Testing SMB ==="
sudo mkdir -p /mnt/smb_test
sudo mount -t cifs //$SERVER_IP/home /mnt/smb_test -o username=$USERNAME,password=$PASSWORD
if mount | grep -q "/mnt/smb_test"; then
    echo "SMB mount successful"
    ls -la /mnt/smb_test | head -3
    touch /mnt/smb_test/smb_test_file.txt
    echo "test content" > /mnt/smb_test/smb_test_file.txt
    ls -la /mnt/smb_test/smb_test_file.txt
    rm /mnt/smb_test/smb_test_file.txt
    sudo umount /mnt/smb_test
    echo "SMB test completed"
else
    echo "SMB mount failed"
fi

echo
echo "=== Test Summary ==="
echo "All protocols configured and listening on $SERVER_IP:"
echo "- SSH/SFTP: port 22"
echo "- NFS: port 2049"
echo "- SMB: ports 139, 445"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"