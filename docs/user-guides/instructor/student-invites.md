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

FeedForward uses an invitation-based system for student enrollment, ensuring only authorized students join your courses. When you invite students, the system creates a personal **join link** for each student, which you distribute through your own channel — an LMS announcement, a cohort email, or in class. This guide covers individual invitations, bulk CSV uploads, distributing join links, and troubleshooting common enrollment issues.

## Understanding the Invitation System

### Why Invitation-Based Enrollment?

1. **Security** - Only authorized students can join
2. **Privacy** - No public course listings
3. **Control** - Instructors manage enrollment
4. **Simplicity** - Students activate with one personal link
5. **Tracking** - Monitor who has joined

### Invitation Workflow

```
1. Instructor enters student emails (paste or CSV)
   ↓
2. System creates an account and a personal join link
   for each student
   ↓
3. Join links appear on-screen for the instructor
   (with a copy-all option)
   ↓
4. Instructor distributes the links via their own
   channel (LMS announcement, cohort email)
   ↓
5. Student opens their link and activates their account
   ↓
6. Student joins the course and can access assignments
```

{: .important }
> FeedForward never emails students. You are always the one who delivers each student's join link, through whatever channel your institution already uses.

## Individual Invitations

### Inviting a Single Student

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
```

4. Click **"Create Invitation"**

The system creates the student's account and displays their personal join link on-screen. Copy the link and send it to the student yourself — for example, in a direct message or email from your own account.

### What the Student Sees

When the student opens their join link, they are taken to an activation page where they:

1. Confirm their name
2. Set a password
3. Land directly in your course

If the student already has a FeedForward account, the link enrolls them in your course immediately.

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

4. **Collect the Join Links**
   - System creates accounts and generates a personal join link per student
   - Links appear on-screen next to each student
   - Use **"Copy All"** to grab the full list at once

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

## Distributing Join Links

### Copying the Links

After inviting students, the join links are shown on-screen:

1. **Copy All**
   - Click **"Copy All"** to copy every student's email and personal link
   - Paste into a spreadsheet, mail merge, or LMS message

2. **Copy Individually**
   - Click the copy icon next to a single student
   - Useful for late enrollers or one-off invitations

### Recommended Distribution Channels

1. **LMS Announcement or Message**
   - Post a course announcement explaining FeedForward
   - Send each student their own link via the LMS message tool
   - Most students already check the LMS daily

2. **Cohort Email**
   - Use your institutional email or a mail merge
   - Include the student's personal link in each message
   - Add context: what FeedForward is and when to join by

3. **In-Class Handout**
   - For small classes, walk through activation together
   - Have links ready before the session

{: .warning }
> Each join link is personal to one student. Do not post links in a shared location where students could pick up the wrong one.

## Managing Enrollment

### Course Students Page

View all invited and enrolled students at a glance:

```
Enrollment Status Overview:
┌────────────┬────────┬──────────────┬─────────────┐
│ Status     │ Count  │ Last Action  │ Actions     │
├────────────┼────────┼──────────────┼─────────────┤
│ Invited    │ 15     │ 2 hours ago  │ Get link    │
│ Active     │ 45     │ 1 hour ago   │ View        │
│ Removed    │ 2      │ 3 days ago   │ Re-invite   │
└────────────┴────────┴──────────────┴─────────────┘
```

### Retrieving a Join Link

If you need a student's link again — because they lost it or you didn't record it:

1. Go to your course's **Students** page
2. Find the student in the list
3. Click **"Get link"**
4. Copy the link and send it to the student

You can retrieve a student's link as many times as needed; it always points to the same personal invitation.

### Removing Students

Remove students who should no longer have access:

1. Select the student(s)
2. Click **"Remove"**
3. Confirm removal
4. Their join link no longer grants access to the course

### Tracking Activation

Monitor who has joined:

```yaml
Activation Metrics:
  Total Invited: 50
  Activated: 45 (90%)
  Not Yet Joined: 5 (10%)

  Average Time to Activate: 4.5 hours
  Fastest: 12 minutes
  Slowest: 3 days
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
   - Copy the generated join links

