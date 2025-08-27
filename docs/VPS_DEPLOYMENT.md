# VPS Deployment Guide

This guide covers deploying FeedForward on a VPS (Ubuntu/Debian) with Docker.

## Prerequisites

- Ubuntu/Debian VPS with Docker installed
- Domain name pointing to your VPS
- Reverse proxy (Caddy, nginx, etc.) already configured

## Deployment Steps

### 1. Clone the Repository

```bash
ssh your-vps
git clone https://github.com/your-repo/feed-forward.git
cd feed-forward
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

Essential configurations:
- `APP_DOMAIN`: Your domain (e.g., `https://feedforward.yourdomain.com`)
- `SECRET_KEY`: Generate a secure key with `openssl rand -hex 32`
- `SMTP_*`: Email server settings
- `ADMIN_EMAIL` and `ADMIN_PASSWORD`: Initial admin account
- At least one LLM API key (OpenAI, Anthropic, etc.)

### 3. Start the Application

```bash
# Start the container
docker-compose up -d

# Verify it's running
docker-compose ps
docker-compose logs feedforward
```

The app will be available on port 5001.

### 4. Configure Your Reverse Proxy

#### For Caddy
Add to your Caddyfile:
```
feedforward.yourdomain.com {
    reverse_proxy localhost:5001
}
```

#### For nginx
```nginx
server {
    server_name feedforward.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Enable Automatic Restart

The container already has `restart: unless-stopped`, which means it will:
- Automatically restart if it crashes
- Start automatically when Docker starts
- Stay stopped if you manually stop it

To ensure Docker starts on boot:
```bash
sudo systemctl enable docker
```

## Management Commands

### View Logs
```bash
docker-compose logs -f feedforward
```

### Stop/Start/Restart
```bash
docker-compose stop
docker-compose start
docker-compose restart
```

### Update Application
```bash
git pull
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
# Create backup directory
mkdir -p ~/backups

# Backup database
docker cp feedforward-app:/app/data/users.db ~/backups/users_$(date +%Y%m%d).db

# Backup uploads
docker cp feedforward-app:/app/data/uploads ~/backups/uploads_$(date +%Y%m%d)
```

### Access Container Shell
```bash
docker exec -it feedforward-app /bin/bash
```

## Using Local LLM (Optional)

To use Ollama for local inference instead of API-based services:

```bash
# Start with Ollama profile
docker-compose --profile with-ollama up -d

# Pull a model
docker exec feedforward-ollama ollama pull llama3.2

# Update .env
echo "OLLAMA_API_BASE=http://ollama:11434" >> .env

# Restart app to use Ollama
docker-compose restart feedforward
```

## Monitoring

### Check Container Health
```bash
# Quick status
docker ps | grep feedforward

# Detailed health
docker inspect feedforward-app --format='{{.State.Health.Status}}'

# Resource usage
docker stats feedforward-app
```

### Application Health Check
```bash
curl -f http://localhost:5001/ || echo "Health check failed"
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs for errors
docker-compose logs feedforward

# Verify port isn't in use
sudo lsof -i :5001

# Check disk space
df -h
```

### Permission Issues
```bash
# The container runs as non-root user 'feedforward'
# Fix data directory permissions if needed
docker exec feedforward-app chown -R feedforward:feedforward /app/data
```

### Database Issues
```bash
# Reinitialize database (WARNING: resets all data)
docker exec feedforward-app python app/init_db.py
```

### Memory Issues
```bash
# Check memory usage
docker system df
free -h

# Clean up unused Docker resources
docker system prune -a
```

## Security Notes

1. Always use HTTPS (configure in your reverse proxy)
2. Keep your `.env` file secure with proper permissions: `chmod 600 .env`
3. Regularly update the base image: `docker-compose pull && docker-compose up -d`
4. Consider using Docker secrets for sensitive data in production
5. Set up firewall rules to only expose necessary ports

## Quick Reference

```bash
# One-line deployment (after configuration)
docker-compose up -d

# One-line update
git pull && docker-compose build && docker-compose up -d

# View recent logs
docker-compose logs --tail=50 -f feedforward

# Emergency stop
docker-compose down
```