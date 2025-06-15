---
layout: default
title: API Reference
parent: Technical Documentation
nav_order: 3
---

# API Reference
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward's API is built with FastHTML, providing server-side rendered HTML with HTMX for dynamic updates. While not a traditional REST API, the endpoints follow RESTful conventions where appropriate. All endpoints return HTML responses unless otherwise noted.

## Authentication

### Session Management

FeedForward uses session-based authentication with secure cookies:

```python
# Session cookie configuration
SESSION_COOKIE_NAME = "feedforward_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only in production
SESSION_COOKIE_SAMESITE = "Lax"
```

### Authentication Flow

```
1. User submits login credentials
2. Server validates and creates session
3. Session cookie set with user email
4. Subsequent requests include cookie
5. Decorators check session['auth'] for access
```

### Role-Based Access Control

Three authorization decorators protect endpoints:

```python
@admin_required     # Admins only
@instructor_required # Instructors (verified + approved)
@student_required   # Students only
```

## Public Endpoints

### Authentication Routes

#### POST /register
Create new instructor account.

**Request Body:**
```
name: string (required)
email: string (required, valid email)
password: string (required, min 8 chars)
confirm_password: string (required, must match)
tos_accepted: boolean (required, must be true)
privacy_accepted: boolean (required, must be true)
```

**Response:**
- Success: Redirect to `/register/confirmation`
- Error: Form with validation messages

**Notes:**
- Students cannot self-register
- Domain whitelist may auto-approve instructors
- Email verification required

---

#### POST /login
Authenticate user and create session.

**Request Body:**
```
email: string (required)
password: string (required)
```

**Response:**
- Success: Redirect to role-specific dashboard
- Error: Form with "Invalid credentials"

---

#### GET /verify
Verify email address with token.

**Query Parameters:**
```
token: string (required, verification token)
```

**Response:**
- Success: Redirect to login with success message
- Error: Error page with invalid token message

---

#### POST /forgot-password
Request password reset email.

**Request Body:**
```
email: string (required)
```

**Response:**
- Always shows success message (security)
- Email sent if account exists

---

#### POST /reset-password
Reset password with token.

**Request Body:**
```
token: string (required, from email)
email: string (required)
password: string (required, min 8 chars)
confirm_password: string (required)
```

**Response:**
- Success: Redirect to login
- Error: Form with validation messages

### Legal Routes

#### GET /terms-of-service
Display current Terms of Service.

**Response:** HTML page with ToS content

---

#### GET /privacy-policy
Display current Privacy Policy.

**Response:** HTML page with privacy policy

## Admin Endpoints

All admin endpoints require `@admin_required` decorator.

### Dashboard

#### GET /admin/dashboard
Admin dashboard with system overview.

**Response Data:**
- Total users by role
- Pending instructor approvals
- System health metrics
- Recent activity

### Instructor Management

#### GET /admin/instructors/approve
View pending instructor approvals.

**Response:** List of unverified/unapproved instructors

---

#### POST /admin/instructors/approve/{email}
Approve instructor account.

**Path Parameters:**
```
email: string (instructor email)
```

**Response:** Redirect with success message

---

#### POST /admin/instructors/reject/{email}
Reject instructor account.

**Path Parameters:**
```
email: string (instructor email)
```

**Response:** Redirect with success message

---

#### GET /admin/instructors
Manage all instructor accounts.

**Response:** Table of all instructors with actions

---

#### POST /admin/instructors/remove/{email}
Soft delete instructor account.

**Path Parameters:**
```
email: string (instructor email)
```

**Response:** Redirect with success message

### Domain Management

#### GET /admin/domains
Manage email domain whitelist.

**Response:** List of whitelisted domains

---

#### POST /admin/domains/add
Add domain to whitelist.

**Request Body:**
```
domain: string (required, e.g., "university.edu")
auto_approve: boolean (auto-approve instructors)
```

**Response:** Redirect with success/error message

---

#### POST /admin/domains/toggle/{id}
Toggle auto-approve for domain.

**Path Parameters:**
```
id: integer (domain ID)
```

**Response:** Redirect with success message

### AI Model Management

#### GET /admin/ai-models
View all system AI models.

**Response:** List of configured AI models

---

#### POST /admin/ai-models/create
Create new AI model configuration.

**Request Body:**
```
name: string (required)
provider: string (required, e.g., "openai")
model_id: string (required, e.g., "gpt-4")
api_key: string (required for most providers)
base_url: string (optional, custom endpoint)
capabilities: array (optional, ["text", "vision"])
max_context: integer (optional, token limit)
```

