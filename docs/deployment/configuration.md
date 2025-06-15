---
layout: default
title: Configuration Guide
parent: Deployment
nav_order: 3
---

# Configuration Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward uses environment variables for configuration, allowing flexible deployment across different environments. This guide details all available configuration options, their purposes, and recommended settings.

## Configuration File

### Environment File Location

FeedForward looks for configuration in the following order:

1. System environment variables
2. `.env` file in the project root
3. Default values in code

### Creating Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

### Configuration Format

```env
# Comments start with #
KEY=value

# Multi-line values use quotes
LONG_VALUE="Line 1
Line 2
Line 3"

# Booleans: true/false, yes/no, 1/0
DEBUG=false

# Lists use comma separation
ALLOWED_HOSTS=localhost,feedforward.edu,www.feedforward.edu
```

## Core Configuration

### Security Settings

#### SECRET_KEY
- **Required**: Yes
- **Type**: String
- **Description**: Secret key for session encryption and CSRF protection
- **Example**: `SECRET_KEY=your-very-long-random-secret-key-here`
- **Generation**:
  ```python
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

{: .warning }
> Never use the default secret key in production. Always generate a new one.

#### DEBUG
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable debug mode (development only)
- **Example**: `DEBUG=false`
- **Values**: `true`, `false`

{: .danger }
> Never enable DEBUG in production. It exposes sensitive information.

#### ALLOWED_HOSTS
- **Required**: No
- **Type**: Comma-separated list
- **Default**: `localhost,127.0.0.1`
- **Description**: Allowed host headers for security
- **Example**: `ALLOWED_HOSTS=feedforward.edu,www.feedforward.edu`

### Application Settings

#### APP_NAME
- **Required**: No
- **Type**: String
- **Default**: `FeedForward`
- **Description**: Application name shown in UI
- **Example**: `APP_NAME=University Writing Center`

#### APP_DOMAIN
- **Required**: Yes (production)
- **Type**: URL
- **Description**: Full application URL
- **Example**: `APP_DOMAIN=https://feedforward.university.edu`

#### APP_DESCRIPTION
- **Required**: No
- **Type**: String
- **Default**: `AI-assisted feedback platform`
- **Description**: Application description for metadata
- **Example**: `APP_DESCRIPTION=Writing feedback system for students`

#### SESSION_LIFETIME
- **Required**: No
- **Type**: Integer (seconds)
- **Default**: `86400` (24 hours)
- **Description**: User session duration
- **Example**: `SESSION_LIFETIME=43200` (12 hours)

#### SESSION_COOKIE_SECURE
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Require HTTPS for session cookies
- **Example**: `SESSION_COOKIE_SECURE=true`

#### SESSION_COOKIE_HTTPONLY
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Prevent JavaScript access to session cookies
- **Example**: `SESSION_COOKIE_HTTPONLY=true`

## Database Configuration

### SQLite Settings (Default)

#### DATABASE_PATH
- **Required**: No
- **Type**: File path
- **Default**: `data/feedforward.db`
- **Description**: Path to SQLite database file
- **Example**: `DATABASE_PATH=/var/lib/feedforward/data.db`

#### DATABASE_BACKUP_PATH
- **Required**: No
- **Type**: Directory path
- **Default**: `data/backups`
- **Description**: Directory for database backups
- **Example**: `DATABASE_BACKUP_PATH=/backup/feedforward`

#### DATABASE_JOURNAL_MODE
- **Required**: No
- **Type**: String
- **Default**: `WAL`
- **Description**: SQLite journal mode
- **Example**: `DATABASE_JOURNAL_MODE=WAL`
- **Options**: `DELETE`, `TRUNCATE`, `PERSIST`, `MEMORY`, `WAL`, `OFF`

### PostgreSQL Settings (Future)

```env
# PostgreSQL configuration (when supported)
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=feedforward
DATABASE_USER=feedforward_user
DATABASE_PASSWORD=secure_password
DATABASE_SSL_MODE=require
```

