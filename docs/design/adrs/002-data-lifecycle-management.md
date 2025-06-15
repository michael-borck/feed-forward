# ADR 002: Data Lifecycle Management

## Status

Accepted

## Context

FeedForward needs to manage the lifecycle of various entities (users, courses, assignments) while preserving data integrity and student work. Common operations like "deleting" an account or course need to be handled in a way that:

1. Preserves student work and feedback
2. Maintains data relationships
3. Supports administrative needs
4. Provides good user experience
5. Minimizes administrative overhead

## Decision

We have decided to implement a soft deletion pattern across key entities using status fields rather than actual deletion. This includes:

### User Status Management
- Adding a `status` field to the users table with these possible values:
  - `active`: Normal account
  - `inactive`: Temporarily disabled (can be reactivated)
  - `archived`: Long-term inactive (preserved for record-keeping)
  - `deleted`: Soft-deleted (personal data anonymized but references maintained)
- Adding a `last_active` timestamp field to track user activity

### Course Status Management
- Adding a `status` field to the courses table:
  - `active`: Normal state
  - `closed`: No longer accepting new enrollments but viewable
  - `archived`: Hidden from normal views but accessible via history
  - `deleted`: Soft-deleted, hidden but references maintained
- Adding `created_at` and `updated_at` timestamp fields

### Assignment Status Management
- Adding a `status` field to the assignments table:
  - `draft`: Being prepared, not yet visible to students
  - `active`: Normal state, accepting submissions
  - `closed`: No longer accepting submissions but viewable
  - `archived`: Hidden from normal views but accessible via history
  - `deleted`: Soft-deleted, hidden but references maintained
- Adding `created_at` and `updated_at` timestamp fields

## Consequences

### Positive

- Student work and feedback is preserved regardless of entity status
- Data relationships are maintained for reporting and historical purposes
- Account reactivation is straightforward (status change rather than recreation)
- Supports compliance with educational record-keeping requirements
- Provides flexibility in how entities are displayed based on status
- Minimizes administrative overhead for managing "deleted" content

### Negative

- More complex queries to filter by status in various contexts
- Additional storage requirements (entities are never truly deleted)
- Need for data anonymization processes for truly deleted accounts
- Additional migration step for existing databases

## Implementation

The implementation includes:
1. Adding status and timestamp fields to key tables
2. Creating a migration script to update existing databases
3. Updating UI to show appropriate options based on entity status
4. Implementing reactivation flows for inactive accounts
5. Adding status filtering to queries that retrieve entities