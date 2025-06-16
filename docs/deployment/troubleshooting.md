---
layout: default
title: Troubleshooting Guide
parent: Deployment
nav_order: 4
---

# Troubleshooting Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This guide helps diagnose and resolve common issues with FeedForward deployments. Issues are organized by category with symptoms, causes, and solutions.

## Quick Diagnostics

### System Health Check

Run the comprehensive health check:

```bash
cd /opt/feedforward
source venv/bin/activate
python tools/health_check.py
```

This checks:
- Database connectivity
- File permissions
- Service status
- API connections
- Configuration validity

### Common Commands

```bash
# Check service status
sudo systemctl status feedforward

# View recent logs
sudo journalctl -u feedforward -n 100

# Test database connection
sqlite3 data/feedforward.db "SELECT COUNT(*) FROM users;"

# Verify permissions
ls -la /opt/feedforward/
```

## Installation Issues

### Python Version Errors

**Symptom**: `ModuleNotFoundError` or syntax errors during installation

**Cause**: Wrong Python version

**Solution**:
```bash
# Check Python version
python3 --version

# Install correct version (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv

# Use specific version
python3.10 -m venv venv
```

### Dependency Installation Failures

**Symptom**: `pip install` fails with compilation errors

**Cause**: Missing system dependencies

**Solution**:
```bash
# Install build dependencies (Ubuntu/Debian)
sudo apt install -y build-essential python3-dev libssl-dev libffi-dev

# For PDF processing
sudo apt install -y libpoppler-cpp-dev

# Retry installation
pip install --upgrade pip
pip install -r requirements.txt
```

### Permission Denied Errors

**Symptom**: Cannot create files or directories

**Cause**: Incorrect ownership or permissions

**Solution**:
```bash
# Fix ownership
sudo chown -R feedforward:feedforward /opt/feedforward

# Fix permissions
sudo chmod -R 755 /opt/feedforward
sudo chmod -R 775 /opt/feedforward/data
sudo chmod -R 775 /opt/feedforward/logs
```

## Database Issues

### Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Cause**: Multiple processes accessing database or stuck transaction

**Solution**:
```bash
# Stop all services
sudo systemctl stop feedforward

# Check for stuck processes
ps aux | grep feedforward
# Kill if necessary
kill -9 <PID>

# Check database integrity
sqlite3 data/feedforward.db "PRAGMA integrity_check;"

# Restart service
sudo systemctl start feedforward
```

### Database Corruption

**Symptom**: `sqlite3.DatabaseError: database disk image is malformed`

**Cause**: Improper shutdown or disk issues

**Solution**:
```bash
# Stop service
sudo systemctl stop feedforward

# Attempt recovery
sqlite3 data/feedforward.db ".recover" | sqlite3 data/feedforward_recovered.db

# If successful, replace
mv data/feedforward.db data/feedforward_corrupt.db
mv data/feedforward_recovered.db data/feedforward.db

# Restore from backup if recovery fails
cp data/backups/feedforward_latest.db data/feedforward.db

# Restart service
sudo systemctl start feedforward
```

### Migration Errors

**Symptom**: Database schema mismatch

**Cause**: Incomplete migrations

**Solution**:
```bash
# Check migration status
python tools/check_migrations.py

# Force migration
python app/init_db.py --force

# If errors persist, backup and recreate
cp data/feedforward.db data/feedforward_backup.db
python app/init_db.py --clean
```

## Authentication Issues

### Cannot Log In

**Symptom**: Valid credentials rejected

**Cause**: Various authentication issues

**Solution**:
```bash
# Check user exists
sqlite3 data/feedforward.db "SELECT email, active FROM users WHERE email='user@example.com';"

# Reset password
python tools/reset_password.py user@example.com

# Check session configuration
grep SESSION .env

# Clear sessions
sqlite3 data/feedforward.db "DELETE FROM sessions;"
```

### Session Expires Too Quickly

**Symptom**: Users logged out frequently

**Cause**: Session timeout too short

**Solution**:
```env
# Increase session lifetime in .env
SESSION_LIFETIME=86400  # 24 hours

# Restart service
sudo systemctl restart feedforward
```

### Password Reset Not Working

**Symptom**: Password reset emails not sent or links invalid

**Cause**: Email configuration or URL issues

**Solution**:
```bash
# Test email configuration
python tools/test_email.py test@example.com

# Check APP_DOMAIN setting
grep APP_DOMAIN .env
# Should match actual domain

# Verify SMTP settings
python tools/validate_config.py --test-email
```

