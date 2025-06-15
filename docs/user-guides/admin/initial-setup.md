---
layout: default
title: Initial Setup
parent: Admin Guide
grand_parent: User Guides
nav_order: 1
---

# Initial Setup Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This guide walks you through the initial configuration of FeedForward after installation. Following these steps ensures your system is properly configured, secure, and ready for instructors and students.

{: .important }
> Complete these setup steps before allowing instructors to create courses or students to submit work.

## Pre-Setup Checklist

Before beginning initial setup, ensure you have:

- [ ] Completed the [installation process](/getting-started/installation)
- [ ] Created an admin account
- [ ] Started the FeedForward server
- [ ] Access to AI provider API keys
- [ ] SMTP email server credentials
- [ ] SSL certificate (for production)

## Step 1: Access Admin Dashboard

1. **Navigate** to your FeedForward instance
2. **Log in** with your administrator credentials
3. **Click** "Admin Dashboard" in the navigation menu
4. **Verify** you see the admin interface

{: .tip }
> Bookmark the admin dashboard URL for quick access: `http://your-domain/admin`

## Step 2: Configure Core Settings

### Application Settings

1. Go to **Settings** → **Application**
2. Configure the following:

```
Application Name: FeedForward
Institution Name: Your University
Support Email: support@youruniversity.edu
Time Zone: America/New_York
Default Language: en
```

### Security Settings

1. Navigate to **Settings** → **Security**
2. Configure security options:

```
Session Timeout: 24 hours
Max Login Attempts: 5
Password Requirements:
  - Minimum Length: 12
  - Require Numbers: Yes
  - Require Special Characters: Yes
  - Require Mixed Case: Yes
  
Enable Audit Logging: Yes
Log Retention Days: 90
```

{: .warning }
> For production deployments, always enable HTTPS and secure cookies.

### Privacy Settings

1. Go to **Settings** → **Privacy**
2. Set privacy options:

```
Draft Retention: 24 hours
Auto-Delete Submissions: Yes
Anonymize Analytics: Yes
Data Export Format: JSON
GDPR Compliance Mode: Yes
```

## Step 3: Email Configuration

Email is essential for sending course invitations to students.

### SMTP Setup

1. Navigate to **Settings** → **Email**
2. Enter your SMTP configuration:

```
SMTP Server: smtp.gmail.com
Port: 587
Username: feedforward@youruniversity.edu
Password: [your-app-password]
Use TLS: Yes
From Address: noreply@youruniversity.edu
From Name: FeedForward System
```

### Test Email Configuration

1. Click **"Test Email Settings"**
2. Enter your email address
3. Click **"Send Test"**
4. Verify you receive the test email

