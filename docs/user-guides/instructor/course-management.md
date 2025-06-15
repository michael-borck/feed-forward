---
layout: default
title: Course Management
parent: Instructor Guide
grand_parent: User Guides
nav_order: 1
---

# Course Management Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Course management is the foundation of your FeedForward experience. This guide covers creating courses, managing course settings, organizing assignments, and handling the course lifecycle from creation to archival.

## Creating a New Course

### Step-by-Step Course Creation

1. **Access Course Creation**
   - From your dashboard, click **"Create New Course"**
   - Or navigate to **"My Courses"** → **"New Course"**

2. **Enter Basic Information**
   ```yaml
   Course Name: Introduction to Academic Writing
   Course Code: ENGL101
   Section: 001 (optional)
   Term: Fall 2024
   Credits: 3
   ```

3. **Add Course Details**
   ```yaml
   Description: |
     This course develops fundamental academic writing skills
     through iterative drafting and revision processes.
   
   Learning Objectives:
     - Develop clear thesis statements
     - Support arguments with evidence
     - Master academic citation formats
     - Improve through revision
   ```

4. **Configure Course Settings**
   ```yaml
   Status: Active
   Start Date: September 1, 2024
   End Date: December 15, 2024
   
   Student Settings:
     Max Enrollment: 30
     Self-Enrollment: Disabled
     Late Submissions: Allowed with penalty
   ```

5. **Save and Continue**
   - Click **"Create Course"**
   - You'll be redirected to the course dashboard

### Course Information Best Practices

#### Course Names
- Use clear, descriptive names
- Include level indicators (intro, advanced)
- Add section numbers for multiple sections
- Keep consistent naming conventions

#### Course Codes
- Follow institutional standards
- Include department prefix
- Add course number
- Specify section if needed

#### Descriptions
- Write student-facing descriptions
- Highlight key learning outcomes
- Mention technology use (AI feedback)
- Set clear expectations

## Course Dashboard

### Understanding Your Course Dashboard

The course dashboard is your command center:

```
[Course Name: ENGL101 - Introduction to Academic Writing]

Quick Stats:
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Students    │ Assignments │ Submissions │ Reviews     │
│ 24/30       │ 5 Active    │ 47 Total    │ 12 Pending  │
└─────────────┴─────────────┴─────────────┴─────────────┘

Navigation:
- Overview
- Assignments
- Students
- Analytics
- Settings
```

### Key Dashboard Sections

#### Overview Tab
- Course announcements
- Recent activity
- Upcoming due dates
- Quick actions

#### Assignments Tab
- List of all assignments
- Status indicators
- Quick edit options
- Submission counts

#### Students Tab
- Enrolled student list
- Invitation status
- Performance overview
- Communication tools

#### Analytics Tab
- Course-wide statistics
- Performance trends
- AI usage metrics
- Export options

## Managing Course Settings

### General Settings

Access via **Course** → **Settings** → **General**

```yaml
Course Information:
  Name: [Editable]
  Code: [Editable]
  Description: [Editable]
  
Display Options:
  Show in Dashboard: Yes
  Student View: Enabled
  Public Syllabus: No
  
Availability:
  Status: Active/Inactive/Archived
  Start Date: [Date picker]
  End Date: [Date picker]
```

### Enrollment Settings

Configure how students join your course:

```yaml
Enrollment Options:
  Method: Invitation Only
  Max Students: 30
  Waitlist: Enabled (5 spots)
  
Invitation Settings:
  Require Acceptance: Yes
  Expiration: 14 days
  Resend Allowed: Yes
  
Access Control:
  Late Enrollment: Allowed until Week 3
  Drop Deadline: Week 8
```

### Assignment Defaults

Set default values for new assignments:

```yaml
Default Settings:
  Draft Limit: 3
  File Types: PDF, DOCX, TXT
  Max File Size: 10 MB
  
AI Configuration:
  Default Models: GPT-4, Claude-3
  Runs per Model: 3
  Aggregation: Average
  
Feedback Settings:
  Require Review: Yes
  Auto-Release: No
  Show Scores: After approval
```

## Course Organization

### Using Course Modules

Organize assignments into logical units:

1. **Create Module**
   - Click **"Add Module"**
   - Name: "Unit 1: Essay Fundamentals"
   - Description: Optional
   - Date range: Optional

2. **Add Assignments to Modules**
   - Drag assignments into modules
   - Or select module when creating
   - Reorder as needed

3. **Module Settings**
   - Sequential unlock
   - Prerequisites
   - Completion requirements

### Course Calendar

Visualize your course timeline:

1. **Calendar View**
   - See all due dates
   - Add course events
   - Sync with institution calendar

2. **Bulk Date Management**
   - Shift all dates
   - Adjust for holidays
   - Copy from previous term

### Announcement System

Communicate with all students:

