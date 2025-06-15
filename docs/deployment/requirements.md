---
layout: default
title: Requirements
parent: Deployment
nav_order: 1
---

# System Requirements
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This document outlines the system requirements for deploying FeedForward in various environments. Requirements are categorized by deployment size and use case to help you choose the appropriate infrastructure.

## Deployment Scenarios

### Small Institution (< 1,000 users)

Suitable for:
- Small colleges or departments
- Pilot programs
- Development/testing environments

### Medium Institution (1,000 - 10,000 users)

Suitable for:
- Mid-sized universities
- Multiple department deployments
- Active production use

### Large Institution (> 10,000 users)

Suitable for:
- Large universities
- Multi-campus deployments
- High-availability requirements

## Hardware Requirements

### Minimum Requirements (Small Deployment)

```yaml
CPU: 2 cores (2.4GHz+)
RAM: 4GB
Storage: 20GB SSD
Network: 100 Mbps

Expected Capacity:
- Concurrent Users: 50-100
- Daily Submissions: 500
- Storage Growth: ~1GB/month
```

### Recommended Requirements (Medium Deployment)

```yaml
CPU: 4-8 cores (2.4GHz+)
RAM: 8-16GB
Storage: 100GB SSD
Network: 1 Gbps

Expected Capacity:
- Concurrent Users: 200-500
- Daily Submissions: 2,500
- Storage Growth: ~5GB/month
```

### Production Requirements (Large Deployment)

```yaml
CPU: 16+ cores (2.4GHz+)
RAM: 32GB+
Storage: 500GB+ SSD (RAID recommended)
Network: 1-10 Gbps

Expected Capacity:
- Concurrent Users: 1,000+
- Daily Submissions: 10,000+
- Storage Growth: ~20GB/month
```

## Software Requirements

### Operating System

#### Linux (Recommended)

```yaml
Supported Distributions:
  Ubuntu: 20.04 LTS, 22.04 LTS
  Debian: 11, 12
  RHEL/CentOS: 8, 9
  Amazon Linux: 2, 2023

Required Packages:
  - python3 (3.8+)
  - python3-pip
  - python3-venv
  - git
  - sqlite3
  - nginx (recommended)
  - supervisor/systemd
```

#### macOS

```yaml
Versions: 11.0+ (Big Sur or later)

Required Tools:
  - Homebrew
  - Python 3.8+ (via brew)
  - Git
  - SQLite (included)
```

#### Windows

```yaml
Versions: Windows 10, Windows Server 2019+

Required Software:
  - Python 3.8+ (python.org)
  - Git for Windows
  - Visual C++ Build Tools
  - Windows Terminal (recommended)

Note: WSL2 recommended for production
```

### Python Environment

```yaml
Python Version: 3.8 minimum, 3.10+ recommended

Core Dependencies:
  - fasthtml: Web framework
  - uvicorn: ASGI server
  - sqlite3: Database (included)
  - bcrypt: Password hashing
  - python-multipart: File uploads
  - litellm: AI provider integration
  - cryptography: Encryption
  
Development Tools:
  - pytest: Testing
  - black: Code formatting
  - mypy: Type checking
  - pip-tools: Dependency management
```

### Database Requirements

#### SQLite (Default)

```yaml
Version: 3.32.0+ (included with Python)

Configuration:
  - WAL mode enabled
  - Foreign keys enabled
  - Auto-vacuum enabled
  
Limitations:
  - Single file database
  - Limited concurrent writes
  - Max size: ~280TB (practical: 10GB)
```

#### PostgreSQL (Future Option)

```yaml
Version: 12+

Benefits:
  - Better concurrency
  - Advanced features
  - Horizontal scaling
  
Requirements:
  - Dedicated database server
  - Connection pooling
  - Regular maintenance
```

### Web Server Requirements

#### Development Server

```yaml
Server: Uvicorn (included)

Usage:
  - Development only
  - Single process
  - Auto-reload
  
Command: python app.py
```

#### Production Server

```yaml
Reverse Proxy: nginx

Configuration:
  - SSL termination
  - Static file serving
  - Load balancing
  - Rate limiting
  
Application Server: Uvicorn + Gunicorn

Configuration:
  - Multiple workers
  - Process management
  - Graceful reloads
  - Health checks
```

## Network Requirements

### Bandwidth

```yaml
Minimum Bandwidth:
  Per User: 1 Mbps
  API Calls: 10 Mbps reserved
  
Recommended:
  Institution: 100 Mbps+
  Peak Usage: 500 Mbps
  
Considerations:
  - File uploads (10MB max)
  - AI API calls
  - Concurrent users
  - Backup transfers
```

### Ports

```yaml
Required Ports:
  HTTP: 80 (redirect to HTTPS)
  HTTPS: 443 (main access)
  
Internal Ports:
  Application: 5001 (default)
  Database: N/A (file-based)
  
Outbound Connections:
  HTTPS: 443 (AI APIs)
  SMTP: 587/465 (email)
```

### DNS Requirements

```yaml
Domain Setup:
  A Record: feedforward.institution.edu
  
Optional:
  CNAME: www.feedforward.institution.edu
  
SSL Certificate:
  Type: Valid CA-signed
  Coverage: Main domain + www
  Renewal: Auto-renewal recommended
```

