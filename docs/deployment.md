---
layout: default
title: Deployment
nav_order: 6
has_children: true
permalink: /deployment
---

# Deployment Guide
{: .no_toc }

Everything you need to deploy FeedForward in production.
{: .fs-6 .fw-300 }

This section provides comprehensive guidance for deploying FeedForward in various environments.

## Documentation Overview

### Prerequisites & Planning
- **[Requirements](./deployment/requirements)** - System and software requirements
- **[Capacity Planning](./deployment/capacity-planning)** - Sizing your deployment

### Installation & Configuration
- **[Installation Guide](./deployment/installation)** - Step-by-step production deployment
- **[Configuration Reference](./deployment/configuration)** - All configuration options explained
- **[Security Hardening](./deployment/security)** - Production security best practices

### Operations & Maintenance
- **[Monitoring](./deployment/monitoring)** - Health checks and performance monitoring
- **[Backup & Recovery](./deployment/backup)** - Data protection strategies
- **[Troubleshooting](./deployment/troubleshooting)** - Common issues and solutions

---

## Deployment Options

### 🖥️ Single Server
Ideal for small to medium institutions (up to 1,000 students)
- Simple setup and maintenance
- SQLite database included
- Minimal resource requirements

### ☁️ Cloud Deployment
For larger institutions or high availability needs
- Scalable architecture
- PostgreSQL/MySQL support
- Load balancing capabilities

### 🐳 Container Deployment
For organizations with existing container infrastructure
- Docker images available
- Kubernetes configurations
- Easy scaling and updates

---

## Quick Deployment Checklist

{: .important }
> Before deploying to production, ensure you have:
> - [ ] Reviewed system requirements
> - [ ] Obtained API keys for LLM providers
> - [ ] Configured SSL/TLS certificates
> - [ ] Set up backup procedures
> - [ ] Reviewed security guidelines