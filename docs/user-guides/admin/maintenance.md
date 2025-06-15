---
layout: default
title: Maintenance
parent: Admin Guide
grand_parent: User Guides
nav_order: 4
---

# Maintenance Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Regular maintenance ensures FeedForward runs smoothly, securely, and efficiently. This guide covers backup procedures, monitoring setup, performance optimization, and routine maintenance tasks.

## Backup Procedures

### Backup Strategy

FeedForward uses a comprehensive backup strategy:

```yaml
Backup Components:
  Database: Full SQLite database files
  Configuration: Environment variables and settings
  Uploads: Temporary student submissions (if retained)
  Logs: System and audit logs
  
Backup Schedule:
  Database: Daily at 2:00 AM
  Configuration: On change + weekly
  Logs: Weekly rotation
  Full System: Weekly
```

### Automated Backups

#### Setting Up Automated Backups

1. Navigate to **System** → **Backup Configuration**
2. Configure backup settings:

```yaml
Backup Configuration:
  Enabled: Yes
  Schedule: "0 2 * * *" (2 AM daily)
  Retention Days: 30
  
Storage Location:
  Type: Local Directory
  Path: /backups/feedforward/
  
Compression:
  Enable: Yes
  Type: gzip
  Level: 6
  
Encryption:
  Enable: Yes (recommended)
  Method: AES-256
  Key Location: /secure/backup.key
```

#### Backup Script

The automated backup script (`tools/backup.py`) performs:

```bash
# Run manually
python tools/backup.py

# Or via cron
0 2 * * * /path/to/venv/bin/python /path/to/tools/backup.py
```

### Manual Backups

#### Full System Backup

1. Stop the FeedForward service:
   ```bash
   systemctl stop feedforward
   ```

2. Create backup directory:
   ```bash
   mkdir -p /backups/feedforward/$(date +%Y%m%d)
   ```

3. Backup database:
   ```bash
   cp data/feedforward.db /backups/feedforward/$(date +%Y%m%d)/
   ```

4. Backup configuration:
   ```bash
   cp .env /backups/feedforward/$(date +%Y%m%d)/
   cp -r config/ /backups/feedforward/$(date +%Y%m%d)/
   ```

5. Create archive:
   ```bash
   tar -czf /backups/feedforward/backup-$(date +%Y%m%d).tar.gz \
     /backups/feedforward/$(date +%Y%m%d)/
   ```

6. Restart service:
   ```bash
   systemctl start feedforward
   ```

### Backup Verification

#### Testing Backups

1. **Monthly verification:**
   ```bash
   python tools/verify_backup.py /path/to/backup.tar.gz
   ```

2. **Restore test:**
   - Use test environment
   - Restore latest backup
   - Verify data integrity
   - Test application functions

#### Backup Monitoring

Set up alerts for backup failures:

1. Go to **System** → **Monitoring** → **Backup Alerts**
2. Configure:
   ```yaml
   Alert on:
     - Backup failure
     - Backup missing (> 25 hours)
     - Low disk space (< 10GB)
     - Verification failure
   ```

### Restore Procedures

#### Database Restore

1. Stop FeedForward:
   ```bash
   systemctl stop feedforward
   ```

2. Backup current database:
   ```bash
   mv data/feedforward.db data/feedforward.db.old
   ```

3. Restore from backup:
   ```bash
   cp /backups/feedforward/backup.db data/feedforward.db
   ```

4. Verify permissions:
   ```bash
   chown feedforward:feedforward data/feedforward.db
   chmod 644 data/feedforward.db
   ```

5. Start service:
   ```bash
   systemctl start feedforward
   ```

## System Monitoring

### Health Checks

#### Automated Health Monitoring

1. Configure health checks:
   ```yaml
   Health Check Endpoints:
     Basic: /health
     Detailed: /health/detailed
     Database: /health/db
     AI Providers: /health/ai
   
   Check Interval: 5 minutes
   Timeout: 30 seconds
   Retries: 3
   ```

2. Set up monitoring service:
   ```bash
   # Using systemd
   systemctl enable feedforward-monitor
   systemctl start feedforward-monitor
   ```

#### Manual Health Checks

Run comprehensive health check:

