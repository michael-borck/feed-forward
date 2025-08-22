# Docker Deployment Guide for FeedForward

## Overview
FeedForward can be deployed using Docker for consistent, reproducible deployments across different environments.

## Quick Start

### 1. Basic Deployment
```bash
# Clone the repository
git clone https://github.com/your-org/feedforward.git
cd feedforward

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Build and run with Docker Compose
docker-compose up -d
```

The application will be available at http://localhost:5001

### 2. Development Setup with Hot Reload
```bash
# Run in development mode with code mounting
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or use the convenience script
./scripts/dev.sh
```

### 3. Production Deployment with HTTPS
```bash
# Run with Caddy reverse proxy for automatic HTTPS
docker-compose --profile production up -d
```

## Configuration

### Environment Variables
Create a `.env` file with your configuration:

```env
# Application
APP_DOMAIN=https://feedforward.yourdomain.com
SECRET_KEY=your-secret-key-here

# Database (SQLite by default, path relative to container)
DATABASE_PATH=/app/data/users.db

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecurePassword123!

# LLM API Keys (optional - will use mock feedback if not provided)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# Local LLM (optional)
OLLAMA_API_BASE=http://ollama:11434
```

### Docker Compose Profiles

The setup includes different profiles for various deployment scenarios:

#### Default Profile
Basic FeedForward application:
```bash
docker-compose up
```

#### With Ollama (Local LLM)
Includes Ollama for local model inference:
```bash
docker-compose --profile with-ollama up
```

#### Production Profile
Includes Caddy for automatic HTTPS:
```bash
docker-compose --profile production up
```

## Deployment Scenarios

### 1. Single Server Deployment

For a simple single-server deployment:

```bash
# 1. Set up the server (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose

# 2. Clone the repository
git clone https://github.com/your-org/feedforward.git
cd feedforward

# 3. Configure environment
cp .env.example .env
nano .env  # Add your configuration

# 4. Start the application
docker-compose up -d

# 5. Check logs
docker-compose logs -f feedforward
```

### 2. Production with HTTPS (Using Caddy)

First, update the Caddyfile:

```caddyfile
# deploy/Caddyfile
feedforward.yourdomain.com {
    reverse_proxy feedforward:5001
    
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
    }
    
    log {
        output file /var/log/caddy/access.log
    }
}
```

Then deploy:

```bash
docker-compose --profile production up -d
```

### 3. Development Environment

For local development with hot reload:

```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Application available at http://localhost:5001
# Code changes will auto-reload
```

### 4. With Local LLM (Ollama)

To use local models instead of API-based services:

```bash
# Start with Ollama
docker-compose --profile with-ollama up -d

# Wait for Ollama to start, then pull a model
docker exec feedforward-ollama ollama pull llama3.2

# Configure in .env
OLLAMA_API_BASE=http://ollama:11434
```

## Data Management

### Backup Database
```bash
# Backup SQLite database
docker cp feedforward-app:/app/data/users.db ./backup/users_$(date +%Y%m%d).db

# Backup uploads
docker cp feedforward-app:/app/data/uploads ./backup/uploads_$(date +%Y%m%d)
```

### Restore Database
```bash
# Stop the application
docker-compose stop feedforward

# Restore database
docker cp ./backup/users_20240101.db feedforward-app:/app/data/users.db

# Restart
docker-compose start feedforward
```

### Volume Management
```bash
# List volumes
docker volume ls | grep feedforward

# Backup volume
docker run --rm -v feedforward_feedforward-logs:/data -v $(pwd):/backup \
    alpine tar czf /backup/logs_backup.tar.gz -C /data .

# Clean unused volumes
docker volume prune
```

## Monitoring

### View Logs
```bash
# Application logs
docker-compose logs -f feedforward

# Last 100 lines
docker-compose logs --tail=100 feedforward

# Ollama logs (if using)
docker-compose logs -f ollama
```

### Health Checks
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Manual health check
curl http://localhost:5001/
```

### Resource Usage
```bash
# View resource usage
docker stats feedforward-app

# Detailed inspection
docker inspect feedforward-app
```

## Scaling Considerations

### Resource Limits
Add resource limits to docker-compose.yml:

```yaml
services:
  feedforward:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Multiple Workers
For production, consider using Gunicorn:

```dockerfile
# In Dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs feedforward

# Check if port is in use
sudo lsof -i :5001

# Rebuild image
docker-compose build --no-cache
```

### Database Issues
```bash
# Access container shell
docker exec -it feedforward-app /bin/bash

# Check database
sqlite3 /app/data/users.db ".tables"

# Reinitialize database
docker exec feedforward-app python app/init_db.py
```

### Permission Issues
```bash
# Fix ownership
docker exec feedforward-app chown -R feedforward:feedforward /app/data

# Check permissions
docker exec feedforward-app ls -la /app/data
```

### Memory Issues
```bash
# Check memory usage
docker system df

# Clean up
docker system prune -a
```

## Security Best Practices

1. **Use Secrets Management**
   ```yaml
   # Use Docker secrets instead of environment variables
   secrets:
     api_keys:
       file: ./secrets/api_keys.txt
   ```

2. **Network Isolation**
   ```yaml
   # Create separate networks
   networks:
     frontend:
     backend:
       internal: true
   ```

3. **Read-Only Filesystem**
   ```yaml
   # Make container filesystem read-only
   read_only: true
   tmpfs:
     - /tmp
   ```

4. **Non-Root User**
   Already implemented - container runs as `feedforward` user

5. **Regular Updates**
   ```bash
   # Update base images regularly
   docker-compose pull
   docker-compose up -d
   ```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/feedforward
            git pull
            docker-compose build
            docker-compose up -d
```

## Maintenance

### Regular Tasks
```bash
# Weekly: Backup database
./scripts/backup.sh

# Monthly: Update dependencies
docker-compose build --pull

# Quarterly: Prune old data
docker exec feedforward-app python tools/cleanup_drafts.py
```

### Upgrade Process
```bash
# 1. Backup data
./scripts/backup.sh

# 2. Pull latest code
git pull

# 3. Rebuild images
docker-compose build

# 4. Restart with new version
docker-compose up -d

# 5. Verify
curl http://localhost:5001/
```

## Support

For issues specific to Docker deployment:
1. Check container logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure volumes have proper permissions
4. Check Docker daemon status: `systemctl status docker`

For application issues, refer to the main documentation.