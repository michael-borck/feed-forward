# FeedForward VPS Deployment Guide

This guide walks you through deploying FeedForward on a VPS with Caddy as the reverse proxy.

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ VPS
- Root access to the server
- A domain name pointing to your VPS
- Git repository with your FeedForward code

## Quick Start

1. **SSH into your VPS**
   ```bash
   ssh root@your-vps-ip
   ```

2. **Clone this repository** (or upload it)
   ```bash
   git clone https://github.com/yourusername/feedforward.git /tmp/feedforward
   cd /tmp/feedforward
   ```

3. **Run the setup script**
   ```bash
   bash deploy/setup.sh
   ```

4. **Configure Caddy** (if not already installed)
   ```bash
   # Install Caddy
   apt install -y debian-keyring debian-archive-keyring apt-transport-https
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
   apt update
   apt install caddy
   
   # Configure Caddy for FeedForward
   cp deploy/Caddyfile.example /etc/caddy/Caddyfile
   # Edit /etc/caddy/Caddyfile and replace "feedforward.yourdomain.com" with your domain
   
   # Restart Caddy
   systemctl restart caddy
   ```

## Detailed Setup Steps

### 1. Initial Server Setup

The `setup.sh` script handles most of the setup, but here's what it does:

- Creates a dedicated `feedforward` system user
- Installs Python 3.10 and system dependencies
- Sets up the project in `/opt/feedforward`
- Installs uv package manager
- Creates a Python virtual environment
- Installs all Python dependencies
- Initializes the database
- Configures and starts the systemd service

### 2. Environment Configuration

After running the setup script, you need to configure your environment:

```bash
# Edit the environment file
nano /opt/feedforward/.env
```

Key settings to configure:
- `APP_DOMAIN`: Your full domain (e.g., https://feedforward.yourdomain.com)
- `ADMIN_EMAIL` and `ADMIN_PASSWORD`: Admin credentials
- `SMTP_*`: Email settings for sending invitations
- API keys for AI providers (at least one required)

### 3. Caddy Configuration

Edit the Caddy configuration:

```bash
nano /etc/caddy/Caddyfile
```

Replace `feedforward.yourdomain.com` with your actual domain. The provided configuration includes:
- Automatic HTTPS with Let's Encrypt
- Security headers
- WebSocket support for FastHTML
- Request size limits
- Compression

### 4. Firewall Configuration (Optional)

If you're using UFW:

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## Managing FeedForward

### Service Commands

```bash
# Start the service
systemctl start feedforward

# Stop the service
systemctl stop feedforward

# Restart the service
systemctl restart feedforward

# Check service status
systemctl status feedforward

# View logs
journalctl -u feedforward -f
```

### Updating FeedForward

Use the provided update script:

```bash
cd /opt/feedforward
sudo bash deploy/update.sh
```

This script will:
- Stop the service
- Backup the database
- Pull latest code
- Update dependencies
- Run any migrations
- Restart the service

### Manual Updates

If you need to update manually:

```bash
cd /opt/feedforward
systemctl stop feedforward
sudo -u feedforward git pull
sudo -u feedforward bash -c "source .venv/bin/activate && uv pip install -e '.[dev]'"
systemctl start feedforward
```

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   journalctl -u feedforward -n 100
   ```

2. Check permissions:
   ```bash
   ls -la /opt/feedforward
   chown -R feedforward:feedforward /opt/feedforward
   ```

3. Verify environment file:
   ```bash
   sudo -u feedforward cat /opt/feedforward/.env
   ```

### Database Issues

1. Check database exists:
   ```bash
   ls -la /opt/feedforward/data/
   ```

2. Re-initialize if needed:
   ```bash
   cd /opt/feedforward
   sudo -u feedforward bash -c "source .venv/bin/activate && python app/init_db.py"
   ```

### Caddy Issues

1. Test configuration:
   ```bash
   caddy validate --config /etc/caddy/Caddyfile
   ```

2. Check Caddy logs:
   ```bash
   journalctl -u caddy -f
   ```

### Application Errors

1. Enable debug mode temporarily:
   ```bash
   # Edit .env and set DEBUG=true
   nano /opt/feedforward/.env
   systemctl restart feedforward
   ```

2. Check Python dependencies:
   ```bash
   sudo -u feedforward bash -c "cd /opt/feedforward && source .venv/bin/activate && pip list"
   ```

## Backup and Recovery

### Automated Backups

Create a cron job for regular backups:

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /opt/feedforward/deploy/backup.sh
```

Create `/opt/feedforward/deploy/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/feedforward/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/feedforward/data/*.db "$BACKUP_DIR/"
cp /opt/feedforward/.env "$BACKUP_DIR/.env.backup"
# Keep only last 7 days of backups
find /opt/feedforward/backups -type d -mtime +7 -exec rm -rf {} +
```

### Manual Backup

```bash
cd /opt/feedforward
tar -czf feedforward-backup-$(date +%Y%m%d).tar.gz data/ .env
```

### Restore from Backup

```bash
systemctl stop feedforward
cd /opt/feedforward
tar -xzf feedforward-backup-20240101.tar.gz
systemctl start feedforward
```

## Security Recommendations

1. **Regular Updates**
   - Keep system packages updated: `apt update && apt upgrade`
   - Update FeedForward regularly using the update script

2. **Secure Environment File**
   ```bash
   chmod 600 /opt/feedforward/.env
   chown feedforward:feedforward /opt/feedforward/.env
   ```

3. **Database Permissions**
   ```bash
   chmod 600 /opt/feedforward/data/*.db
   ```

4. **Monitor Logs**
   - Set up log rotation
   - Monitor for suspicious activity

5. **API Key Security**
   - Use strong, unique API keys
   - Rotate keys periodically
   - Never commit keys to version control

## Support

For issues or questions:
1. Check the logs first: `journalctl -u feedforward -f`
2. Review this documentation
3. Check the main project documentation
4. Submit issues to the project repository