```bash
python tools/health_check.py --verbose

# Output:
✓ Database: Connected (15.2 MB)
✓ Email: SMTP connection active
✓ AI Providers:
  ✓ OpenAI: Active (1,234 calls today)
  ✓ Anthropic: Active (567 calls today)
✓ Storage: 45.6 GB free (78%)
✓ Memory: 2.3 GB used (29%)
✓ CPU: 12% average load
```

### Performance Monitoring

#### Key Metrics

Monitor these performance indicators:

```yaml
Application Metrics:
  - Response time (target: < 200ms)
  - Concurrent users
  - Request rate
  - Error rate (target: < 0.1%)
  
Database Metrics:
  - Query time (target: < 50ms)
  - Connection pool usage
  - Database size
  - Lock contention
  
AI Metrics:
  - API response time
  - Token usage
  - Cost per feedback
  - Model availability
```

#### Setting Up Monitoring Dashboard

1. Access **System** → **Monitoring Dashboard**
2. Configure widgets:
   - System overview
   - Real-time metrics
   - AI usage graphs
   - Error logs

### Log Management

#### Log Rotation

Configure automatic log rotation:

```yaml
Log Rotation Policy:
  Application Logs:
    Max Size: 100 MB
    Max Age: 30 days
    Compress: Yes
    
  Audit Logs:
    Max Size: 500 MB
    Max Age: 365 days
    Archive: Yes
    
  Access Logs:
    Max Size: 200 MB
    Max Age: 90 days
    Compress: Yes
```

#### Log Analysis

Regular log review tasks:

1. **Daily:** Check error logs
   ```bash
   grep ERROR logs/feedforward.log | tail -50
   ```

2. **Weekly:** Analyze patterns
   ```bash
   python tools/log_analyzer.py --last-week
   ```

3. **Monthly:** Generate reports
   ```bash
   python tools/generate_log_report.py --month
   ```

## Database Maintenance

### Regular Optimization

#### Weekly Tasks

1. **Vacuum database:**
   ```sql
   -- Run during low usage
   VACUUM;
   ANALYZE;
   ```

2. **Check integrity:**
   ```bash
   python tools/db_check.py
   ```

3. **Update statistics:**
   ```sql
   ANALYZE main;
   ```

#### Monthly Tasks

1. **Full optimization:**
   ```bash
   python tools/db_optimize.py --full
   ```

2. **Index maintenance:**
   ```sql
   -- Rebuild fragmented indexes
   REINDEX;
   ```

3. **Archive old data:**
   ```bash
   python tools/archive_old_data.py --months 6
   ```

### Database Growth Management

Monitor and manage database size:

```yaml
Size Thresholds:
  Warning: 5 GB
  Critical: 8 GB
  Maximum: 10 GB
  
Actions:
  At Warning: Alert admin
  At Critical: Archive old data
  At Maximum: Prevent new submissions
```

### Privacy Compliance

Ensure privacy-compliant data management:

1. **Automated cleanup:**
   ```bash
   # Remove old submission content
   python tools/cleanup_drafts.py
   
   # Verify cleanup
   python tools/verify_privacy_compliance.py
   ```

2. **Audit trail maintenance:**
   - Keep audit logs as required
   - Anonymize old entries
   - Export for compliance

## Performance Optimization

### Application Tuning

#### Worker Configuration

Optimize based on server resources:

```yaml
Worker Settings:
  Workers: (2 × CPU cores) + 1
  Threads: 2-4 per worker
  Max Requests: 1000
  Timeout: 120 seconds
  
Example (4-core server):
  Workers: 9
  Threads: 3
  Total Capacity: 27 concurrent requests
```

#### Caching Configuration

Enable caching for better performance:

```yaml
Cache Settings:
  Static Files: 1 hour
  API Responses: 5 minutes
  User Sessions: 24 hours
  AI Results: 1 hour
  
Cache Storage:
  Type: Memory (Redis recommended)
  Max Size: 1 GB
  Eviction: LRU
```

### Database Optimization

#### Query Optimization

1. **Identify slow queries:**
   ```bash
   python tools/slow_query_log.py --threshold 100ms
   ```

2. **Add missing indexes:**
   ```sql
   -- Example: Speed up assignment lookups
   CREATE INDEX idx_assignment_course 
   ON assignments(course_id, status);
   ```

3. **Optimize common queries:**
   - Use prepared statements
   - Batch operations
   - Limit result sets

#### Connection Pool Tuning

