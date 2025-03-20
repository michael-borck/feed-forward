# FeedForward Authentication Testing Guide

This guide outlines the steps to test the authentication flows in FeedForward.

## Prerequisites

- Python environment set up with required dependencies
- FeedForward codebase
- Database initialized with `python -m app.init_db`

## Automated Test Script

Run the automated test script to generate test data:

```bash
python tools/test_auth_flows.py
```

This will generate test users, verification links, and invitation links that you can use in the manual testing steps.

## Manual Testing Flows

### 1. Instructor Registration & Approval Flow

**Test: Auto-Approved Instructor**

1. Navigate to `/register`
2. Fill out the form with a curtin.edu.au email
3. Submit the form
4. Check for success message
5. Follow the verification link from the test script output
6. Verify the account is ready to use
7. Log in with the credentials

**Test: Non-Auto-Approved Instructor**

1. Navigate to `/register`
2. Fill out the form with a notre-dame.edu.au email
3. Submit the form
4. Check for success message (should mention approval needed)
5. Follow the verification link from the test script output
6. Verify the account shows "awaiting approval" message
7. Log in as admin (admin@example.com / Admin123!)
8. Navigate to `/admin/instructors/approve`
9. Approve the instructor
10. Log out and log in as the instructor

**Test: Unknown Domain Instructor**

1. Navigate to `/register`
2. Fill out the form with a unknown-university.edu email
3. Submit the form
4. Check for success message (should mention approval needed)
5. Follow the verification link from the test script output
6. Verify the account shows "awaiting approval" message
7. Log in as admin and approve the instructor

### 2. Student Invitation Flow

**Test: Student Invitation and Registration**

1. Log in as an instructor (use the test_instructor@curtin.edu.au account created by the test script)
2. Navigate to `/instructor/invite-students`
3. Select the test course
4. Enter student emails (one per line)
5. Submit the form
6. Copy the invitation links from the test script output
7. Open the invitation links in a new browser session
8. Complete student registration with name and password
9. Verify the student is automatically logged in and redirected to dashboard

### 3. Domain Whitelist Management

**Test: Admin Domain Management**

1. Log in as admin (admin@example.com / Admin123!)
2. Navigate to `/admin/domains`
3. Add a new domain (e.g., "example-university.edu")
4. Toggle auto-approval status
5. Delete a domain
6. Verify changes are reflected in the whitelist

## Full End-to-End Flow Test

1. Run the app: `python app.py`
2. Clear existing test data (optional): `cp data/users_backup.db data/users.db`
3. Reset the database with test data: `python -m app.init_db`
4. Register an instructor with a auto-approved domain
5. Verify the instructor's email
6. Log in as the instructor
7. Create a course
8. Invite students to the course
9. Access the student invitation links
10. Complete student registration
11. Log in as students
12. Verify all accounts have appropriate access

## Student Upload

For student assessment upload:

1. Students are invited by instructors to specific courses (not directly to assessments)
2. Instructors create assignments within courses
3. Students submit drafts to assignments
4. The system processes drafts with AI models to provide feedback

## Troubleshooting

- Check app logs for any errors
- Verify email links have the correct domain
- Make sure the database is properly initialized
- Ensure domain whitelist contains test domains

## Automated Testing Extension

Future work can enhance the test script to:
- Add Selenium-based UI testing
- Create automated API testing for authentication endpoints
- Implement integration tests for the full authentication flow