---
layout: default
title: User Management
parent: Admin Guide
grand_parent: User Guides
nav_order: 2
---

# User Management Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

User management is a critical administrative function in FeedForward. This guide covers creating and managing instructor accounts, handling permissions, and maintaining user security. Students are managed by instructors through course invitations.

## User Roles in FeedForward

### Role Hierarchy

FeedForward has three distinct user roles:

1. **Administrator**
   - Full system access
   - Manages instructors and system configuration
   - Controls AI providers and global settings
   - Cannot directly manage students

2. **Instructor**
   - Creates and manages courses
   - Invites students to courses
   - Reviews and approves AI feedback
   - Manages own AI models (if permitted)

3. **Student**
   - Joins courses via invitation
   - Submits assignment drafts
   - Views feedback
   - Tracks progress

{: .note }
> Students cannot self-register. They must be invited by instructors to maintain institutional control.

## Managing Instructors

### Creating Instructor Accounts

#### Method 1: Individual Creation

1. Navigate to **Users** → **Instructors**
2. Click **"Create New Instructor"**
3. Fill in the required information:

```
Personal Information:
- First Name: Required
- Last Name: Required
- Email: Required (must be unique)
- Employee ID: Optional (for integration)

Account Settings:
- Username: Auto-generated from email
- Temporary Password: System generates or set manually
- Force Password Change: Yes (recommended)
- Account Status: Active

Permissions:
- Can Create Courses: Yes
- Can Manage Own AI Keys: No (default)
- Course Limit: 10 (default)
- Student Limit per Course: 200 (default)
```

4. Click **"Create Account"**
5. System sends welcome email with login instructions

#### Method 2: Bulk Import

1. Go to **Users** → **Import**
2. Download the CSV template
3. Fill in instructor data:

```csv
first_name,last_name,email,employee_id,department
John,Smith,jsmith@university.edu,12345,Computer Science
Jane,Doe,jdoe@university.edu,12346,English
Robert,Johnson,rjohnson@university.edu,12347,Mathematics
```

4. Upload the completed CSV
5. Review import preview
6. Click **"Import Instructors"**

{: .tip }
> Use bulk import for semester starts when onboarding multiple instructors.

### Editing Instructor Accounts

1. Navigate to **Users** → **Instructors**
2. Find the instructor (use search or filters)
3. Click **"Edit"** next to their name
4. Update information as needed:
   - Personal details
   - Contact information
   - Permissions
   - Resource limits
5. Click **"Save Changes"**

### Managing Instructor Permissions

#### Standard Permissions

Configure what instructors can do:

```
Course Management:
- Create Courses: Yes/No
- Maximum Courses: Number
- Archive Courses: Yes/No
- Delete Courses: Yes/No

Student Management:
- Invite Students: Yes
- Remove Students: Yes
- Max Students per Course: Number
- View Student Details: Yes

AI Configuration:
- Use System AI Models: Yes
- Add Own AI Keys: Yes/No
- Configure AI Settings: Yes
- View AI Usage: Yes

Feedback Control:
- Override AI Feedback: Yes
- Bulk Approve Feedback: Yes/No
- Export Feedback: Yes
- Delete Feedback: Yes/No
```

#### Advanced Permissions

For trusted instructors or department heads:

```
Administrative:
- View Department Analytics: Yes/No
- Manage Department Instructors: Yes/No
- Access Cost Reports: Yes/No
- Export System Data: Yes/No
```

### Account Status Management

#### Deactivating Accounts

When an instructor leaves:

1. Go to instructor's profile
2. Click **"Deactivate Account"**
3. Choose deactivation options:
   - Immediate: Account locked now
   - Scheduled: Set future date
   - End of Semester: Automatic timing
4. Handle existing courses:
   - Transfer to another instructor
   - Archive with read-only access
   - Delete after export

#### Reactivating Accounts

1. Go to **Users** → **Inactive**
2. Find the instructor
3. Click **"Reactivate"**
4. Reset password if needed
5. Review and update permissions

## User Account Security

### Password Policies

Configure password requirements:

1. Navigate to **Settings** → **Security** → **Passwords**
2. Set password rules:

```
Minimum Length: 12 characters
Complexity Requirements:
- Uppercase Letters: Required
- Lowercase Letters: Required
- Numbers: Required
- Special Characters: Required

Additional Rules:
- No Common Passwords: Enabled
- No Personal Info: Enabled
- Password History: Last 5 passwords
- Maximum Age: 90 days
- Minimum Age: 1 day
```