```yaml
Database Pool:
  Min Connections: 5
  Max Connections: 20
  Max Overflow: 10
  Timeout: 30 seconds
  Recycle: 3600 seconds
```

## Security Maintenance

### Security Updates

#### Regular Tasks

1. **Weekly security scan:**
   ```bash
   python tools/security_scan.py
   ```

2. **Dependency updates:**
   ```bash
   # Check for updates
   pip list --outdated
   
   # Update safely
   pip install --upgrade -r requirements.txt
   ```

3. **Certificate management:**
   - Check SSL expiration
   - Renew certificates
   - Update configurations

### Access Auditing

Regular access reviews:

1. **Monthly user audit:**
   ```bash
   python tools/user_audit.py --inactive-days 90
   ```

2. **Permission review:**
   - Check admin accounts
   - Verify instructor limits
   - Remove unused accounts

3. **API key rotation:**
   - Schedule quarterly rotation
   - Update documentation
   - Test after rotation

## Routine Maintenance Schedule

### Daily Tasks

- [ ] Check system health dashboard
- [ ] Review error logs
- [ ] Monitor AI usage/costs
- [ ] Verify backup completion
- [ ] Check disk space

### Weekly Tasks

- [ ] Database optimization
- [ ] Log rotation and cleanup
- [ ] Security scan
- [ ] Performance review
- [ ] Update monitoring alerts

### Monthly Tasks

- [ ] Full system backup verification
- [ ] User access audit
- [ ] Database integrity check
- [ ] Generate usage reports
- [ ] Review and update documentation

### Quarterly Tasks

- [ ] API key rotation
- [ ] Security audit
- [ ] Performance baseline update
- [ ] Disaster recovery drill
- [ ] Update maintenance procedures

## Troubleshooting Maintenance Issues

### Common Problems

**High Database Growth**
```bash
# Identify large tables
python tools/db_size_report.py

# Clean up old data
python tools/cleanup_old_data.py --days 180
```

**Performance Degradation**
```bash
# Run performance diagnostic
python tools/performance_diagnostic.py

# Common fixes:
- Increase worker count
- Add database indexes
- Enable caching
- Optimize queries
```

**Backup Failures**
```bash
# Check disk space
df -h /backups

# Verify permissions
ls -la /backups/feedforward/

# Test backup manually
python tools/backup.py --verbose
```

## Maintenance Automation

### Setting Up Cron Jobs

Create maintenance schedule:

```bash
# Edit crontab
crontab -e

# Add maintenance tasks
# Daily backup (2 AM)
0 2 * * * /path/to/venv/bin/python /path/to/tools/backup.py

# Weekly optimization (Sunday 3 AM)
0 3 * * 0 /path/to/venv/bin/python /path/to/tools/db_optimize.py

# Monthly report (1st day, 4 AM)
0 4 1 * * /path/to/venv/bin/python /path/to/tools/generate_monthly_report.py

# Privacy cleanup (daily 1 AM)
0 1 * * * /path/to/venv/bin/python /path/to/tools/cleanup_drafts.py
```

### Monitoring Automation

Set up automated monitoring:

1. **Health check monitoring:**
   ```yaml
   Service: feedforward-monitor
   Type: systemd timer
   Interval: 5 minutes
   Action: Email on failure
   ```

2. **Performance alerts:**
   ```yaml
   Metrics:
     CPU > 80%: Warning
     Memory > 90%: Critical
     Disk > 85%: Warning
     Response Time > 500ms: Alert
   ```

## Disaster Recovery

### Recovery Plan

Document and test recovery procedures:

1. **Recovery Time Objective (RTO):** 4 hours
2. **Recovery Point Objective (RPO):** 24 hours
3. **Key contacts and procedures documented**
4. **Quarterly disaster recovery drills**

### Emergency Procedures

In case of system failure:

1. **Assess the situation**
2. **Notify stakeholders**
3. **Initiate recovery procedures**
4. **Restore from latest backup**
5. **Verify system integrity**
6. **Document incident**

## Next Steps

- Review [Security Best Practices](/deployment/security)
- Set up [Monitoring Dashboard](/deployment/monitoring)
- Create [Disaster Recovery Plan](/deployment/disaster-recovery)

---

{: .warning }
> Always perform maintenance during scheduled windows and notify users in advance.

{: .tip }
> Automate as many maintenance tasks as possible to ensure consistency and reduce manual errors.