## Email Issues

### Emails Not Sending

**Symptom**: No emails received

**Cause**: SMTP configuration error

**Solution**:
```bash
# Test SMTP connection
python tools/test_smtp.py

# Common fixes:
# 1. Check credentials
grep SMTP .env

# 2. Try different ports
SMTP_PORT=587  # TLS
SMTP_PORT=465  # SSL
SMTP_PORT=25   # Plain (not recommended)

# 3. Enable/disable TLS/SSL
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# 4. Check firewall
sudo ufw status
sudo ufw allow 587/tcp
```

### Gmail SMTP Issues

**Symptom**: Authentication failed with Gmail

**Cause**: Security restrictions

**Solution**:
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password in configuration:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
```

## AI Provider Issues

### API Key Invalid

**Symptom**: AI generation fails with authentication error

**Cause**: Invalid or expired API key

**Solution**:
```bash
# Validate API keys
python tools/test_ai_providers.py

# Check key format
# OpenAI: starts with 'sk-'
# Anthropic: starts with 'sk-ant-'

# Verify in provider console:
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/
```

### Rate Limiting

**Symptom**: Intermittent AI failures

**Cause**: Exceeding API rate limits

**Solution**:
```python
# Implement rate limiting
# In .env:
AI_REQUESTS_PER_MINUTE=20
AI_RETRY_DELAY=60

# Use multiple models
# Configure fallback models in admin panel
```

### Timeout Errors

**Symptom**: AI requests timeout

**Cause**: Slow response or network issues

**Solution**:
```env
# Increase timeout in .env
AI_TIMEOUT=600  # 10 minutes

# For specific providers
OPENAI_TIMEOUT=300
ANTHROPIC_TIMEOUT=600
```

### Ollama Connection Failed

**Symptom**: Cannot connect to local Ollama

**Cause**: Ollama not running or misconfigured

**Solution**:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull required model
ollama pull llama2

# Update configuration
OLLAMA_BASE_URL=http://localhost:11434
```

## Performance Issues

### Slow Page Load

**Symptom**: Pages take long to load

**Cause**: Various performance bottlenecks

**Solution**:
```bash
# 1. Check database performance
sqlite3 data/feedforward.db "PRAGMA optimize;"
sqlite3 data/feedforward.db "ANALYZE;"

# 2. Enable caching
ENABLE_CACHE=true
CACHE_TTL=3600

# 3. Increase workers
WORKER_PROCESSES=8
WORKER_THREADS=2

# 4. Check disk space
df -h /opt/feedforward

# 5. Monitor resources
htop
iotop
```

### High Memory Usage

**Symptom**: Application using excessive RAM

**Cause**: Memory leaks or configuration

**Solution**:
```bash
# Limit worker memory
# In systemd service:
MemoryLimit=2G

# Reduce worker count
WORKER_PROCESSES=4

# Enable memory profiling
python tools/memory_profile.py
```

### Database Slow

**Symptom**: Queries taking too long

**Cause**: Missing indexes or large database

**Solution**:
```bash
# Optimize database
python tools/optimize_database.py

# Add missing indexes
sqlite3 data/feedforward.db < tools/sql/add_indexes.sql

# Vacuum database
sqlite3 data/feedforward.db "VACUUM;"

# Consider PostgreSQL migration for large deployments
```

## File Upload Issues

### Upload Fails

**Symptom**: File uploads rejected

**Cause**: Size limits or file type restrictions

**Solution**:
```env
# Increase size limits in .env
MAX_UPLOAD_SIZE_MB=25
MAX_CONTENT_LENGTH=26214400

# Allow more file types
ALLOWED_EXTENSIONS=txt,pdf,docx,doc,rtf,odt

# Check Nginx limits
# In nginx.conf:
client_max_body_size 25M;
```

### PDF Extraction Errors

**Symptom**: Cannot extract text from PDFs

**Cause**: Missing dependencies or corrupted PDFs

**Solution**:
```bash
# Install poppler
sudo apt install poppler-utils

# Test extraction
python -c "from app.utils.file_handlers import extract_pdf_content; print(extract_pdf_content(open('test.pdf', 'rb').read()))"

# Handle corrupted PDFs
# Add error handling in code
```

## Security Issues

### SSL Certificate Errors

**Symptom**: Browser shows security warning

**Cause**: Invalid or expired certificate

