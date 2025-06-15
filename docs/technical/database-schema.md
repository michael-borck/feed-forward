---
layout: default
title: Database Schema
parent: Technical Documentation
nav_order: 2
---

# Database Schema Reference
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward uses SQLite as its database engine with FastLite as the ORM layer. The schema is designed around educational workflows with a focus on data privacy, soft deletion patterns, and clear hierarchical relationships between instructors, courses, assignments, and students.

## Database Configuration

```yaml
Database Engine: SQLite 3
Database File: data/users.db
ORM: FastLite (FastHTML's database layer)
Connection Management: Connection pooling with WAL mode
Backup Strategy: Daily snapshots with 30-day retention
```

## Schema Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   users     │         │   courses   │         │ assignments │
│─────────────│         │─────────────│         │─────────────│
│ email (PK)  │←────────│instructor_  │         │ id (PK)     │
│ name        │         │   email(FK) │←────────│ course_id   │
│ role        │         │ id (PK)     │         │   (FK)      │
│ status      │         │ code        │         │ title       │
└─────────────┘         │ title       │         │ status      │
       ↑                └─────────────┘         └─────────────┘
       │                       ↑                        ↑
       │                       │                        │
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ enrollments │         │   drafts    │         │  rubrics    │
│─────────────│         │─────────────│         │─────────────│
│ id (PK)     │         │ id (PK)     │         │ id (PK)     │
│ course_id   │         │ assignment_ │         │ assignment_ │
│   (FK)      │         │   id (FK)   │         │   id (FK)   │
│ student_    │         │ student_    │         └─────────────┘
│   email(FK) │         │   email(FK) │                ↑
└─────────────┘         │ content     │                │
                        │ status      │         ┌─────────────┐
                        └─────────────┘         │   rubric_   │
                               ↑                │ categories  │
                               │                │─────────────│
                        ┌─────────────┐         │ id (PK)     │
                        │ model_runs  │         │ rubric_id   │
                        │─────────────│         │   (FK)      │
                        │ id (PK)     │         │ name        │
                        │ draft_id    │         │ weight      │
                        │   (FK)      │         └─────────────┘
                        │ model_id    │
                        │   (FK)      │
                        └─────────────┘