{: .note }
> If using Gmail, create an [app-specific password](https://support.google.com/accounts/answer/185833) rather than using your regular password.

### Email Templates

1. Go to **Settings** → **Email Templates**
2. Customize templates for:
   - Student Invitations
   - Password Resets
   - Assignment Notifications
   - Feedback Ready Alerts

## Step 4: AI Provider Configuration

### Add Your First AI Provider

1. Navigate to **AI Models** → **Providers**
2. Click **"Add Provider"**
3. Select your provider type:

#### OpenAI Configuration
```
Provider: OpenAI
API Key: sk-...your-key-here
Organization ID: org-...your-org (optional)
Default Model: gpt-4
Max Tokens: 2000
Temperature: 0.7
```

#### Anthropic Configuration
```
Provider: Anthropic
API Key: sk-ant-...your-key
Default Model: claude-3-opus-20240229
Max Tokens: 2000
Temperature: 0.7
```

#### Google AI Configuration
```
Provider: Google AI
API Key: ...your-key
Default Model: gemini-pro
Max Tokens: 2000
Temperature: 0.7
```

### Test AI Connection

1. After saving, click **"Test Connection"**
2. The system will verify:
   - API key validity
   - Model availability
   - Response generation
3. Check the test results

### Set Default Models

1. Go to **AI Models** → **System Defaults**
2. Set defaults for:
   - Primary Feedback Model
   - Fallback Model
   - Quick Feedback Model

## Step 5: Create Initial Users

### Create Your First Instructor

1. Navigate to **Users** → **Instructors**
2. Click **"Create Instructor"**
3. Fill in details:

```
Name: Dr. Jane Smith
Email: jsmith@university.edu
Department: English
Employee ID: 12345
Temporary Password: [generate]
Send Welcome Email: Yes
```

### Set Up Departments (Optional)

1. Go to **Users** → **Departments**
2. Create department structure:
   - English Department
   - Computer Science
   - Mathematics
   - Business

## Step 6: Configure System Limits

### Resource Limits

1. Navigate to **Settings** → **Limits**
2. Configure appropriate limits:

```
Max Students per Course: 500
Max Assignments per Course: 20
Max Drafts per Assignment: 5
Max File Upload Size: 10MB
Max AI Calls per Day: 10000
Max Concurrent Processing: 10
```

### Rate Limiting

```
API Calls per Minute: 60
Submissions per Student per Hour: 10
Login Attempts per IP: 10
Password Reset per Email: 3
```

## Step 7: Set Up Monitoring

### Enable Monitoring

1. Go to **Monitoring** → **Configuration**
2. Enable monitoring features:

```
System Metrics: Enabled
API Usage Tracking: Enabled
Error Logging: Enabled
Performance Monitoring: Enabled
User Activity Tracking: Enabled
```

### Configure Alerts

1. Navigate to **Monitoring** → **Alerts**
2. Set up alerts for:

```
High API Usage: > 80% of daily limit
System Errors: > 10 per hour
Failed Logins: > 20 per hour
Database Size: > 80% of limit
Queue Backlog: > 100 items
```

### Alert Recipients

Add email addresses for alert notifications:
- admin@university.edu
- it-support@university.edu

## Step 8: Backup Configuration

### Automatic Backups

1. Go to **Maintenance** → **Backups**
2. Configure backup settings:

```
Backup Schedule: Daily at 2:00 AM
Retention Period: 30 days
Backup Location: /backups/feedforward/
Include Submissions: No (privacy)
Compress Backups: Yes
```

### Test Backup

1. Click **"Run Backup Now"**
2. Verify backup completes successfully
3. Check backup file is created

## Step 9: Final Verification

### System Health Check

1. Go to **Dashboard**
2. Verify all indicators are green:
   - ✅ Database Connected
   - ✅ Email Configured
   - ✅ AI Providers Active
   - ✅ Storage Available
   - ✅ No Error Alerts

### Test User Flow

1. Create a test instructor account
2. Log in as test instructor
3. Create a test course
4. Verify all functions work

### Documentation

1. Document your configuration:
   - AI provider details
   - Email settings
   - Backup locations
   - Admin contacts

## Post-Setup Tasks

### Immediate Actions

1. **Change default passwords** for all test accounts
2. **Enable SSL/HTTPS** for production
3. **Configure firewall** rules
4. **Set up monitoring** dashboards

### Within First Week

1. **Train instructors** on the system
2. **Create documentation** for your institution
3. **Establish support** procedures
4. **Plan maintenance** windows

### Ongoing Maintenance

1. **Weekly**: Check system health and logs
2. **Monthly**: Review AI usage and costs
3. **Quarterly**: Update API keys
4. **Annually**: Review security settings

## Troubleshooting Setup Issues

### Common Problems

**Cannot send emails**
- Verify SMTP credentials
- Check firewall allows port 587/465
- Try with different email provider
- Check spam filters

**AI provider connection fails**
- Verify API key is active
- Check billing/credits available
- Ensure network allows HTTPS
- Try different model

**Database errors**
- Check disk space
- Verify file permissions
- Run database integrity check
- Review error logs

## Next Steps

Your FeedForward instance is now configured! Continue with:

1. [User Management](./user-management) - Create instructor accounts
2. [AI Configuration](./ai-configuration) - Fine-tune AI settings
3. [Maintenance](./maintenance) - Set up regular maintenance

---

{: .tip }
> Save a copy of your configuration settings in a secure location for disaster recovery purposes.