### Account Lockout Policies

Protect against brute force attacks:

```
Failed Login Attempts: 5
Lockout Duration: 30 minutes
Reset Counter After: 30 minutes
Admin Override: Available
IP-Based Blocking: Enabled
```

### Password Management

#### Resetting Passwords

1. Find the user in **Users** → **Instructors**
2. Click **"Reset Password"**
3. Choose reset method:
   - Email reset link
   - Generate temporary password
   - Set specific password
4. Notify user of reset

#### Bulk Password Reset

For security incidents:

1. Go to **Security** → **Bulk Actions**
2. Select **"Force Password Reset"**
3. Choose scope:
   - All instructors
   - Specific department
   - Last login before date
4. Execute and monitor completion

## User Activity Monitoring

### Login History

View user login activity:

1. Navigate to **Users** → **Activity**
2. Filter by:
   - User
   - Date range
   - Success/Failure
   - IP address
3. Export for analysis

### Audit Trails

Track administrative actions:

```
Tracked Actions:
- Account creation/deletion
- Permission changes
- Password resets
- Course transfers
- AI key additions
```

Access audit logs:
1. Go to **Security** → **Audit Logs**
2. Search by user, action, or date
3. Export for compliance

### Usage Analytics

Monitor instructor activity:

1. Navigate to **Analytics** → **Instructors**
2. View metrics:
   - Courses created
   - Students managed
   - AI usage
   - Feedback reviewed
   - Last active date

## Managing Departments

### Creating Departments

1. Go to **Organization** → **Departments**
2. Click **"Add Department"**
3. Enter details:

```
Department Name: Computer Science
Code: CS
Head: Dr. Smith (select from instructors)
Parent Department: None (or select)
Status: Active
```

### Department Permissions

Set department-wide policies:

```
Default Instructor Limits:
- Courses: 10
- Students per Course: 150
- AI Calls per Month: 10000

Department Features:
- Shared Rubric Templates: Yes
- Department Analytics: Yes
- Cost Center Tracking: Yes
```

## User Support

### Common User Issues

**Cannot Log In**
1. Check account status (active/inactive)
2. Verify email address spelling
3. Check password expiration
4. Review lockout status
5. Reset password if needed

**Missing Permissions**
1. Review role assignment
2. Check department settings
3. Verify individual overrides
4. Update as needed

**Email Not Received**
1. Check email configuration
2. Verify email address
3. Check spam filters
4. Resend welcome email

### User Communications

#### System Announcements

1. Go to **Communications** → **Announcements**
2. Create announcement:
   - Title
   - Message
   - Target audience
   - Display period
3. Publish to dashboard

#### Mass Emails

1. Navigate to **Communications** → **Email**
2. Compose message
3. Select recipients:
   - All instructors
   - Specific departments
   - Custom selection
4. Send or schedule

## Best Practices

### Onboarding New Instructors

1. **Week Before Start**
   - Create accounts
   - Send welcome emails
   - Schedule training

2. **First Day**
   - Verify login works
   - Review permissions
   - Provide documentation

3. **First Week**
   - Monitor activity
   - Address issues
   - Gather feedback

### Regular Maintenance

**Monthly Tasks**
- Review inactive accounts
- Check failed login attempts
- Update department rosters
- Audit permissions

**Quarterly Tasks**
- Password policy review
- Security audit
- Usage analysis
- Training updates

**Annual Tasks**
- Full user audit
- Policy updates
- Security review
- Archive old accounts

### Security Recommendations

1. **Enforce Strong Passwords**
   - Minimum 12 characters
   - Regular rotation
   - Complexity requirements

2. **Monitor Access**
   - Regular login reviews
   - Unusual activity alerts
   - Geographic restrictions

3. **Principle of Least Privilege**
   - Only necessary permissions
   - Regular permission audits
   - Time-limited elevated access

## Compliance Considerations

### Data Protection

- Store minimal personal data
- Implement retention policies
- Enable audit trails
- Document access

### Access Control

- Role-based permissions
- Regular access reviews
- Terminated user procedures
- Guest account policies

## Next Steps

- [AI Configuration](./ai-configuration) - Set up AI providers
- [Maintenance](./maintenance) - System maintenance procedures
- [Security Best Practices](/deployment/security) - Advanced security configuration

---

{: .warning }
> Always follow your institution's HR policies when managing user accounts and access.