## Email Configuration

### SMTP Settings

#### SMTP_SERVER
- **Required**: Yes (if email enabled)
- **Type**: String
- **Description**: SMTP server hostname
- **Example**: `SMTP_SERVER=smtp.university.edu`

#### SMTP_PORT
- **Required**: No
- **Type**: Integer
- **Default**: `587`
- **Description**: SMTP server port
- **Example**: `SMTP_PORT=587`
- **Common Values**: `25`, `465`, `587`, `2525`

#### SMTP_USER
- **Required**: Yes (if auth required)
- **Type**: String
- **Description**: SMTP authentication username
- **Example**: `SMTP_USER=feedforward@university.edu`

#### SMTP_PASSWORD
- **Required**: Yes (if auth required)
- **Type**: String
- **Description**: SMTP authentication password
- **Example**: `SMTP_PASSWORD=secure_smtp_password`

#### SMTP_FROM
- **Required**: No
- **Type**: Email address
- **Default**: Value of SMTP_USER
- **Description**: Default sender address
- **Example**: `SMTP_FROM=noreply@university.edu`

#### SMTP_USE_TLS
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Use STARTTLS encryption
- **Example**: `SMTP_USE_TLS=true`

#### SMTP_USE_SSL
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Use SSL/TLS encryption
- **Example**: `SMTP_USE_SSL=false`

### Email Templates

#### EMAIL_SUBJECT_PREFIX
- **Required**: No
- **Type**: String
- **Default**: `[FeedForward]`
- **Description**: Prefix for email subjects
- **Example**: `EMAIL_SUBJECT_PREFIX=[Writing Center]`

#### EMAIL_FOOTER_TEXT
- **Required**: No
- **Type**: String
- **Default**: System default
- **Description**: Footer text for emails
- **Example**: `EMAIL_FOOTER_TEXT=University Writing Center - Do not reply`

## AI Provider Configuration

### Multiple Provider Support

FeedForward supports multiple AI providers. Configure at least one:

### OpenAI

#### OPENAI_API_KEY
- **Required**: Conditional
- **Type**: String
- **Description**: OpenAI API key
- **Example**: `OPENAI_API_KEY=sk-...`
- **Obtain**: https://platform.openai.com/api-keys

#### OPENAI_ORG_ID
- **Required**: No
- **Type**: String
- **Description**: OpenAI organization ID
- **Example**: `OPENAI_ORG_ID=org-...`

#### OPENAI_API_BASE
- **Required**: No
- **Type**: URL
- **Default**: `https://api.openai.com/v1`
- **Description**: Custom API endpoint
- **Example**: `OPENAI_API_BASE=https://api.openai.com/v1`

### Anthropic (Claude)

#### ANTHROPIC_API_KEY
- **Required**: Conditional
- **Type**: String
- **Description**: Anthropic API key
- **Example**: `ANTHROPIC_API_KEY=sk-ant-...`
- **Obtain**: https://console.anthropic.com/

#### ANTHROPIC_API_BASE
- **Required**: No
- **Type**: URL
- **Default**: `https://api.anthropic.com`
- **Description**: Custom API endpoint
- **Example**: `ANTHROPIC_API_BASE=https://api.anthropic.com`

### Google AI

#### GOOGLE_API_KEY
- **Required**: Conditional
- **Type**: String
- **Description**: Google AI API key
- **Example**: `GOOGLE_API_KEY=...`
- **Obtain**: https://makersuite.google.com/app/apikey

#### GOOGLE_APPLICATION_CREDENTIALS
- **Required**: No
- **Type**: File path
- **Description**: Path to service account JSON
- **Example**: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`

### Ollama (Local)

#### OLLAMA_BASE_URL
- **Required**: Conditional
- **Type**: URL
- **Default**: `http://localhost:11434`
- **Description**: Ollama server URL
- **Example**: `OLLAMA_BASE_URL=http://localhost:11434`

