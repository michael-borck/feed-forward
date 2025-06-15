---
layout: default
title: Installation Guide
parent: Deployment
nav_order: 2
---

# Production Installation Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This guide provides detailed instructions for deploying FeedForward in a production environment. It covers server preparation, application installation, configuration, and verification steps.

## Pre-Installation Checklist

Before beginning installation, ensure you have:

- [ ] Server meeting [system requirements](./requirements)
- [ ] Root or sudo access to the server
- [ ] Domain name configured and pointing to server
- [ ] SSL certificate (or plan to use Let's Encrypt)
- [ ] AI provider API keys
- [ ] SMTP server credentials
- [ ] Backup storage location

## Server Preparation

### Step 1: Update System

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y
sudo apt install -y software-properties-common

# RHEL/CentOS
sudo yum update -y
sudo yum install -y epel-release
```

### Step 2: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    nginx \
    supervisor \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# RHEL/CentOS
sudo yum install -y \
    python310 \
    python310-devel \
    python310-pip \
    git \
    nginx \
    supervisor \
    sqlite \
    gcc \
    openssl-devel
```

### Step 3: Create Application User

```bash
# Create dedicated user for security
sudo useradd -m -s /bin/bash feedforward
sudo usermod -aG sudo feedforward  # If admin access needed

# Set up directory structure
sudo mkdir -p /opt/feedforward
sudo chown feedforward:feedforward /opt/feedforward
```

## Application Installation

### Step 1: Clone Repository

```bash
# Switch to feedforward user
sudo su - feedforward

# Clone the repository
cd /opt
git clone https://github.com/michael-borck/feed-forward.git feedforward
cd feedforward

# For specific version/tag
git checkout v1.0.0  # Replace with desired version
```

### Step 2: Create Virtual Environment

```bash
# Create Python virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# For production, also install
pip install gunicorn
```

### Step 4: Initialize Database

```bash
# Create data directory
mkdir -p data

# Initialize database
python app/init_db.py

# Verify database creation
ls -la data/
# Should show: feedforward.db
```

## Configuration

### Step 1: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

Essential configuration:

```env
# Security (generate strong key)
SECRET_KEY=your-very-long-random-secret-key-here

# Application
APP_DOMAIN=https://feedforward.yourdomain.edu
APP_NAME=FeedForward
DEBUG=false

# Database
DATABASE_PATH=data/feedforward.db

# Email Configuration
SMTP_SERVER=smtp.yourdomain.edu
SMTP_PORT=587
SMTP_USER=feedforward@yourdomain.edu
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@yourdomain.edu
SMTP_USE_TLS=true

# AI Providers (add at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Session
SESSION_LIFETIME=86400
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

Generate secure secret key:

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Create Initial Admin

```bash
# Run admin creation script
python tools/create_admin.py

# Follow prompts:
# Email: admin@yourdomain.edu
# Name: System Administrator
# Password: [strong password]
```

## Web Server Configuration

### Step 1: Configure Gunicorn

Create systemd service file:

```bash
sudo nano /etc/systemd/system/feedforward.service
```

Add the following content:

```ini
[Unit]
Description=FeedForward Application
After=network.target

[Service]
User=feedforward
Group=feedforward
WorkingDirectory=/opt/feedforward
Environment="PATH=/opt/feedforward/venv/bin"
ExecStart=/opt/feedforward/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind unix:/opt/feedforward/feedforward.sock \
    --error-logfile /opt/feedforward/logs/gunicorn-error.log \
    --access-logfile /opt/feedforward/logs/gunicorn-access.log \
    --log-level info \
    app:app

Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 2: Configure Nginx

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/feedforward
```

Add the following:

```nginx
server {
    listen 80;
    server_name feedforward.yourdomain.edu;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name feedforward.yourdomain.edu;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/feedforward.crt;
    ssl_certificate_key /etc/ssl/private/feedforward.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # File Upload Limit
    client_max_body_size 10M;
    
    # Static Files
    location /static {
        alias /opt/feedforward/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://unix:/opt/feedforward/feedforward.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Monitoring endpoint
    location /health {
        proxy_pass http://unix:/opt/feedforward/feedforward.sock;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/feedforward /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### Step 3: SSL Certificate

#### Option A: Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d feedforward.yourdomain.edu

# Test auto-renewal
sudo certbot renew --dry-run
```

#### Option B: Commercial Certificate

```bash
# Copy certificate files
sudo cp your-cert.crt /etc/ssl/certs/feedforward.crt
sudo cp your-cert.key /etc/ssl/private/feedforward.key
sudo chmod 600 /etc/ssl/private/feedforward.key
```

## Service Management

### Start Services

```bash
# Create log directory
sudo mkdir -p /opt/feedforward/logs
sudo chown feedforward:feedforward /opt/feedforward/logs

# Enable and start FeedForward
sudo systemctl enable feedforward
sudo systemctl start feedforward

# Check status
sudo systemctl status feedforward
```

### Configure Log Rotation

Create logrotate configuration:

```bash
sudo nano /etc/logrotate.d/feedforward
```

Add:

```
/opt/feedforward/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 feedforward feedforward
    sharedscripts
    postrotate
        systemctl reload feedforward >/dev/null 2>&1
    endscript
}
```

## Database Optimization

### Configure SQLite for Production

```bash
# Run optimization script
cd /opt/feedforward
source venv/bin/activate
python tools/optimize_database.py
```

Or manually:

```sql
sqlite3 data/feedforward.db << EOF
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 30000000000;
VACUUM;
ANALYZE;
EOF
```

### Set Up Automated Maintenance

```bash
# Add to crontab
crontab -e

# Add these lines:
# Database optimization (weekly)
0 3 * * 0 cd /opt/feedforward && /opt/feedforward/venv/bin/python tools/optimize_database.py

# Privacy cleanup (hourly)
0 * * * * cd /opt/feedforward && /opt/feedforward/venv/bin/python tools/cleanup_drafts.py

# Backup (daily)
0 2 * * * cd /opt/feedforward && /opt/feedforward/venv/bin/python tools/backup.py
```

## Monitoring Setup

### Application Monitoring

Create monitoring endpoint check:

```bash
# Create monitoring script
nano /opt/feedforward/tools/monitor.sh
```

```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://localhost/health)
if [ $response -eq 200 ]; then
    echo "OK"
else
    echo "FAIL: HTTP $response"
    # Send alert
    echo "FeedForward health check failed" | mail -s "FeedForward Alert" admin@yourdomain.edu
fi
```

```bash
chmod +x /opt/feedforward/tools/monitor.sh

# Add to crontab (every 5 minutes)
*/5 * * * * /opt/feedforward/tools/monitor.sh
```

### System Monitoring

Install monitoring tools:

```bash
# Install basic monitoring
sudo apt install -y htop iotop nethogs

# For advanced monitoring, consider:
# - Prometheus + Grafana
# - New Relic
# - DataDog
```

## Security Hardening

### Firewall Configuration

```bash
# Ubuntu/Debian with UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# RHEL/CentOS with firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Fail2ban Setup

```bash
# Install fail2ban
sudo apt install fail2ban

# Create FeedForward jail
sudo nano /etc/fail2ban/jail.d/feedforward.conf
```

```ini
[feedforward]
enabled = true
port = https
filter = feedforward
logpath = /opt/feedforward/logs/access.log
maxretry = 5
bantime = 3600
```

## Verification Steps

### 1. Service Health

```bash
# Check services
sudo systemctl status feedforward
sudo systemctl status nginx

# Check processes
ps aux | grep gunicorn
```

### 2. Application Access

```bash
# Test local access
curl http://localhost:5001/health

# Test through Nginx
curl https://feedforward.yourdomain.edu/health
```

### 3. Functionality Tests

1. Browse to https://feedforward.yourdomain.edu
2. Log in with admin credentials
3. Create a test course
4. Configure an AI model
5. Send a test invitation

### 4. Error Logs

```bash
# Check for errors
tail -f /opt/feedforward/logs/gunicorn-error.log
tail -f /var/log/nginx/error.log
sudo journalctl -u feedforward -f
```

## Post-Installation Tasks

### 1. Configure AI Models

1. Log in as admin
2. Navigate to Admin → AI Models
3. Add at least one AI provider
4. Test the connection

### 2. Set Up Email

1. Test email configuration:
   ```bash
   cd /opt/feedforward
   source venv/bin/activate
   python tools/test_email.py recipient@domain.edu
   ```

### 3. Configure Domains

1. Go to Admin → Domains
2. Add approved email domains
3. Set auto-approval if desired

### 4. Create First Instructor

1. Admin → Users → Create Instructor
2. Or allow registration from approved domain

### 5. Documentation

Document your installation:
- Server details
- Configuration choices
- API keys location
- Backup procedures
- Emergency contacts

## Troubleshooting Installation

### Common Issues

**Port Already in Use**
```bash
# Find process using port
sudo lsof -i :5001
# Kill if necessary
sudo kill -9 <PID>
```

**Permission Denied**
```bash
# Fix ownership
sudo chown -R feedforward:feedforward /opt/feedforward
```

**Module Import Errors**
```bash
# Ensure virtual environment activated
source /opt/feedforward/venv/bin/activate
# Reinstall requirements
pip install -r requirements.txt
```

**Database Locked**
```bash
# Ensure single process access
sudo systemctl stop feedforward
# Check database integrity
sqlite3 data/feedforward.db "PRAGMA integrity_check;"
```

## Maintenance Mode

To take the system offline for maintenance:

```bash
# Create maintenance page
sudo nano /usr/share/nginx/html/maintenance.html

# Update Nginx configuration to serve maintenance page
# Add to server block:
location / {
    return 503;
}
error_page 503 @maintenance;
location @maintenance {
    root /usr/share/nginx/html;
    rewrite ^(.*)$ /maintenance.html break;
}

# Reload Nginx
sudo systemctl reload nginx
```

## Next Steps

1. Review [Configuration Guide](./configuration) for detailed options
2. Set up regular backups
3. Configure monitoring alerts
4. Plan disaster recovery procedures
5. Schedule security updates

---

{: .warning }
> Always test configuration changes in a staging environment before applying to production.

{: .tip }
> Keep detailed documentation of your specific installation for easier maintenance and troubleshooting.