```

## Core Tables

### users

Primary user table supporting three roles: ADMIN, INSTRUCTOR, and STUDENT.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| email | str | PRIMARY KEY | User's email address |
| name | str | NOT NULL | User's full name |
| password | str | NOT NULL | Bcrypt hashed password |
| role | str | NOT NULL | STUDENT, INSTRUCTOR, or ADMIN |
| verified | bool | DEFAULT false | Email verification status |
| verification_token | str | | Token for email verification |
| approved | bool | DEFAULT false | Admin approval status |
| department | str | | User's department |
| reset_token | str | | Password reset token |
| reset_token_expiry | str | | Token expiration (ISO timestamp) |
| status | str | DEFAULT 'active' | active, inactive, archived, deleted |
| last_active | str | | Last activity timestamp |
| tos_accepted | bool | DEFAULT false | Terms of Service acceptance |
| privacy_accepted | bool | DEFAULT false | Privacy Policy acceptance |
| acceptance_date | str | | ToS/Privacy acceptance timestamp |

**Indexes:**
- PRIMARY KEY: email
- INDEX: role, status
- INDEX: verification_token
- INDEX: reset_token

### courses

Stores course information managed by instructors.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| code | str | NOT NULL | Course code (e.g., CS101) |
| title | str | NOT NULL | Course title |
| term | str | | Academic term |
| department | str | | Department offering course |
| instructor_email | str | FOREIGN KEY | References users.email |
| status | str | DEFAULT 'active' | active, closed, archived, deleted |
| created_at | str | | Creation timestamp |
| updated_at | str | | Last update timestamp |

**Indexes:**
- PRIMARY KEY: id
- INDEX: instructor_email
- INDEX: status
- UNIQUE: code, term, instructor_email

### assignments

Stores assignment details within courses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| course_id | int | FOREIGN KEY | References courses.id |
| title | str | NOT NULL | Assignment title |
| description | str | | Assignment instructions |
| due_date | str | | Due date (ISO format) |
| max_drafts | int | DEFAULT 3 | Maximum draft submissions |
| created_by | str | FOREIGN KEY | Instructor email |
| status | str | DEFAULT 'draft' | draft, active, closed, archived, deleted |
| created_at | str | | Creation timestamp |
| updated_at | str | | Last update timestamp |

**Indexes:**
- PRIMARY KEY: id
- INDEX: course_id, status
- INDEX: due_date

## Student Data Tables

### enrollments

Junction table linking students to courses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| course_id | int | FOREIGN KEY | References courses.id |
| student_email | str | FOREIGN KEY | References users.email |

**Indexes:**
- PRIMARY KEY: id
- UNIQUE: course_id, student_email

### drafts

Stores student draft submissions with privacy-focused design.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| assignment_id | int | FOREIGN KEY | References assignments.id |
| student_email | str | FOREIGN KEY | References users.email |
| version | int | NOT NULL | Draft version number |
| content | str | | Draft content (temporarily stored) |
| content_preserved | bool | DEFAULT false | Flag to preserve content |
| submission_date | str | | Submission timestamp |
| word_count | int | | Word count for statistics |
| status | str | DEFAULT 'submitted' | submitted, processing, feedback_ready, archived |
| content_removed_date | str | | When content was removed |
| hidden_by_student | bool | DEFAULT false | Soft delete by student |

**Indexes:**
- PRIMARY KEY: id
- INDEX: assignment_id, student_email
- INDEX: status
- UNIQUE: assignment_id, student_email, version

## Rubric Tables

### rubrics

Main rubric configuration per assignment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| assignment_id | int | FOREIGN KEY | References assignments.id |

**Indexes:**
- PRIMARY KEY: id
- UNIQUE: assignment_id

### rubric_categories

Individual rubric evaluation categories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| rubric_id | int | FOREIGN KEY | References rubrics.id |
| name | str | NOT NULL | Category name |
| description | str | | Category description |
| weight | float | NOT NULL | Category weight (0-1) |

**Indexes:**
- PRIMARY KEY: id
- INDEX: rubric_id

## AI Configuration Tables

### ai_models

Stores AI model configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | str | NOT NULL | Display name |
| provider | str | NOT NULL | OpenAI, Anthropic, Ollama, etc |
| model_id | str | NOT NULL | Model identifier (gpt-4, claude-3) |
| model_version | str | | Model version |
| description | str | | Model description |
| api_config | str | | JSON configuration |
| owner_type | str | DEFAULT 'system' | system or instructor |
| owner_id | str/int | | Owner identifier |
| capabilities | str | | JSON array of capabilities |
| max_context | int | | Maximum context length |
| active | bool | DEFAULT true | Model availability |
| created_at | str | | Creation timestamp |
| updated_at | str | | Last update timestamp |

**Indexes:**
- PRIMARY KEY: id
- INDEX: provider, active
- INDEX: owner_type, owner_id

### assignment_settings

Assignment-specific AI configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| assignment_id | int | FOREIGN KEY | References assignments.id |
| primary_ai_model_id | int | FOREIGN KEY | Primary model for aggregation |
| feedback_level | str | DEFAULT 'both' | overall, criterion, or both |
| num_runs | int | DEFAULT 3 | Number of AI runs |
| aggregation_method_id | int | FOREIGN KEY | Aggregation method |
| feedback_style_id | int | FOREIGN KEY | Feedback presentation style |
| require_review | bool | DEFAULT true | Instructor review required |
| mark_display_option_id | int | FOREIGN KEY | Score display option |

**Indexes:**
- PRIMARY KEY: id
- UNIQUE: assignment_id

### assignment_model_runs

Links AI models to assignments with run configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| assignment_setting_id | int | FOREIGN KEY | References assignment_settings.id |
| ai_model_id | int | FOREIGN KEY | References ai_models.id |
| num_runs | int | DEFAULT 3 | Runs for this model |

**Indexes:**
- PRIMARY KEY: id
- INDEX: assignment_setting_id

## Feedback Tables

### model_runs

Individual AI model execution records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| draft_id | int | FOREIGN KEY | References drafts.id |
| model_id | int | FOREIGN KEY | References ai_models.id |
| run_number | int | | Run sequence number |
| timestamp | str | | Execution timestamp |
| prompt | str | | Prompt used |
| raw_response | str | | Raw AI response |
| status | str | DEFAULT 'pending' | pending, complete, error |

**Indexes:**
- PRIMARY KEY: id
- INDEX: draft_id, status
- INDEX: model_id

### category_scores

Scores for each rubric category per model run.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| model_run_id | int | FOREIGN KEY | References model_runs.id |
| category_id | int | FOREIGN KEY | References rubric_categories.id |
| score | float | NOT NULL | Category score |
| confidence | float | | Score confidence (0-1) |

**Indexes:**
- PRIMARY KEY: id
- INDEX: model_run_id
- INDEX: category_id

### feedback_items

Individual feedback points from model runs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| model_run_id | int | FOREIGN KEY | References model_runs.id |
| category_id | int | FOREIGN KEY | References rubric_categories.id |
| type | str | NOT NULL | strength, improvement, general |
| content | str | NOT NULL | Feedback text |
| is_strength | bool | DEFAULT false | Positive feedback flag |
| is_aggregated | bool | DEFAULT false | Included in aggregation |

**Indexes:**
- PRIMARY KEY: id
- INDEX: model_run_id, category_id
- INDEX: type, is_aggregated

### aggregated_feedback

Final aggregated feedback for student viewing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| draft_id | int | FOREIGN KEY | References drafts.id |
| category_id | int | FOREIGN KEY | References rubric_categories.id |
| aggregated_score | float | NOT NULL | Final score |
| feedback_text | str | NOT NULL | Aggregated feedback |
| edited_by_instructor | bool | DEFAULT false | Instructor modified |
| instructor_email | str | | Editor's email |
| release_date | str | | When released to student |
| status | str | DEFAULT 'pending_review' | pending_review, approved, released |

**Indexes:**
- PRIMARY KEY: id
- INDEX: draft_id, status
- UNIQUE: draft_id, category_id

## Configuration Tables

### system_config

System-wide configuration settings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | str | PRIMARY KEY | Configuration key |
| value | str | NOT NULL | Configuration value |
| description | str | | Setting description |

### domain_whitelist

Approved email domains for registration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| domain | str | NOT NULL UNIQUE | Email domain |
| auto_approve_instructor | bool | DEFAULT false | Auto-approve instructors |
| created_at | str | | Creation timestamp |
| updated_at | str | | Last update timestamp |

### aggregation_methods

Available feedback aggregation methods.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | str | NOT NULL | Method name |
| description | str | | Method description |
| is_active | bool | DEFAULT true | Method availability |

**Default Methods:**
- Average
- Weighted Average
- Maximum
- Median

### feedback_styles

Feedback presentation styles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | str | NOT NULL | Style name |
| description | str | | Style description |
| is_active | bool | DEFAULT true | Style availability |

### mark_display_options

Options for displaying scores to students.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| display_type | str | NOT NULL | numeric, hidden, icon |
| name | str | NOT NULL | Option name |
| description | str | | Option description |
| icon_type | str | | Icon type if applicable |
| is_active | bool | DEFAULT true | Option availability |

## Data Integrity Rules

### Soft Deletion Pattern

Most tables implement soft deletion using a `status` field:

```sql
-- Example status transitions
'draft' → 'active' → 'inactive' → 'archived' → 'deleted'

