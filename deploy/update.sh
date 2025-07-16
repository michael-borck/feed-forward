#!/bin/bash
# FeedForward Update Script
# This script updates FeedForward to the latest version

set -euo pipefail

# Configuration
PROJECT_DIR="/opt/feedforward"
SERVICE_USER="feedforward"
SERVICE_NAME="feedforward"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

print_status "Starting FeedForward update..."

# Change to project directory
cd $PROJECT_DIR

# Stop the service
print_status "Stopping FeedForward service..."
systemctl stop $SERVICE_NAME

# Backup database
print_status "Backing up database..."
BACKUP_DIR="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
sudo -u $SERVICE_USER mkdir -p "$BACKUP_DIR"
sudo -u $SERVICE_USER cp -r data/*.db "$BACKUP_DIR/" 2>/dev/null || true
sudo -u $SERVICE_USER cp .env "$BACKUP_DIR/.env.backup"

# Pull latest changes
print_status "Pulling latest code..."
sudo -u $SERVICE_USER git pull

# Update dependencies
print_status "Updating dependencies..."
sudo -u $SERVICE_USER bash -c "
    source ~/.bashrc
    cd $PROJECT_DIR
    source .venv/bin/activate
    uv pip install -e '.[dev]'
"

# Run any database migrations
print_status "Checking for database migrations..."
if [ -f "app/migrate.py" ]; then
    sudo -u $SERVICE_USER bash -c "
        cd $PROJECT_DIR
        source .venv/bin/activate
        python app/migrate.py
    "
else
    print_status "No migrations to run"
fi

# Update systemd service file if changed
if ! diff -q deploy/feedforward.service /etc/systemd/system/feedforward.service >/dev/null 2>&1; then
    print_status "Updating systemd service file..."
    cp deploy/feedforward.service /etc/systemd/system/
    systemctl daemon-reload
fi

# Start the service
print_status "Starting FeedForward service..."
systemctl start $SERVICE_NAME

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    print_status "FeedForward service is running!"
    print_status "Update completed successfully!"
else
    print_error "FeedForward service failed to start!"
    print_error "Rolling back to previous version..."
    
    # Rollback
    sudo -u $SERVICE_USER git reset --hard HEAD~1
    systemctl start $SERVICE_NAME
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_warning "Rolled back to previous version"
        print_error "Update failed! Check logs: journalctl -u $SERVICE_NAME -f"
    else
        print_error "Rollback failed! Manual intervention required."
        print_error "Backup location: $BACKUP_DIR"
    fi
    exit 1
fi

# Show recent logs
print_status "Recent logs:"
journalctl -u $SERVICE_NAME -n 20 --no-pager

echo ""
print_status "Update complete!"
print_status "Backup saved to: $BACKUP_DIR"