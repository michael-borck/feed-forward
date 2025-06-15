---
layout: default
title: Student Invitations
parent: Instructor Guide
grand_parent: User Guides
nav_order: 4
---

# Student Invitation Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward uses an invitation-based system for student enrollment, ensuring only authorized students join your courses. This guide covers individual invitations, bulk CSV uploads, managing invitations, and troubleshooting common enrollment issues.

## Understanding the Invitation System

### Why Invitation-Based Enrollment?

1. **Security** - Only authorized students can join
2. **Privacy** - No public course listings
3. **Control** - Instructors manage enrollment
4. **Verification** - Email verification required
5. **Tracking** - Monitor who has joined

### Invitation Workflow

```
1. Instructor sends invitation
   ↓
2. Student receives email
   ↓
3. Student clicks invitation link
   ↓
4. Student creates account (if needed)
   ↓
5. Student joins course automatically
   ↓
6. Student can access assignments
```

## Individual Invitations

### Sending Single Invitations

1. **Navigate to Your Course**
2. Click **"Students"** → **"Invite Students"**
3. Select **"Individual Invitation"**

```yaml
Invitation Form:
  Student Email: student@university.edu
  
  Optional Fields:
    First Name: Jane
    Last Name: Smith
    Student ID: 12345678
  
  Message Customization:
    Use Default: Yes
    Or Custom Message: |
      Welcome to ENGL101! I'm looking forward
      to working with you this semester.
  
  Options:
    Send Copy to Self: Yes
    Expiration: 14 days
```

### Invitation Email Template

Students receive:

```
Subject: Invitation to join Introduction to Academic Writing

Dear [Student Name],

You have been invited to join the following course on FeedForward:

Course: Introduction to Academic Writing (ENGL101)
Instructor: Dr. Jane Smith
Term: Fall 2024

Click here to accept this invitation: [ACCEPT INVITATION]

This invitation will expire in 14 days.

If you already have a FeedForward account, you'll be added to 
the course immediately. Otherwise, you'll be prompted to create 
an account first.

Questions? Contact your instructor at jsmith@university.edu

Best regards,
The FeedForward Team
```

## Bulk CSV Upload

### Preparing Your CSV File

#### Download Template

1. Go to **"Students"** → **"Invite Students"**
2. Click **"Bulk Upload"**
3. Download **"CSV Template"**

#### CSV Format

```csv
email,first_name,last_name,student_id
jdoe@university.edu,John,Doe,12345678
asmith@university.edu,Alice,Smith,12345679
bwilson@university.edu,Bob,Wilson,12345680
cjohnson@university.edu,Carol,Johnson,12345681
```

#### CSV Requirements

- **Required**: email column
- **Optional**: first_name, last_name, student_id
- **Format**: UTF-8 encoding
- **Headers**: Must match exactly
- **Limit**: 500 students per upload

### Uploading the CSV

1. **Select Your File**
   - Click "Choose File"
   - Select your prepared CSV
   - Maximum size: 5MB

2. **Preview Import**
   ```
   Import Preview:
   ┌─────┬──────────────────┬────────────┬───────────┐
   │ Row │ Email            │ Name       │ Status    │
   ├─────┼──────────────────┼────────────┼───────────┤
   │ 1   │ jdoe@univ.edu   │ John Doe   │ ✓ Valid   │
   │ 2   │ asmith@univ.edu │ Alice Smith│ ✓ Valid   │
   │ 3   │ invalid-email   │ Bob Wilson │ ✗ Invalid │
   └─────┴──────────────────┴────────────┴───────────┘
   
   Valid: 2 | Invalid: 1 | Duplicates: 0
   ```

3. **Review and Confirm**
   - Check for errors
   - Fix invalid entries
   - Confirm upload

4. **Process Invitations**
   - System sends emails
   - Track progress
   - View results

### Handling CSV Errors

Common issues and solutions:

#### Invalid Email Addresses
```
Error: "invalid-email" is not a valid email address
Fix: Correct the email format (user@domain.com)
```

#### Duplicate Entries
```
Error: "jdoe@university.edu" appears multiple times
Fix: Remove duplicates, keep only one entry
```

#### Missing Required Fields
```
Error: Row 5 missing email address
Fix: Add email or remove the row
```

#### Encoding Issues
```
Error: Unable to parse CSV file
Fix: Save as UTF-8 without BOM
```

## Managing Invitations

### Invitation Dashboard

View all invitations at a glance:

```
Invitation Status Overview:
┌────────────┬────────┬──────────────┬─────────────┐
│ Status     │ Count  │ Last Action  │ Actions     │
├────────────┼────────┼──────────────┼─────────────┤
│ Pending    │ 15     │ 2 hours ago  │ Resend All  │
│ Accepted   │ 45     │ 1 hour ago   │ View        │
│ Expired    │ 3      │ 3 days ago   │ Reinvite    │
│ Declined   │ 0      │ -            │ -           │
└────────────┴────────┴──────────────┴─────────────┘
```

### Invitation Actions

#### Resending Invitations

For pending invitations:

1. **Individual Resend**
   - Find student in list
   - Click "Resend"
   - Confirm action

2. **Bulk Resend**
   - Select multiple students
   - Click "Resend Selected"
   - Or "Resend All Pending"

#### Canceling Invitations

Remove unwanted invitations:

1. Select invitation(s)
2. Click "Cancel"
3. Confirm cancellation
4. Student cannot use link

#### Extending Expiration

For invitations about to expire:

1. **Individual Extension**
   - Click "Extend"
   - Add days (max 30)
   - Save changes

