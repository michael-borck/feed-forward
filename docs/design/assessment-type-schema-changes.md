# Assessment Type Extensibility - Database Schema Changes

## Overview

This document outlines the database schema changes required to support multiple assessment types in FeedForward.

## New Tables

### 1. `assessment_types`

Stores available assessment types and their configurations.

```sql
CREATE TABLE assessment_types (
    id INTEGER PRIMARY KEY,
    type_code TEXT UNIQUE NOT NULL,  -- 'essay', 'code', 'math', 'video', etc.
    display_name TEXT NOT NULL,
    description TEXT,
    handler_class TEXT NOT NULL,  -- Python class name for the handler
    file_extensions TEXT,  -- JSON array of allowed extensions
    max_file_size INTEGER,  -- Max size in bytes
    requires_file BOOLEAN DEFAULT 0,
    supports_text_input BOOLEAN DEFAULT 1,
    configuration TEXT,  -- JSON configuration specific to type
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Default assessment types
INSERT INTO assessment_types (type_code, display_name, handler_class, supports_text_input) VALUES
    ('essay', 'Essay', 'EssayAssessmentHandler', 1),
    ('code', 'Code', 'CodeAssessmentHandler', 1),
    ('math', 'Mathematics', 'MathAssessmentHandler', 1);
```

### 2. `assessment_services`

External services that can process specific assessment types.

```sql
CREATE TABLE assessment_services (
    id INTEGER PRIMARY KEY,
    service_name TEXT UNIQUE NOT NULL,
    service_url TEXT NOT NULL,
    api_key TEXT,  -- Encrypted
    assessment_types TEXT NOT NULL,  -- JSON array of supported type_codes
    capabilities TEXT,  -- JSON object describing service capabilities
    health_check_url TEXT,
    timeout_seconds INTEGER DEFAULT 300,
    is_active BOOLEAN DEFAULT 1,
    last_health_check TEXT,
    health_status TEXT,  -- 'healthy', 'unhealthy', 'unknown'
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### 3. `submission_files`

Store file uploads associated with drafts.

```sql
CREATE TABLE submission_files (
    id INTEGER PRIMARY KEY,
    draft_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,  -- Relative path in storage
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    checksum TEXT NOT NULL,  -- SHA256 hash
    uploaded_at TEXT NOT NULL,
    removed_at TEXT,  -- When file was deleted (privacy compliance)
    FOREIGN KEY (draft_id) REFERENCES drafts(id)
);
```

## Modified Tables

### 1. `assignments` table

Add assessment type field:

```sql
ALTER TABLE assignments ADD COLUMN assessment_type_id INTEGER DEFAULT 1;
ALTER TABLE assignments ADD COLUMN type_config TEXT;  -- JSON for type-specific settings
ALTER TABLE assignments ADD FOREIGN KEY (assessment_type_id) REFERENCES assessment_types(id);
```

### 2. `drafts` table

Add fields for different content types:

```sql
ALTER TABLE drafts ADD COLUMN submission_type TEXT DEFAULT 'text';  -- 'text', 'file', 'mixed'
ALTER TABLE drafts ADD COLUMN submission_metadata TEXT;  -- JSON metadata
ALTER TABLE drafts ADD COLUMN preprocessing_status TEXT;  -- 'pending', 'processing', 'complete', 'error'
ALTER TABLE drafts ADD COLUMN preprocessing_result TEXT;  -- JSON result from preprocessing
ALTER TABLE drafts ADD COLUMN external_service_id INTEGER;  -- If processed by external service
ALTER TABLE drafts ADD FOREIGN KEY (external_service_id) REFERENCES assessment_services(id);
```

### 3. `rubrics` table

Add assessment-type-specific rubric support:

```sql
ALTER TABLE rubrics ADD COLUMN assessment_type_id INTEGER;
ALTER TABLE rubrics ADD COLUMN type_specific_criteria TEXT;  -- JSON for type-specific evaluation
ALTER TABLE rubrics ADD FOREIGN KEY (assessment_type_id) REFERENCES assessment_types(id);
```

### 4. `model_runs` table

Track which service processed the submission:

```sql
ALTER TABLE model_runs ADD COLUMN preprocessing_service_id INTEGER;
ALTER TABLE model_runs ADD COLUMN service_response_time REAL;  -- Time in seconds
ALTER TABLE model_runs ADD FOREIGN KEY (preprocessing_service_id) REFERENCES assessment_services(id);
```

## Migration Strategy

### Phase 1: Add New Tables
1. Create all new tables without foreign key constraints
2. Populate `assessment_types` with default values
3. Add foreign key constraints

### Phase 2: Update Existing Tables
1. Add new columns with defaults
2. Migrate existing assignments to 'essay' type
3. Update all existing drafts with submission_type='text'

### Phase 3: Data Migration Script

```python
# Pseudo-code for migration
def migrate_to_assessment_types():
    # 1. Ensure essay type exists
    essay_type = get_or_create_assessment_type('essay')
    
    # 2. Update all existing assignments
    for assignment in assignments.all():
        assignment.assessment_type_id = essay_type.id
        assignment.save()
    
    # 3. Update all existing drafts
    for draft in drafts.all():
        draft.submission_type = 'text'
        draft.submission_metadata = {'migrated': True}
        draft.save()
```

## Indexes

Add indexes for performance:

```sql
CREATE INDEX idx_assignments_assessment_type ON assignments(assessment_type_id);
CREATE INDEX idx_drafts_submission_type ON drafts(submission_type);
CREATE INDEX idx_drafts_preprocessing_status ON drafts(preprocessing_status);
CREATE INDEX idx_submission_files_draft ON submission_files(draft_id);
CREATE INDEX idx_assessment_services_active ON assessment_services(is_active);
```

## Example Usage

### Creating a Code Assignment

```python
# Get code assessment type
code_type = assessment_types[type_code='code']

# Create assignment
assignment = Assignment(
    title="Python Functions",
    assessment_type_id=code_type.id,
    type_config={
        "language": "python",
        "test_cases": [...],
        "allowed_imports": ["math", "datetime"]
    }
)
```

### Submitting a Video

```python
# Create draft with file
draft = Draft(
    assignment_id=assignment.id,
    submission_type='file',
    submission_metadata={
        "duration": 180,
        "format": "mp4"
    }
)

# Store file reference
file = SubmissionFile(
    draft_id=draft.id,
    filename="presentation_123456.mp4",
    mime_type="video/mp4"
)
```

## Benefits

1. **Backward Compatible**: Existing essays continue to work
2. **Extensible**: New assessment types can be added without schema changes
3. **Service Integration**: External services can be registered and used
4. **File Management**: Proper tracking of uploaded files
5. **Type-Specific Configuration**: Each type can have custom settings
6. **Audit Trail**: Track which services processed submissions

## Security Considerations

1. File uploads must be validated and sandboxed
2. External service API keys must be encrypted
3. File checksums ensure integrity
4. Automatic file removal for privacy compliance
5. Service health monitoring for reliability