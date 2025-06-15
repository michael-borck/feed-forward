---
layout: default
title: Configuration
parent: Getting Started
nav_order: 2
---

# Configuration Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward uses environment variables for configuration, allowing easy deployment across different environments. All configuration is stored in a `.env` file in the project root.

## Essential Configuration

### Security Settings

```env
# REQUIRED: Generate a strong secret key for session encryption
SECRET_KEY=your-very-long-random-secret-key-here

# Optional: Set to true only for development
DEBUG=false
```

{: .warning }
> **Important**: Generate a cryptographically secure SECRET_KEY. You can use Python to generate one:
> ```python
> import secrets
> print(secrets.token_urlsafe(32))
> ```

### Application Settings

```env
# Application base URL (update for production)
APP_DOMAIN=http://localhost:5001

# Application name (shown in UI and emails)
APP_NAME=FeedForward

# Server port (default: 5001)
PORT=5001

# Database location (relative to project root)
DATABASE_PATH=data/feedforward.db
```

### Email Configuration

Email settings are required for sending course invitations to students:

```env
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com        # Your SMTP server
SMTP_PORT=587                     # Usually 587 for TLS, 465 for SSL
SMTP_USER=your-email@gmail.com    # SMTP username
SMTP_PASSWORD=your-app-password   # SMTP password or app password
SMTP_FROM=noreply@yourdomain.com # From address for emails

# Optional: Email security
SMTP_USE_TLS=true                 # Use TLS (recommended)
SMTP_USE_SSL=false                # Use SSL (alternative to TLS)
```

{: .tip }
> **Gmail Users**: Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## AI Provider Configuration

FeedForward supports multiple AI providers through LiteLLM. Configure the providers you plan to use:

### OpenAI

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-...your-key-here
OPENAI_API_BASE=https://api.openai.com/v1  # Optional: for Azure or proxies
OPENAI_API_VERSION=2024-02-15-preview      # Optional: for Azure
```

### Anthropic (Claude)

```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

### Google (Gemini/PaLM)

```env
# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-key
# OR for Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Ollama (Local Models)

```env
# Ollama Configuration (for local models)
OLLAMA_API_BASE=http://localhost:11434
```

### Other Providers

```env
# Cohere
COHERE_API_KEY=your-cohere-key

# Hugging Face
HUGGINGFACE_API_KEY=your-hf-key

# Replicate
REPLICATE_API_KEY=your-replicate-key
```

## Advanced Configuration

### Privacy Settings

```env
# Draft content retention (hours before cleanup, 0 = immediate)
DRAFT_RETENTION_HOURS=24

# Enable automatic cleanup scheduler
ENABLE_AUTO_CLEANUP=true
CLEANUP_SCHEDULE="0 2 * * *"  # Cron format: 2 AM daily
```

### Performance Tuning

```env
# Worker configuration
WORKERS=4                    # Number of worker processes
WORKER_TIMEOUT=120          # Worker timeout in seconds

# Database settings
DATABASE_POOL_SIZE=10       # Connection pool size
DATABASE_POOL_TIMEOUT=30    # Pool timeout in seconds

# File upload limits
MAX_UPLOAD_SIZE_MB=10       # Maximum file upload size
ALLOWED_EXTENSIONS=txt,pdf,docx
```

### Logging Configuration

```env
# Logging settings
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/feedforward.log
LOG_FORMAT=json             # json or text
LOG_ROTATION=daily          # daily, size, or time
LOG_RETENTION_DAYS=30       # Keep logs for 30 days
```

### Session Configuration

```env
# Session settings
SESSION_LIFETIME=86400      # Session lifetime in seconds (24 hours)
SESSION_COOKIE_SECURE=true  # Require HTTPS for cookies (production)
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
```

## Environment-Specific Configurations

### Development Environment

Create `.env.development`:

```env
DEBUG=true
APP_DOMAIN=http://localhost:5001
SESSION_COOKIE_SECURE=false
LOG_LEVEL=DEBUG
```

### Production Environment

Create `.env.production`:

```env
DEBUG=false
APP_DOMAIN=https://feedforward.yourdomain.com
SESSION_COOKIE_SECURE=true
LOG_LEVEL=WARNING
WORKERS=8
```

### Testing Environment

Create `.env.test`:

```env
DEBUG=true
DATABASE_PATH=data/test.db
SMTP_SERVER=localhost
SMTP_PORT=1025  # For MailHog or similar
```

## Configuration Best Practices

### 1. Security First

- Never commit `.env` files to version control
- Use strong, unique secret keys
- Rotate API keys regularly
- Use environment-specific configurations

### 2. API Key Management

- Store API keys securely
- Use separate keys for development/production
- Monitor API usage and costs
- Set up usage alerts with providers

### 3. Email Configuration

- Use app-specific passwords
- Test email configuration before production
- Consider using transactional email services
- Monitor bounce rates and delivery

### 4. Performance Optimization

- Adjust worker counts based on server capacity
- Monitor database connection pool usage
- Set appropriate timeouts
- Enable caching where appropriate

## Validating Configuration

After setting up your configuration, validate it:

```bash
# Check configuration
python tools/check_config.py

# Test email configuration
python tools/test_email.py recipient@example.com

# Test AI provider connections
python tools/test_ai_providers.py
```

## Troubleshooting Configuration

### Common Issues

**Missing environment variables:**
```
Error: SECRET_KEY not found in environment
Solution: Ensure .env file is in project root and properly formatted
```

**Invalid SMTP settings:**
```
Error: Failed to send email
Solution: Verify SMTP credentials and server settings
```

**API key errors:**
```
Error: Invalid API key for OpenAI
Solution: Check key format and ensure it's active
```

**Database connection issues:**
```
Error: Unable to open database file
Solution: Ensure data directory exists and has write permissions
```

## Configuration Reference

For a complete list of all configuration options, see the [Configuration Reference](/deployment/configuration) in the deployment documentation.

## Next Steps

- Continue to [Quick Start](./quick-start) to create your first assignment
- Review [AI Integration](/technical/ai-integration) for model configuration details
- See [Security Best Practices](/deployment/security) for production deployments

---

{: .note }
> Configuration changes require restarting the application to take effect.