#### OLLAMA_API_KEY
- **Required**: No
- **Type**: String
- **Default**: `ollama`
- **Description**: Ollama API key (if configured)
- **Example**: `OLLAMA_API_KEY=custom_key`

### AI Configuration Options

#### DEFAULT_AI_MODEL
- **Required**: No
- **Type**: String
- **Default**: First available model
- **Description**: Default model for new assignments
- **Example**: `DEFAULT_AI_MODEL=gpt-4`

#### AI_TIMEOUT
- **Required**: No
- **Type**: Integer (seconds)
- **Default**: `300`
- **Description**: AI API request timeout
- **Example**: `AI_TIMEOUT=600`

#### AI_MAX_RETRIES
- **Required**: No
- **Type**: Integer
- **Default**: `3`
- **Description**: Maximum retry attempts
- **Example**: `AI_MAX_RETRIES=5`

#### AI_TEMPERATURE_DEFAULT
- **Required**: No
- **Type**: Float (0.0-2.0)
- **Default**: `0.7`
- **Description**: Default temperature setting
- **Example**: `AI_TEMPERATURE_DEFAULT=0.5`

## Privacy & Data Settings

### Data Retention

#### DRAFT_RETENTION_HOURS
- **Required**: No
- **Type**: Integer
- **Default**: `24`
- **Description**: Hours to retain draft content
- **Example**: `DRAFT_RETENTION_HOURS=48`

#### FEEDBACK_RETENTION_DAYS
- **Required**: No
- **Type**: Integer
- **Default**: `0` (indefinite)
- **Description**: Days to retain feedback
- **Example**: `FEEDBACK_RETENTION_DAYS=365`

#### LOG_RETENTION_DAYS
- **Required**: No
- **Type**: Integer
- **Default**: `30`
- **Description**: Days to retain logs
- **Example**: `LOG_RETENTION_DAYS=90`

### Privacy Features

#### ENABLE_ANALYTICS
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable usage analytics
- **Example**: `ENABLE_ANALYTICS=false`

#### ANONYMIZE_SUBMISSIONS
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Remove identifying info from AI calls
- **Example**: `ANONYMIZE_SUBMISSIONS=true`

#### ALLOW_DATA_EXPORT
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Allow users to export their data
- **Example**: `ALLOW_DATA_EXPORT=true`

## File Upload Settings

### Size Limits

#### MAX_UPLOAD_SIZE_MB
- **Required**: No
- **Type**: Integer
- **Default**: `10`
- **Description**: Maximum file size in MB
- **Example**: `MAX_UPLOAD_SIZE_MB=25`

#### MAX_CONTENT_LENGTH
- **Required**: No
- **Type**: Integer (bytes)
- **Default**: `10485760` (10MB)
- **Description**: Maximum request size
- **Example**: `MAX_CONTENT_LENGTH=26214400`

### File Types

#### ALLOWED_EXTENSIONS
- **Required**: No
- **Type**: Comma-separated list
- **Default**: `txt,pdf,docx`
- **Description**: Allowed file extensions
- **Example**: `ALLOWED_EXTENSIONS=txt,pdf,docx,doc,rtf`

#### SCAN_UPLOADS
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Scan uploads for malware
- **Example**: `SCAN_UPLOADS=true`

## Performance Settings

### Worker Configuration

#### WORKER_PROCESSES
- **Required**: No
- **Type**: Integer
- **Default**: CPU count
- **Description**: Number of worker processes
- **Example**: `WORKER_PROCESSES=4`

#### WORKER_THREADS
- **Required**: No
- **Type**: Integer
- **Default**: `1`
- **Description**: Threads per worker
- **Example**: `WORKER_THREADS=2`

#### WORKER_TIMEOUT
- **Required**: No
- **Type**: Integer (seconds)
- **Default**: `300`
- **Description**: Worker request timeout
- **Example**: `WORKER_TIMEOUT=600`

### Caching

#### ENABLE_CACHE
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable response caching
- **Example**: `ENABLE_CACHE=true`