-- Query pattern for active records
SELECT * FROM table WHERE status != 'deleted';
```

### Timestamp Format

All timestamps use ISO 8601 format:
```
YYYY-MM-DDTHH:MM:SS.sssZ
Example: 2024-10-15T14:30:00.000Z
```

### JSON Storage

Complex configurations stored as JSON strings:
```python
# api_config example
{
    "api_key": "encrypted_key",
    "endpoint": "https://api.openai.com/v1",
    "organization": "org-123"
}

# capabilities example
["text", "vision", "code", "audio"]
```

### Privacy Constraints

1. Draft content can be removed after feedback generation
2. `content_preserved` flag prevents automatic removal
3. `content_removed_date` tracks deletion for compliance

### Cascade Rules

Application-level cascade handling:
- Deleting course → soft delete assignments → soft delete drafts
- Deleting user → handle based on role and data retention policy
- Deleting assignment → preserve drafts for record keeping

## Database Maintenance

### Regular Tasks

```sql
-- Vacuum database (monthly)
VACUUM;

-- Analyze tables for query optimization
ANALYZE;

-- Clean old soft-deleted records (quarterly)
DELETE FROM drafts 
WHERE status = 'deleted' 
AND DATE(updated_at) < DATE('now', '-90 days');
```

### Backup Strategy

```bash
# Daily backup script
sqlite3 data/users.db ".backup /backups/users_$(date +%Y%m%d).db"

# Verify backup integrity
sqlite3 /backups/users_20241015.db "PRAGMA integrity_check;"
```

### Performance Optimization

Key indexes for common queries:
1. User lookups by email and role
2. Course listings by instructor
3. Assignment queries by course and status
4. Draft searches by student and assignment
5. Feedback retrieval by draft status

## Migration Considerations

### SQLite to PostgreSQL

For scaling beyond SQLite limits:

```sql
-- Example PostgreSQL equivalents
-- SQLite: AUTOINCREMENT
-- PostgreSQL: SERIAL or IDENTITY

-- SQLite: TEXT for all strings
-- PostgreSQL: VARCHAR(n) with specific limits

-- SQLite: INTEGER for booleans
-- PostgreSQL: BOOLEAN native type
```

### Schema Versioning

Track schema changes:
```sql
-- system_config table
INSERT INTO system_config (key, value, description)
VALUES ('schema_version', '1.0.0', 'Current database schema version');
```

---

{: .note }
> This schema is optimized for educational workflows with privacy-conscious design. Regular maintenance and monitoring ensure optimal performance.