**Solution**:
```bash
# Check certificate
openssl x509 -in /etc/ssl/certs/feedforward.crt -text -noout

# Renew Let's Encrypt
sudo certbot renew

# Test configuration
sudo nginx -t
sudo systemctl reload nginx
```

### CSRF Token Errors

**Symptom**: Form submissions fail with CSRF error

**Cause**: Misconfigured security settings

**Solution**:
```env
# Ensure in .env:
SECRET_KEY=your-secure-key
SESSION_COOKIE_SECURE=true  # Only with HTTPS
SESSION_COOKIE_HTTPONLY=true

# Clear browser cookies
# Restart application
```

## Deployment Issues

### Service Won't Start

**Symptom**: `systemctl start feedforward` fails

**Cause**: Configuration or dependency issues

**Solution**:
```bash
# Check service logs
sudo journalctl -u feedforward -n 50

# Test manual start
cd /opt/feedforward
source venv/bin/activate
python app.py

# Common fixes:
# 1. Fix Python path in service file
# 2. Ensure all dependencies installed
# 3. Check file permissions
# 4. Verify .env file exists
```

### Port Already in Use

**Symptom**: `Address already in use` error

**Cause**: Another process using the port

**Solution**:
```bash
# Find process using port
sudo lsof -i :5001

# Kill process
sudo kill -9 <PID>

# Or change port in .env
APP_PORT=5002
```

## Data Issues

### Lost Student Work

**Symptom**: Student submissions disappear

**Cause**: Privacy cleanup running too frequently

**Solution**:
```env
# Increase retention in .env
DRAFT_RETENTION_HOURS=72  # 3 days instead of 24 hours

# Disable automatic cleanup temporarily
# Comment out in crontab:
# 0 * * * * cd /opt/feedforward && python tools/cleanup_drafts.py

# Recover from backup if needed
python tools/restore_backup.py --date yesterday
```

### Feedback Not Generating

**Symptom**: Feedback stays in "processing" state

**Cause**: Background worker issues

**Solution**:
```bash
# Check background tasks
ps aux | grep feedforward

# Restart workers
sudo systemctl restart feedforward

# Check task queue
sqlite3 data/feedforward.db "SELECT * FROM background_tasks WHERE status='pending';"

# Process manually if needed
python tools/process_pending_feedback.py
```

## Monitoring and Logs

### Finding Log Files

```bash
# Application logs
/opt/feedforward/logs/feedforward.log
/opt/feedforward/logs/gunicorn-error.log
/opt/feedforward/logs/gunicorn-access.log

# System logs
/var/log/nginx/error.log
/var/log/nginx/access.log
sudo journalctl -u feedforward

# Database logs
/opt/feedforward/logs/database.log
```

### Enabling Debug Mode

**For development only**:
```env
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
SQL_LOG_LEVEL=DEBUG

# Restart service
sudo systemctl restart feedforward
```

{: .danger }
> Never enable DEBUG in production. It exposes sensitive information.

### Log Analysis

```bash
# Common error patterns
grep ERROR /opt/feedforward/logs/feedforward.log | tail -50

# Failed login attempts
grep "Failed login" /opt/feedforward/logs/feedforward.log

# AI API errors
grep -E "(OpenAI|Anthropic|API)" /opt/feedforward/logs/feedforward.log

# Performance issues
grep "Slow query" /opt/feedforward/logs/database.log
```

## Getting Help

### Gathering Diagnostic Information

When reporting issues, include:

```bash
# System information
python tools/diagnostic_report.py > diagnostic_report.txt

# This includes:
# - System details
# - Configuration (sanitized)
# - Recent errors
# - Database statistics
# - Service status
```

### Support Channels

1. **GitHub Issues**: https://github.com/michael-borck/feed-forward/issues
2. **Documentation**: https://michael-borck.github.io/feed-forward/
3. **Community Forum**: [If applicable]
4. **Email Support**: [If applicable]

### Emergency Procedures

**Complete System Down**:
1. Check server accessibility
2. Verify disk space: `df -h`
3. Check system resources: `free -h`
4. Review system logs: `dmesg | tail`
5. Restart services: `sudo systemctl restart feedforward nginx`
6. Restore from backup if needed

**Data Recovery**:
1. Stop all services
2. Backup current state
3. Restore from latest good backup
4. Verify data integrity
5. Test functionality
6. Resume services

---

{: .tip }
> Keep this guide handy and update it with solutions to new issues you encounter.

{: .note }
> Most issues can be resolved by checking logs, verifying configuration, and ensuring all dependencies are properly installed.