3. **Distribute via LMS**
   - Send each student their link through LMS messaging
   - Or post an announcement directing students to check their messages

### Student Information System

Connect with institutional systems:

```yaml
SIS Integration:
  Import Method: CSV export from SIS
  Sync Frequency: Start of term + add/drop period

  Field Mapping:
    SIS_Email → email
    SIS_FirstName → first_name
    SIS_LastName → last_name
    SIS_ID → student_id
```

## Communication Best Practices

### Before Distributing Links

1. **Prepare Students**
   - Announce in class
   - Explain FeedForward
   - Set expectations
   - Provide timeline

2. **Check Email Lists**
   - Verify addresses
   - Remove duplicates
   - Confirm enrollment

### Distribution Timing

Optimal enrollment schedule:

```yaml
Recommended Timeline:
  Week -1: Create invitations and distribute links
  Week 1, Day 1: First reminder in class / LMS
  Week 1, Day 3: Follow up with students who haven't joined
  Week 2: Individual follow-up (re-send links via "Get link")
```

### Follow-Up Strategies

For students who haven't activated:

1. **Re-Send Their Link**
   - Use **"Get link"** on the course students page
   - Send via LMS message or direct email
   - CC academic advisor if needed

2. **In-Class Reminders**
   - Verbal announcements
   - Demonstrate the activation process
   - Offer help session

3. **Alternative Contact**
   - Phone calls
   - Office hours
   - Peer assistance

## Troubleshooting

### Common Student Issues

**"I lost my join link"**
1. Go to your course's **Students** page
2. Find the student and click **"Get link"**
3. Copy the link and send it to the student again

**"A student opened someone else's link"**
1. Join links are unique to each student — don't swap them
2. Ask the student to close the page without activating
3. Use **"Get link"** to retrieve the correct link for each student
4. Send each student their own link

**"The link doesn't work"**
1. Check the full URL was copied (links can break across line wraps)
2. Verify the student is still on the course roster
3. Retrieve a fresh copy via **"Get link"**

**"I can't create an account"**
1. Check password requirements
2. Clear browser cache
3. Try different browser

**"I activated but can't see the course"**
1. Verify activation completed
2. Check course status is Active
3. Have student log out/in

### System Issues

**Bulk upload fails**
- Check CSV format
- Verify file size < 5MB
- Remove special characters
- Try smaller batches

**Join links not appearing**
- Refresh the course students page
- Verify the upload completed
- Contact administrator if links are still missing

## Privacy and Security

### Student Data Protection

1. **Minimal Information**
   - Only collect necessary data
   - Email required, rest optional
   - No sensitive information

2. **Secure Links**
   - Unique, unguessable tokens per student
   - HTTPS required
   - Links tied to a single account

3. **Access Control**
   - Only instructor can invite
   - Links are personal — one per student
   - Removed students lose access

### FERPA Compliance

Maintain educational privacy:

- Don't share student emails
- Keep rosters confidential
- Secure CSV files
- Send each link only to its student

## Best Practices Summary

### Do's
✅ Create invitations early in term
✅ Use bulk upload for large classes
✅ Distribute links through your LMS
✅ Follow up with students who haven't joined
✅ Communicate clearly about the process

### Don'ts
❌ Wait until assignments are due
❌ Post join links in shared/public spaces
❌ Swap links between students
❌ Upload sensitive student data
❌ Assume all students saw your announcement

## Next Steps

- Learn about [Feedback Review](./feedback-review)
- Explore [Analytics](./analytics)
- Return to [Instructor Overview](./index)

---

{: .tip }
> Set up a reminder for yourself to check activation status on the course students page during the first two weeks of class, and re-send links with "Get link" as needed.

{: .note }
> Students who join late can still access all previous assignment feedback, making the invitation system flexible for add/drop periods.