**Response:** Redirect to models list or form with errors

---

#### POST /admin/ai-models/test
Test AI model connection.

**Request Body:**
```
provider: string (required)
api_key: string (required)
base_url: string (optional)
```

**Response:** JSON with test results
```json
{
  "success": true,
  "message": "Connection successful",
  "models": ["gpt-4", "gpt-3.5-turbo"]
}
```

---

#### DELETE /admin/ai-models/{id}
Delete AI model configuration.

**Path Parameters:**
```
id: integer (model ID)
```

**Response:** 200 OK or error status

## Instructor Endpoints

All instructor endpoints require `@instructor_required` decorator.

### Dashboard

#### GET /instructor/dashboard
Instructor dashboard overview.

**Response Data:**
- Active courses
- Recent submissions
- Pending feedback reviews
- Student activity

### Course Management

#### GET /instructor/courses
View all instructor's courses.

**Query Parameters:**
```
status: string (optional, filter by status)
```

**Response:** List of courses with management actions

---

#### POST /instructor/courses/new
Create new course.

**Request Body:**
```
code: string (required, e.g., "CS101")
title: string (required)
description: string (optional)
term: string (optional, e.g., "Fall 2024")
```

**Response:** Redirect to course page or form with errors

---

#### POST /instructor/courses/{course_id}/edit
Update course details.

**Path Parameters:**
```
course_id: integer
```

**Request Body:**
```
title: string
description: string
status: string (active, closed, archived)
```

**Response:** Redirect with success message

### Assignment Management

#### GET /instructor/courses/{course_id}/assignments
View course assignments.

**Path Parameters:**
```
course_id: integer
```

**Response:** List of assignments with actions

---

#### POST /instructor/courses/{course_id}/assignments/new
Create new assignment.

**Path Parameters:**
```
course_id: integer
```

**Request Body:**
```
title: string (required)
description: string (required)
due_date: datetime (required)
max_drafts: integer (default: 3)
```

**Response:** Redirect to assignment or form with errors

---

#### POST /instructor/assignments/{assignment_id}/status
Toggle assignment status (active/inactive).

**Path Parameters:**
```
assignment_id: integer
```

**Response:** Redirect with status update

### Rubric Management

#### POST /instructor/assignments/{assignment_id}/rubric/create
Create assignment rubric.

**Path Parameters:**
```
assignment_id: integer
```

**Response:** Redirect to rubric management

---

#### POST /instructor/assignments/{assignment_id}/rubric/categories/add
Add rubric category.

**Path Parameters:**
```
assignment_id: integer
```

**Request Body:**
```
name: string (required)
description: string (optional)
weight: float (required, 0-1)
```

**Response:** HTML partial for HTMX update

---

#### GET /instructor/assignments/{assignment_id}/rubric/template/{template_type}
Get rubric template structure.

**Path Parameters:**
```
assignment_id: integer
template_type: string (essay, report, presentation, creative)
```

**Response:** JSON with template structure
```json
{
  "categories": [
    {
      "name": "Thesis Statement",
      "description": "Clear and arguable thesis",
      "weight": 0.2
    }
  ]
}
```

### Student Management

#### GET /instructor/courses/{course_id}/students
View course students.

**Path Parameters:**
```
course_id: integer
```

**Response:** Student roster with management actions

---

#### POST /instructor/invite-students
Send student invitations.

**Request Body:**
```
course_id: integer (required)
emails: string (required, comma-separated)
```

**Response:** Success/error messages for each email

---

#### POST /instructor/remove-student
Remove student from course.

**Request Body:**
```
student_email: string (required)
course_id: integer (required)
```

**Response:** Redirect with success message

### Feedback Review

#### GET /instructor/assignments/{assignment_id}/feedback
View all submissions for assignment.

**Path Parameters:**
```
assignment_id: integer
```

**Query Parameters:**
```
status: string (optional, filter by feedback status)
```

**Response:** List of submissions grouped by status

---

#### GET /instructor/drafts/{draft_id}/review
Review AI-generated feedback.

**Path Parameters:**
```
draft_id: integer
```

**Response:** Feedback review interface

---

#### POST /instructor/drafts/{draft_id}/review
Approve or edit feedback.

**Path Parameters:**
```
draft_id: integer
```

**Request Body:**
```
action: string (required, "approve" or "save_edits")
category_{id}_score: float (for each category)
category_{id}_feedback: string (for each category)
instructor_notes: string (optional)
```

