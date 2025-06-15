---
layout: default
title: Architecture
parent: Technical Documentation
nav_order: 1
---

# System Architecture
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward is designed as a monolithic web application with a focus on simplicity, privacy, and educational effectiveness. The architecture prioritizes ease of deployment, minimal operational overhead, and clear separation of concerns while providing sophisticated AI-powered feedback capabilities.

## High-Level Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│                    (Student/Instructor/Admin)               │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────┴───────────────────────────────────┐
│                    FastHTML Application                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Presentation Layer                   │   │
│  │          (FastHTML + HTMX + Tailwind CSS)           │   │
│  └─────────────────────────┬───────────────────────────┘   │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │                  Application Layer                   │   │
│  │     (Routes, Controllers, Business Logic)            │   │
│  └─────────────────────────┬───────────────────────────┘   │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │                   Service Layer                      │   │
│  │  (Auth, Feedback Gen, Email, File Processing)       │   │
│  └─────────────────────────┬───────────────────────────┘   │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │                    Data Layer                        │   │
│  │           (FastLite ORM + SQLite Database)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┴────────────────┐
        │                                      │
┌───────┴─────────┐                  ┌─────────┴────────┐
│  External APIs  │                  │   File Storage   │
│  (LLM Providers)│                  │   (Local Disk)   │
└─────────────────┘                  └──────────────────┘
```

### Technology Stack

```yaml
Core Framework:
  Language: Python 3.8+
  Web Framework: FastHTML (FastAPI + Starlette)
  Template Engine: FastHTML components
  Frontend: HTMX for interactivity
  Styling: Tailwind CSS

Database:
  Engine: SQLite 3
  ORM: FastLite
  Migrations: Custom SQL scripts

External Services:
  AI/LLM: LiteLLM (multi-provider)
  Email: SMTP
  File Processing: Python libraries

Infrastructure:
  Server: Uvicorn ASGI
  Process Manager: systemd/supervisor
  Reverse Proxy: nginx (recommended)
```

## Architectural Patterns

### Model-View-Controller (MVC)

FeedForward follows a modified MVC pattern:

```
Models (app/models/)
├── User, Course, Assignment, Draft
├── AIModel, FeedbackResult
└── Database schema definitions

Views (app/templates/ + FastHTML components)
├── Server-side rendered HTML
├── HTMX partial updates
└── Tailwind CSS styling

Controllers (app/routes/)
├── Route handlers by role
├── Business logic coordination
└── Response generation
```

### Service-Oriented Architecture

Key services are isolated for maintainability:

```
Services (app/services/)
├── AuthService - Authentication/authorization
├── FeedbackGenerator - AI feedback orchestration
├── EmailService - Notification delivery
├── FileHandler - Upload/content extraction
├── PrivacyService - Data cleanup/retention
└── AnalyticsService - Progress tracking
```

## Data Architecture

### Database Schema Overview

```sql
-- Core Educational Hierarchy
users (id, email, role, status...)
  └── instructors → courses
       └── assignments
            └── drafts (student submissions)
                 └── feedback_results

-- AI Configuration
ai_providers (api keys, config)
  └── ai_models
       └── assignment_model_runs
            └── model_feedback_results

-- Supporting Tables
rubric_templates
rubric_criteria
course_students
invitations
audit_logs
```

### Data Flow

```
Student Submission Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. File Upload
   Browser → FastHTML → FileHandler → Disk Storage

2. Content Processing
   File → Extractor → Draft Record → Database

3. AI Feedback Generation
   Draft → FeedbackGenerator → LLM APIs → Results

4. Instructor Review
   Results → Review Interface → Approval → Student

5. Privacy Cleanup
   Scheduled Task → Remove Content → Keep Metadata
```

### Entity Lifecycle Management

All major entities follow a consistent lifecycle:

```yaml
Status Progression:
  draft → active → inactive → archived → deleted

Soft Deletion:
  - Records never physically deleted
  - Status field indicates state
  - Deleted_at timestamp when removed
  - Cascade rules for dependent entities

Example - Course Lifecycle:
  draft: Being created
  active: Students can access
  inactive: No new submissions
  archived: Read-only access
  deleted: Hidden from all users
```

## Security Architecture

### Authentication & Authorization

```
Authentication Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Email/Password Login
   └── Verify credentials
        └── Create session
             └── Set secure cookie

