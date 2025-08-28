#!/bin/bash
# Quick fix for VPS permission issues

echo "Fixing FeedForward data directory permissions..."

# Create data directory on host
mkdir -p ./data
mkdir -p ./data/uploads

# Set permissions (writable by container's feedforward user - UID 1000)
sudo chown -R 1000:1000 ./data
sudo chmod -R 755 ./data

echo "Data directory created and permissions set."
echo "Now you can run: docker compose up -d"