2. **Bulk Extension**
   - Filter by "Expiring Soon"
   - Select all
   - Extend by X days

### Tracking Acceptance

Monitor who has joined:

```yaml
Acceptance Metrics:
  Total Invited: 50
  Accepted: 45 (90%)
  Pending: 3 (6%)
  Expired: 2 (4%)
  
  Average Time to Accept: 4.5 hours
  Fastest: 12 minutes
  Slowest: 3 days
```

## Advanced Invitation Features

### Custom Invitation Messages

Personalize your invitations:

1. **Create Template**
   ```
   Subject: Welcome to [COURSE_NAME]!
   
   Dear [STUDENT_NAME],
   
   I'm excited to have you in [COURSE_CODE] this semester.
   
   Our first assignment will be available on [DATE].
   Please join the course by [DEADLINE] to ensure
   you don't miss any important information.
   
   Looking forward to working with you!
   
   Best,
   [INSTRUCTOR_NAME]
   ```

2. **Use Variables**
   - [STUDENT_NAME]
   - [COURSE_NAME]
   - [COURSE_CODE]
   - [INSTRUCTOR_NAME]
   - [DEADLINE]
   - [CUSTOM_FIELD]

### Invitation Groups

Organize large classes:

1. **Create Groups**
   - Lab Section A
   - Lab Section B
   - Tuesday Discussion
   - Thursday Discussion

2. **Assign to Groups**
   - During CSV upload
   - After acceptance
   - Bulk assignment

3. **Group Features**
   - Separate announcements
   - Different due dates
   - Section-specific content

### Waitlist Management

Handle course capacity:

```yaml
Waitlist Settings:
  Enable Waitlist: Yes
  Waitlist Capacity: 10
  Auto-Promote: Yes
  
  Notification Settings:
    Notify When Space Opens: Yes
    Give Response Time: 48 hours
    Auto-Cancel if No Response: Yes
```

## Integration with External Systems

### LMS Integration

Sync with your Learning Management System:

1. **Export from LMS**
   - Download roster
   - Format as CSV
   - Include email addresses

2. **Import to FeedForward**
   - Use bulk upload
   - Map fields correctly
   - Process invitations

### Student Information System

Connect with institutional systems:

```yaml
SIS Integration:
  Import Method: API/CSV
  Sync Frequency: Daily
  
  Field Mapping:
    SIS_Email → email
    SIS_FirstName → first_name
    SIS_LastName → last_name
    SIS_ID → student_id
  
  Conflict Resolution:
    Use SIS Data: Yes
    Notify on Changes: Yes
```

## Communication Best Practices

### Before Sending Invitations

1. **Prepare Students**
   - Announce in class
   - Explain FeedForward
   - Set expectations
   - Provide timeline

2. **Check Email Lists**
   - Verify addresses
   - Remove duplicates
   - Confirm enrollment

### Invitation Timing

Optimal invitation schedule:

```yaml
Recommended Timeline:
  Week -1: Send initial invitations
  Week 1, Day 1: First reminder
  Week 1, Day 3: Second reminder
  Week 1, Day 5: Final reminder
  Week 2: Individual follow-up
```

### Follow-Up Strategies

For non-responders:

1. **Email Reminders**
   - Automated resends
   - Personal messages
   - CC academic advisor

2. **In-Class Reminders**
   - Verbal announcements
   - Show accept process
   - Offer help session

3. **Alternative Contact**
   - Phone calls
   - Office hours
   - Peer assistance

## Troubleshooting

### Common Student Issues

**"I didn't receive the invitation"**
1. Check spam/junk folders
2. Verify email address
3. Resend invitation
4. Send to alternate email

**"The link doesn't work"**
1. Check if expired
2. Verify student email
3. Cancel and recreate
4. Provide direct link

**"I can't create an account"**
1. Check password requirements
2. Verify email not taken
3. Clear browser cache
4. Try different browser

**"I accepted but can't see the course"**
1. Verify acceptance completed
2. Check course status
3. Have student log out/in
4. Manually add if needed

### System Issues

**Bulk upload fails**
- Check CSV format
- Verify file size < 5MB
- Remove special characters
- Try smaller batches

**Emails not sending**
- Check system status
- Verify email configuration
- Contact administrator
- Use manual process

## Privacy and Security

### Student Data Protection

1. **Minimal Information**
   - Only collect necessary data
   - Email required, rest optional
   - No sensitive information

2. **Secure Transmission**
   - Encrypted invitation links
   - HTTPS required
   - Time-limited access

3. **Access Control**
   - Only instructor can invite
   - Students can't share links
   - One-time use tokens

### FERPA Compliance

Maintain educational privacy:

- Don't share student emails
- Keep rosters confidential
- Secure CSV files
- Delete old invitations

## Best Practices Summary

### Do's
✅ Send invitations early in term
✅ Use bulk upload for large classes
✅ Follow up with non-responders
✅ Keep invitation lists organized
✅ Communicate clearly about the process

### Don'ts
❌ Wait until assignments are due
❌ Share invitation links publicly
❌ Upload sensitive student data
❌ Ignore failed invitations
❌ Assume all students received emails

## Next Steps

- Learn about [Feedback Review](./feedback-review)
- Explore [Analytics](./analytics)
- Return to [Instructor Overview](./index)

---

{: .tip }
> Set up a reminder system for yourself to check invitation status regularly during the first two weeks of class.

{: .note }
> Students who join late can still access all previous assignment feedback, making the invitation system flexible for add/drop periods.