2. Role-Based Access Control
   Admin: Full system access
   Instructor: Course management
   Student: Assignment submission

3. Route Protection
   @admin_required
   @instructor_required  
   @student_required
```

### Data Security

```yaml
API Key Management:
  Storage: Encrypted in database
  Encryption: Fernet (symmetric)
  Key Derivation: PBKDF2HMAC from SECRET_KEY
  Access: Decrypted only when needed

Student Data Privacy:
  Submissions: Temporarily stored
  Cleanup: Automatic after feedback
  Retention: Metadata only
  Access: Student + Instructor only

Session Security:
  Cookie: HTTPOnly, Secure, SameSite
  Timeout: Configurable (default 24h)
  Storage: Server-side sessions
```

## AI Integration Architecture

### Multi-Model System

```
AI Model Hierarchy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provider Level (OpenAI, Anthropic, etc.)
  ├── API Configuration
  ├── Authentication
  └── Rate Limiting

Model Level (GPT-4, Claude-3, etc.)
  ├── Capabilities
  ├── Default Parameters
  └── Cost Information

Instance Level (Per Assignment Config)
  ├── Temperature Settings
  ├── Token Limits
  ├── Custom Prompts
  └── Number of Runs
```

### Feedback Generation Pipeline

```python
# Simplified feedback generation flow
async def generate_feedback(draft_id):
    # 1. Load assignment configuration
    assignment = get_assignment_settings(draft_id)
    
    # 2. Execute multiple model runs
    results = []
    for model in assignment.models:
        for run in range(model.num_runs):
            result = await call_llm(
                model=model,
                prompt=build_prompt(draft, rubric),
                parameters=model.parameters
            )
            results.append(result)
    
    # 3. Aggregate results
    final_feedback = aggregate_results(
        results, 
        method=assignment.aggregation_method
    )
    
    # 4. Store and notify
    save_feedback(final_feedback)
    notify_instructor(draft_id)
```

## Scalability Considerations

### Current Design Limits

```yaml
Concurrent Users: ~1,000 active
Total Users: ~20,000 accounts
Requests/Second: ~100
Database Size: ~10GB practical limit
File Storage: Local disk dependent
```

### Scaling Strategies

```
Vertical Scaling (Current):
├── Increase server resources
├── Optimize database queries
├── Add caching layer
└── Tune worker processes

Future Horizontal Scaling:
├── PostgreSQL migration
├── S3 file storage
├── Redis session store
├── Load balancer
└── Background job queue
```

## Deployment Architecture

### Single-Server Deployment

```
Recommended Production Setup:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────┐
│         nginx (Reverse Proxy)   │
│  - SSL termination              │
│  - Static file serving          │
│  - Rate limiting                │
└────────────────┬────────────────┘
                 │
┌────────────────┴────────────────┐
│      Uvicorn (ASGI Server)      │
│  - Multiple workers             │
│  - Process management           │
└────────────────┬────────────────┘
                 │
┌────────────────┴────────────────┐
│     FeedForward Application     │
│  - FastHTML app                 │
│  - SQLite database              │
│  - Local file storage           │
└─────────────────────────────────┘
```

### Directory Structure

```
/opt/feedforward/
├── app/              # Application code
├── data/            
│   ├── feedforward.db    # SQLite database
│   └── uploads/          # Temporary files
├── logs/            # Application logs
├── backups/         # Database backups
└── venv/            # Python virtual environment
```

## Background Tasks

### Asynchronous Processing

```python
# Background task example
@background_task
async def process_draft_submission(draft_id):
    try:
        # Update status
        update_draft_status(draft_id, "processing")
        
        # Generate feedback
        await generate_feedback(draft_id)
        
        # Cleanup
        schedule_content_removal(draft_id)
        
    except Exception as e:
        update_draft_status(draft_id, "error")
        log_error(e)
```

### Scheduled Tasks

```yaml
Scheduled Jobs:
  Privacy Cleanup:
    Schedule: Every hour
    Action: Remove old submission content
    
  Database Optimization:
    Schedule: Daily at 2 AM
    Action: VACUUM and ANALYZE
    
  Usage Reports:
    Schedule: Weekly
    Action: Generate analytics
    
  Backup:
    Schedule: Daily at 3 AM
    Action: Database backup