1. **Create Announcement**
   ```yaml
   Title: Week 5 Feedback Released
   Priority: Normal/High/Urgent
   
   Message: |
     Your Essay 2 feedback is now available.
     Please review and begin your revisions.
   
   Options:
     Email Students: Yes
     Pin to Top: No
     Schedule: Immediate
   ```

2. **Announcement Types**
   - General updates
   - Assignment reminders
   - Feedback notifications
   - Course changes

## Student Management

### Viewing Enrolled Students

Access via **Course** → **Students**

```
Student List View:
┌──────────────┬─────────────┬────────────┬─────────────┐
│ Name         │ Email       │ Status     │ Last Active │
├──────────────┼─────────────┼────────────┼─────────────┤
│ Jane Smith   │ js@edu      │ Active     │ 2 hours ago │
│ John Doe     │ jd@edu      │ Active     │ 1 day ago   │
│ Mary Johnson │ mj@edu      │ Invited    │ Never       │
└──────────────┴─────────────┴────────────┴─────────────┘
```

### Student Actions

For each student, you can:

1. **View Profile**
   - Submission history
   - Performance summary
   - Contact information

2. **Manage Access**
   - Temporary extensions
   - Special permissions
   - Remove from course

3. **Communicate**
   - Send direct message
   - View message history
   - Flag for attention

### Bulk Student Operations

Handle multiple students efficiently:

1. **Select Multiple Students**
2. **Choose Action:**
   - Send announcement
   - Grant extension
   - Export data
   - Remove from course

## Course Duplication

### Copying a Course

Reuse successful course structures:

1. **Find Source Course**
   - Go to **My Courses**
   - Click **"Duplicate"** option

2. **Select Copy Options**
   ```yaml
   Copy Settings:
     Course Information: Yes
     Assignments: Yes
     Rubrics: Yes
     Modules: Yes
     
   Exclude:
     Student Enrollments: Yes
     Submissions: Yes
     Announcements: Optional
   ```

3. **Configure New Course**
   - Update term/dates
   - Adjust assignments
   - Modify settings

### Import/Export

Transfer course content:

1. **Export Course**
   - Select components
   - Generate export file
   - Download archive

2. **Import Course**
   - Upload archive
   - Map components
   - Review and confirm

## Course Lifecycle

### Active Phase

During the active term:

- Regular assignment creation
- Student management
- Feedback review
- Progress monitoring

### End of Term

As the course concludes:

1. **Final Tasks**
   - Ensure all feedback reviewed
   - Export gradebook
   - Archive important data
   - Send final announcements

2. **Grade Export**
   - Generate final reports
   - Export to LMS/SIS
   - Create backups

### Archiving a Course

Preserve course for reference:

1. **Prepare for Archive**
   - Review all assignments
   - Export necessary data
   - Notify students

2. **Archive Process**
   - Go to **Settings** → **Archive Course**
   - Confirm understanding:
     - Course becomes read-only
     - Students retain view access
     - No new submissions
     - Data preserved

3. **Post-Archive**
   - Course moved to archives
   - Can be reactivated if needed
   - Data remains searchable

## Advanced Features

### Co-Instructor Management

Add teaching assistants or co-instructors:

1. **Add Co-Instructor**
   - Navigate to **Settings** → **Instructors**
   - Enter email address
   - Set permissions level

2. **Permission Levels**
   ```yaml
   Full Co-Instructor:
     - All course management
     - Student management
     - Settings access
   
   Teaching Assistant:
     - View submissions
     - Review feedback
     - Limited settings
   
   Grader:
     - Review feedback only
     - No settings access
   ```

### Integration Options

Connect with other systems:

1. **LMS Integration**
   - Sync rosters
   - Grade passback
   - Assignment links

2. **Calendar Sync**
   - Export to iCal
   - Google Calendar
   - Outlook integration

## Best Practices

### Course Setup
1. **Plan Ahead**
   - Create course early
   - Set up all assignments
   - Test configurations

2. **Clear Communication**
   - Detailed descriptions
   - Explicit expectations
   - Regular updates

3. **Consistent Structure**
   - Similar assignment formats
   - Regular due dates
   - Predictable patterns

### During the Term
1. **Stay Organized**
   - Use modules effectively
   - Keep calendar updated
   - Archive old announcements

2. **Monitor Progress**
   - Check analytics weekly
   - Address issues early
   - Adjust as needed

3. **Maintain Engagement**
   - Regular announcements
   - Timely feedback
   - Respond to questions

## Troubleshooting

### Common Issues

**Students Can't Access Course**
- Check enrollment status
- Verify course is active
- Resend invitations
- Check spam folders

**Assignment Not Visible**
- Verify publication status
- Check date restrictions
- Review module requirements
- Test student view

**Performance Issues**
- Large class sizes
- Too many assignments
- Archive old content
- Contact support

## Next Steps

- Learn about [Creating Assignments](./assignments)
- Master [Rubric Design](./rubrics)
- Understand [Student Invitations](./student-invites)

---

{: .tip }
> Use the course duplication feature to save time when teaching multiple sections or repeating courses across terms.