**Response:** Redirect with success message

## Student Endpoints

All student endpoints require `@student_required` decorator.

### Registration

#### POST /student/join
Complete student registration from invitation.

**Request Body:**
```
token: string (required, from invitation)
email: string (required)
name: string (required)
password: string (required, min 8 chars)
confirm_password: string (required)
tos_accepted: boolean (required)
privacy_accepted: boolean (required)
```

**Response:** Redirect to dashboard or form with errors

### Dashboard

#### GET /student/dashboard
Student dashboard overview.

**Response Data:**
- Enrolled courses
- Recent feedback
- Upcoming assignments
- Submission statistics

### Course Access

#### GET /student/courses/{course_id}
View course details.

**Path Parameters:**
```
course_id: integer
```

**Response:** Course information and assignments

---

#### GET /student/courses/{course_id}/assignments
View course assignments.

**Path Parameters:**
```
course_id: integer
```

**Response:** List of available assignments

### Assignment Submission

#### GET /student/assignments/{assignment_id}
View assignment details.

**Path Parameters:**
```
assignment_id: integer
```

**Response:** Assignment info, rubric, submission status

---

#### POST /student/assignments/{assignment_id}/submit
Submit draft for feedback.

**Path Parameters:**
```
assignment_id: integer
```

**Request Body (multipart/form-data):**
```
submission_method: string ("text" or "file")
content: string (if method="text")
file: file (if method="file", PDF/DOCX/TXT)
version: integer (draft version)
```

**Response:** Redirect to feedback status page

### Feedback Access

#### GET /student/drafts/{draft_id}/feedback
View feedback for submitted draft.

**Path Parameters:**
```
draft_id: integer
```

**Response:** 
- If processing: Auto-refresh status page
- If ready: Detailed feedback report

---

#### GET /api/feedback-status/{draft_id}
Check feedback generation status (AJAX).

**Path Parameters:**
```
draft_id: integer
```

**Response:** JSON status
```json
{
  "status": "processing|ready|error",
  "message": "Feedback is being generated..."
}
```

### Submission Management

#### GET /student/submissions
View all submissions.

**Query Parameters:**
```
show_hidden: boolean (include hidden submissions)
```

**Response:** List of all drafts with actions

---

#### POST /student/submissions/hide/{draft_id}
Hide a submission from view.

**Path Parameters:**
```
draft_id: integer
```

**Response:** Redirect with success message

## Response Formats

### HTML Responses

Most endpoints return full HTML pages or HTMX partials:

```html
<!-- Full page response -->
<html>
  <head>...</head>
  <body>
    <div id="content">...</div>
  </body>
</html>

<!-- HTMX partial response -->
<div id="rubric-categories" hx-swap-oob="true">
  <div class="category">...</div>
</div>
```

### JSON Responses

Select endpoints return JSON for AJAX/API usage:

```json
{
  "success": true|false,
  "message": "Operation result",
  "data": { ... }
}
```

### Error Responses

Errors are typically shown in-page:

```html
<div class="error-message">
  <p>Error: Invalid input provided</p>
</div>
```

HTTP status codes:
- 200: Success
- 302: Redirect
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## HTMX Integration

Many endpoints support HTMX for dynamic updates:

```html
<!-- Example: Add rubric category -->
<button hx-post="/instructor/assignments/1/rubric/categories/add"
        hx-target="#categories"
        hx-swap="beforeend">
  Add Category
</button>

<!-- Example: Check feedback status -->
<div hx-get="/api/feedback-status/123"
     hx-trigger="every 5s"
     hx-swap="innerHTML">
  Checking status...
</div>
```

## Rate Limiting

API rate limits (configurable):

```yaml
Global Limits:
  Requests per minute: 60
  Burst allowance: 10

Per-Endpoint Limits:
  AI model testing: 10 per hour
  Draft submission: 5 per hour
  Feedback generation: 20 per day
```

## Security Considerations

1. **CSRF Protection**: All POST requests require valid session
2. **Input Validation**: Server-side validation on all inputs
3. **SQL Injection**: Parameterized queries via ORM
4. **XSS Prevention**: HTML escaping on all user content
5. **File Upload**: Type and size restrictions enforced
6. **Rate Limiting**: Prevents abuse and excessive API usage

---

{: .note }
> This API is designed for server-side rendered applications. For building separate frontends, consider adding dedicated JSON API endpoints.