```

## Performance Optimization

### Caching Strategy

```yaml
Cache Layers:
  Application Cache:
    - Rubric templates
    - AI model configurations
    - User permissions
    
  Database Query Cache:
    - Prepared statements
    - Connection pooling
    - Index optimization
    
  Frontend Cache:
    - Static assets (1 year)
    - HTMX partials (5 minutes)
    - API responses (varies)
```

### Database Optimization

```sql
-- Key indexes for performance
CREATE INDEX idx_drafts_assignment_student 
  ON drafts(assignment_id, student_id);

CREATE INDEX idx_feedback_draft 
  ON feedback_results(draft_id);

CREATE INDEX idx_courses_instructor 
  ON courses(instructor_id, status);

-- Partitioning strategy (future)
-- Partition by academic year for historical data
```

## Error Handling

### Error Classification

```yaml
User Errors (4xx):
  - Invalid input → Clear error message
  - Unauthorized → Redirect to login
  - Not found → Helpful 404 page

System Errors (5xx):
  - Database error → Retry + fallback
  - AI API failure → Queue for retry
  - Server error → Error page + logging

External Service Errors:
  - LLM timeout → Fallback model
  - Email failure → Retry queue
  - File processing → Error notification
```

### Fault Tolerance

```python
# Resilient service pattern
async def call_ai_with_fallback(prompt, models):
    for model in models:
        try:
            return await model.generate(prompt)
        except (Timeout, APIError):
            continue
    
    # All models failed
    return queue_for_manual_review(prompt)
```

## Monitoring and Observability

### Key Metrics

```yaml
Application Metrics:
  - Request rate and latency
  - Error rates by endpoint
  - Active user sessions
  - Background job success rate

Business Metrics:
  - Submissions per day
  - Feedback generation time
  - AI API usage and costs
  - User engagement rates

System Metrics:
  - CPU and memory usage
  - Database query performance
  - Disk usage and I/O
  - Network throughput
```

### Logging Architecture

```
Log Streams:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Logs → /logs/app.log
  - User actions
  - Business events
  - Errors and warnings

Access Logs → /logs/access.log
  - HTTP requests
  - Response times
  - Status codes

Audit Logs → Database
  - Security events
  - Data modifications
  - Permission changes

AI Logs → /logs/ai_calls.log
  - Model calls
  - Token usage
  - Response times
```

## Future Architecture Considerations

### Potential Enhancements

```yaml
Near-term (6 months):
  - Redis caching layer
  - PostgreSQL migration option
  - S3-compatible file storage
  - Enhanced monitoring (Prometheus)

Medium-term (1 year):
  - Microservices extraction
  - API-first architecture
  - Real-time notifications (WebSockets)
  - Advanced analytics pipeline

Long-term (2+ years):
  - Multi-tenant SaaS option
  - Kubernetes deployment
  - Event-driven architecture
  - Machine learning pipeline
```

### Migration Paths

```
SQLite → PostgreSQL:
  - Export/import scripts
  - Connection string change
  - Query compatibility layer
  - Gradual migration support

Monolith → Services:
  - Extract feedback service first
  - API gateway pattern
  - Shared database initially
  - Event bus for communication
```

## Architecture Decision Records

Key architectural decisions are documented in ADRs:

1. [ADR-001: AI Model Ownership](../design/adrs/001-ai-model-ownership) - System vs instructor model management
2. [ADR-002: Data Lifecycle](../design/adrs/002-data-lifecycle-management) - Soft deletion and status management
3. [ADR-003: Authentication Strategy](../design/adrs/003-authentication-strategy) - Email-based with roles
4. [ADR-004: Database Choice](../design/adrs/004-database-choice) - SQLite for simplicity
5. [ADR-005: UI Framework](../design/adrs/005-ui-framework-selection) - FastHTML with HTMX
6. [ADR-006: Student Enrollment](../design/adrs/006-student-enrollment-lifecycle) - Invitation-only system
7. [ADR-007: Educational Workflow](../design/adrs/007-educational-workflow-architecture) - Hierarchical structure
8. [ADR-008: Submission Privacy](../design/adrs/008-student-submission-privacy) - Temporary storage
9. [ADR-009: API Key Management](../design/adrs/009-api-key-management) - Encrypted storage
10. [ADR-010: Model Configuration](../design/adrs/010-model-instance-configuration) - Three-tier system

---

{: .note }
> This architecture is designed for institutional deployment with 1,000-20,000 users. For larger scales, consider the migration paths outlined above.