## External Service Requirements

### AI/LLM Providers

At least one required:

```yaml
OpenAI:
  - API Key required
  - Billing enabled
  - Usage limits configured
  
Anthropic:
  - API Key required
  - Approved account
  
Google AI:
  - API Key or Service Account
  - Project configured
  
Ollama (Local):
  - Local server running
  - Models downloaded
  - Sufficient GPU/RAM
```

### Email Service

```yaml
SMTP Requirements:
  - SMTP server access
  - Authentication credentials
  - TLS/SSL support
  - Appropriate send limits
  
Options:
  - Institution SMTP
  - Gmail (with app password)
  - SendGrid
  - Amazon SES
  - Mailgun
```

### Monitoring (Optional)

```yaml
Recommended Services:
  - Application monitoring (New Relic, DataDog)
  - Log aggregation (ELK, Splunk)
  - Uptime monitoring (Pingdom, UptimeRobot)
  - Error tracking (Sentry)
```

## Security Requirements

### SSL/TLS

```yaml
Requirements:
  - Valid SSL certificate
  - TLS 1.2 minimum
  - Strong cipher suites
  - HSTS enabled
  
Certificate Options:
  - Let's Encrypt (free)
  - Commercial CA
  - Institution wildcard
```

### Firewall

```yaml
Inbound Rules:
  - 443/tcp from anywhere (HTTPS)
  - 80/tcp from anywhere (redirect)
  - 22/tcp from admin IPs (SSH)
  
Outbound Rules:
  - 443/tcp to anywhere (APIs)
  - 587/tcp to SMTP server
  - 53/udp to DNS servers
  
Internal:
  - 5001/tcp localhost only
```

### Access Control

```yaml
Server Access:
  - SSH key authentication
  - Sudo access limited
  - Regular security updates
  
Application Access:
  - Strong admin passwords
  - Regular key rotation
  - Audit logging enabled
```

## Performance Considerations

### Resource Scaling

```yaml
CPU Scaling:
  - 1 core per 50 concurrent users
  - Additional cores for AI processing
  
RAM Scaling:
  - 100MB per concurrent user
  - 2GB base system requirement
  - Cache allocation extra
  
Storage Scaling:
  - 10MB per submission average
  - 1GB per 1000 users
  - 20% overhead for indexes
```

### Optimization Checklist

- [ ] Enable database WAL mode
- [ ] Configure connection pooling
- [ ] Set up static file caching
- [ ] Enable gzip compression
- [ ] Optimize database indexes
- [ ] Configure worker processes
- [ ] Set up monitoring alerts
- [ ] Plan backup strategy

## Backup Requirements

### Backup Storage

```yaml
Storage Needs:
  - 3x database size minimum
  - Remote backup location
  - Encryption capability
  
Backup Frequency:
  - Database: Daily
  - Configuration: On change
  - Logs: Weekly rotation
```

### Recovery Requirements

```yaml
RTO (Recovery Time Objective): 4 hours
RPO (Recovery Point Objective): 24 hours

Test Schedule:
  - Monthly restore test
  - Quarterly DR drill
  - Annual full recovery
```

## Compliance Requirements

### Data Residency

```yaml
Considerations:
  - Data must stay in country/region
  - AI API calls may cross borders
  - Backup location compliance
  
Solutions:
  - Local deployment
  - Regional AI endpoints
  - Compliant backup services
```

### Audit Requirements

```yaml
Logging:
  - All authentication attempts
  - Data access patterns
  - Configuration changes
  - API usage
  
Retention:
  - Audit logs: 1 year
  - Access logs: 90 days
  - Error logs: 30 days
```

## Environment-Specific Requirements

### Development Environment

```yaml
Purpose: Local development

Requirements:
  - Python 3.8+
  - Git
  - Text editor/IDE
  - 2GB RAM free
  - 5GB disk space
  
Optional:
  - Docker Desktop
  - PostgreSQL (testing)
  - Multiple browsers
```

### Staging Environment

```yaml
Purpose: Pre-production testing

Requirements:
  - Mirrors production
  - Separate database
  - Test data only
  - Same OS version
  - Similar resources (50%)
```

### Production Environment

```yaml
Purpose: Live system

Requirements:
  - Meets all requirements above
  - Redundant components
  - Monitoring active
  - Backup configured
  - Security hardened
```

## Quick Requirement Check

### Minimum Viable Deployment

✓ 2 CPU cores, 4GB RAM, 20GB SSD  
✓ Ubuntu 20.04 or similar  
✓ Python 3.8+  
✓ One AI API key  
✓ SMTP access  
✓ Domain name  
✓ SSL certificate  

### Recommended Production

✓ 8 CPU cores, 16GB RAM, 100GB SSD  
✓ Ubuntu 22.04 LTS  
✓ Python 3.10+  
✓ Multiple AI providers  
✓ Dedicated SMTP  
✓ Monitoring setup  
✓ Automated backups  
✓ Load balancer ready  

---

{: .note }
> Start with minimum requirements and scale up based on actual usage patterns. Most institutions find the recommended specifications sufficient for their needs.