#!/bin/bash
# FeedForward VPS Setup Script
# This script sets up FeedForward on a fresh VPS

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="feedforward"
PROJECT_DIR="/opt/feedforward"
SERVICE_USER="feedforward"
PYTHON_VERSION="3.10"

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

print_status "Starting FeedForward setup..."

# Update system packages
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    git \
    curl \
    build-essential \
    sqlite3

# Create service user
if ! id "$SERVICE_USER" &>/dev/null; then
    print_status "Creating service user..."
    useradd --system --shell /bin/bash --home-dir /home/$SERVICE_USER --create-home $SERVICE_USER
else
    print_status "Service user already exists"
fi

# Create project directory
print_status "Creating project directory..."
mkdir -p $PROJECT_DIR
chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

# Clone or pull the repository
if [ -d "$PROJECT_DIR/.git" ]; then
    print_status "Updating existing repository..."
    cd $PROJECT_DIR
    sudo -u $SERVICE_USER git pull
else
    print_status "Cloning repository..."
    print_warning "Please enter the Git repository URL:"
    read -r GIT_REPO_URL
    sudo -u $SERVICE_USER git clone "$GIT_REPO_URL" "$PROJECT_DIR"
fi

cd $PROJECT_DIR

# Install uv for the service user
print_status "Installing uv package manager..."
sudo -u $SERVICE_USER bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# Add uv to PATH for the service user
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /home/$SERVICE_USER/.bashrc

# Create virtual environment and install dependencies
print_status "Setting up Python environment..."
sudo -u $SERVICE_USER bash -c "
    source ~/.bashrc
    cd $PROJECT_DIR
    uv venv
    source .venv/bin/activate
    uv pip install -e '.[dev]'
"

# Create data directories
print_status "Creating data directories..."
sudo -u $SERVICE_USER mkdir -p $PROJECT_DIR/data $PROJECT_DIR/data/uploads

# Set up environment file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_status "Setting up environment configuration..."
    cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env
    chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/.env
    chmod 600 $PROJECT_DIR/.env
    
    print_warning "Please edit $PROJECT_DIR/.env and configure:"
    print_warning "  - APP_DOMAIN (your domain name)"
    print_warning "  - Admin credentials"
    print_warning "  - SMTP settings (if using email)"
    print_warning "  - API keys for AI providers"
    print_warning ""
    print_warning "Press Enter to continue after editing the file..."
    read -r
fi

# Initialize database
print_status "Initializing database..."
sudo -u $SERVICE_USER bash -c "
    cd $PROJECT_DIR
    source .venv/bin/activate
    python app/init_db.py
"

# Install systemd service
print_status "Installing systemd service..."
cp $PROJECT_DIR/deploy/feedforward.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable feedforward.service

# Start the service
print_status "Starting FeedForward service..."
systemctl start feedforward.service

# Check service status
if systemctl is-active --quiet feedforward.service; then
    print_status "FeedForward service is running!"
else
    print_error "FeedForward service failed to start. Check logs with: journalctl -u feedforward -f"
    exit 1
fi

# Display next steps
echo ""
print_status "FeedForward setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Caddy for reverse proxy (see deploy/Caddyfile.example)"
echo "2. Set up firewall rules if needed"
echo "3. Monitor logs: journalctl -u feedforward -f"
echo "4. Access the app at: http://localhost:5001 (or your configured domain)"
echo ""
echo "Service commands:"
echo "  - Start:   systemctl start feedforward"
echo "  - Stop:    systemctl stop feedforward"
echo "  - Restart: systemctl restart feedforward"
echo "  - Status:  systemctl status feedforward"
echo "  - Logs:    journalctl -u feedforward -f"