#### CACHE_TTL
- **Required**: No
- **Type**: Integer (seconds)
- **Default**: `3600`
- **Description**: Cache time-to-live
- **Example**: `CACHE_TTL=7200`

## Logging Configuration

### Log Levels

#### LOG_LEVEL
- **Required**: No
- **Type**: String
- **Default**: `INFO`
- **Description**: Application log level
- **Example**: `LOG_LEVEL=WARNING`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

#### SQL_LOG_LEVEL
- **Required**: No
- **Type**: String
- **Default**: `WARNING`
- **Description**: Database query logging
- **Example**: `SQL_LOG_LEVEL=DEBUG`

### Log Outputs

#### LOG_FILE
- **Required**: No
- **Type**: File path
- **Default**: `logs/feedforward.log`
- **Description**: Log file location
- **Example**: `LOG_FILE=/var/log/feedforward/app.log`

#### LOG_FORMAT
- **Required**: No
- **Type**: String
- **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Description**: Log message format
- **Example**: `LOG_FORMAT=%(asctime)s [%(levelname)s] %(message)s`

#### LOG_TO_CONSOLE
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Also log to console
- **Example**: `LOG_TO_CONSOLE=false`

## Feature Flags

### Optional Features

#### ENABLE_REGISTRATION
- **Required**: No
- **Type**: Boolean
- **Default**: `true`
- **Description**: Allow new user registration
- **Example**: `ENABLE_REGISTRATION=false`

#### ENABLE_OAUTH
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable OAuth authentication
- **Example**: `ENABLE_OAUTH=true`

#### ENABLE_API
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable REST API endpoints
- **Example**: `ENABLE_API=true`

#### ENABLE_WEBHOOKS
- **Required**: No
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable webhook notifications
- **Example**: `ENABLE_WEBHOOKS=true`

## Integration Settings

### LMS Integration

#### LMS_TYPE
- **Required**: No
- **Type**: String
- **Description**: LMS platform type
- **Example**: `LMS_TYPE=canvas`
- **Options**: `canvas`, `moodle`, `blackboard`

#### LMS_API_URL
- **Required**: No
- **Type**: URL
- **Description**: LMS API endpoint
- **Example**: `LMS_API_URL=https://canvas.university.edu/api/v1`

#### LMS_API_KEY
- **Required**: No
- **Type**: String
- **Description**: LMS API authentication
- **Example**: `LMS_API_KEY=...`

### External Services

#### SENTRY_DSN
- **Required**: No
- **Type**: String
- **Description**: Sentry error tracking DSN
- **Example**: `SENTRY_DSN=https://...@sentry.io/...`

#### ANALYTICS_ID
- **Required**: No
- **Type**: String
- **Description**: Analytics tracking ID
- **Example**: `ANALYTICS_ID=UA-123456789-1`

## Environment-Specific Configurations

### Development Environment

```env
# Development settings
DEBUG=true
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_PATH=data/dev.db
LOG_LEVEL=DEBUG
EMAIL_BACKEND=console  # Print emails to console
AI_TIMEOUT=60  # Faster timeout for testing
```

### Staging Environment

```env
# Staging settings
DEBUG=false
SECRET_KEY=${STAGING_SECRET_KEY}
ALLOWED_HOSTS=staging.feedforward.edu
DATABASE_PATH=/var/lib/feedforward/staging.db
LOG_LEVEL=INFO
EMAIL_BACKEND=smtp
ENABLE_ANALYTICS=false
```

### Production Environment

```env
# Production settings
DEBUG=false
SECRET_KEY=${PRODUCTION_SECRET_KEY}
ALLOWED_HOSTS=feedforward.university.edu,www.feedforward.university.edu
DATABASE_PATH=/var/lib/feedforward/production.db
LOG_LEVEL=WARNING
EMAIL_BACKEND=smtp
ENABLE_ANALYTICS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

## Configuration Validation

### Validation Script

FeedForward includes a configuration validation tool:

```bash
# Validate configuration
python tools/validate_config.py

# Test specific settings
python tools/validate_config.py --test-email
python tools/validate_config.py --test-ai
python tools/validate_config.py --test-database
```

### Common Validation Errors

1. **Missing Required Values**
   ```
   ERROR: SECRET_KEY is required but not set
   ```
   Solution: Set all required environment variables

2. **Invalid Values**
   ```
   ERROR: LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
   ```
   Solution: Use valid values from documentation

3. **Connection Failures**
   ```
   ERROR: Cannot connect to SMTP server smtp.example.com:587
   ```
   Solution: Verify server settings and credentials

## Security Best Practices

### Secrets Management

1. **Never commit secrets**
   ```bash
   # Add to .gitignore
   .env
   .env.*
   *.key
   *.pem
   ```

2. **Use environment variables**
   ```bash
   # Production deployment
   export SECRET_KEY=$(cat /run/secrets/feedforward_secret_key)
   export OPENAI_API_KEY=$(cat /run/secrets/openai_api_key)
   ```

3. **Rotate regularly**
   - Change SECRET_KEY quarterly
   - Rotate API keys monthly
   - Update passwords regularly

### Secure Defaults

FeedForward uses secure defaults:
- HTTPS required in production
- Session cookies secure by default
- Debug mode disabled by default
- Strong password requirements

## Troubleshooting Configuration

### Debug Configuration Issues

1. **Check loaded values**
   ```python
   python -c "from app.config import settings; print(settings)"
   ```

2. **Verify environment**
   ```bash
   env | grep -E '^(APP_|DATABASE_|SMTP_)'
   ```

3. **Test components**
   ```bash
   # Test database
   python tools/test_database.py
   
   # Test email
   python tools/test_email.py recipient@example.com
   
   # Test AI providers
   python tools/test_ai_providers.py
   ```

### Common Issues

**Issue**: Changes not taking effect
- Solution: Restart application after changes
- Check: Environment variable precedence

**Issue**: Can't connect to services
- Solution: Verify firewall rules
- Check: Service URLs and ports

**Issue**: Performance problems
- Solution: Adjust worker settings
- Check: Resource limits

## Configuration Examples

### Minimal Configuration

```env
# Minimum required for production
SECRET_KEY=your-secure-random-key
APP_DOMAIN=https://feedforward.example.edu
OPENAI_API_KEY=sk-...
SMTP_SERVER=smtp.example.edu
SMTP_USER=feedforward@example.edu
SMTP_PASSWORD=smtp-password
```

### Full-Featured Configuration

```env
# Complete production configuration
# Security
SECRET_KEY=very-long-secure-random-key
DEBUG=false
ALLOWED_HOSTS=feedforward.edu,www.feedforward.edu

# Application
APP_NAME=University Writing Feedback
APP_DOMAIN=https://feedforward.university.edu
APP_DESCRIPTION=AI-powered writing feedback for students
SESSION_LIFETIME=43200
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# Database
DATABASE_PATH=/var/lib/feedforward/data/production.db
DATABASE_BACKUP_PATH=/backup/feedforward
DATABASE_JOURNAL_MODE=WAL

# Email
SMTP_SERVER=smtp.university.edu
SMTP_PORT=587
SMTP_USER=feedforward@university.edu
SMTP_PASSWORD=secure-smtp-password
SMTP_FROM=noreply@university.edu
SMTP_USE_TLS=true

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_AI_MODEL=gpt-4
AI_TIMEOUT=600
AI_MAX_RETRIES=5

# Privacy
DRAFT_RETENTION_HOURS=48
ANONYMIZE_SUBMISSIONS=true
ENABLE_ANALYTICS=true

# Performance
WORKER_PROCESSES=8
WORKER_THREADS=2
ENABLE_CACHE=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/feedforward/app.log

# Features
ENABLE_REGISTRATION=true
ENABLE_API=true

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

---

{: .tip }
> Keep a secure backup of your production configuration. Document any custom settings for your deployment.

{: .warning }
> Always validate configuration changes in a staging environment before applying to production.