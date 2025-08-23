# Phase 1: Assessment Framework Integration - Detailed Tasks

## Overview
The assessment type extensibility framework is ALREADY BUILT but needs to be connected to the main application. This phase focuses on integration, not creation.

## Pre-Implementation Checklist
- [x] Assessment handlers exist (`app/assessment/handlers/`)
- [x] Registry pattern implemented (`app/assessment/registry.py`)
- [x] Base handler class defined (`app/assessment/base.py`)
- [x] Database models created (`app/models/assessment.py`)
- [ ] Schema migrations needed
- [ ] UI integration needed
- [ ] Workflow connection needed

## Task Breakdown

### 1. Database Migration (Day 1-2)

#### 1.1 Create Migration Script
```python
# tools/migrate_assessment_types.py
# Add these columns to existing tables:
- assignments.assessment_type_id (FK to assessment_types.id)
- assignments.type_config (JSON)
- drafts.preprocessing_status (varchar)
- drafts.preprocessing_result (JSON)
- drafts.external_service_id (FK to assessment_services.id)
```

#### 1.2 Migration Tasks
- [ ] Write migration script using SQLite ALTER TABLE
- [ ] Add foreign key constraints
- [ ] Set default values for existing records
- [ ] Create rollback script
- [ ] Test migration on copy of database
- [ ] Document migration process

### 2. Assignment Creation UI (Day 3-4)

#### 2.1 Modify Assignment Form
**File**: `app/routes/instructor/assignments.py`

- [ ] Add assessment type dropdown to creation form
- [ ] Load assessment types from database
- [ ] Add type-specific configuration section
- [ ] Create dynamic form fields based on type
- [ ] Add client-side validation

#### 2.2 Type-Specific Configuration Forms

**Essay Configuration**:
- [ ] Min/max word count
- [ ] Allowed file formats
- [ ] Rubric integration

**Code Configuration**:
- [ ] Programming language selection
- [ ] Test case upload
- [ ] Execution time limits
- [ ] Memory limits

**Math Configuration**:
- [ ] Problem type (proof, calculation, etc.)
- [ ] LaTeX rendering support
- [ ] Symbol palette

**Video Configuration**:
- [ ] Max duration
- [ ] File size limits
- [ ] Resolution requirements
- [ ] Audio requirements

### 3. Submission Interface Updates (Day 5-6)

#### 3.1 Student Submission Page
**File**: `app/routes/student/submissions.py`

- [ ] Detect assessment type from assignment
- [ ] Render type-specific submission form
- [ ] Add file upload for code/video
- [ ] Implement type validation
- [ ] Show type-specific instructions

#### 3.2 Submission Handlers
- [ ] Route submissions to correct handler
- [ ] Implement preprocessing pipeline
- [ ] Store metadata in drafts table
- [ ] Handle file uploads appropriately
- [ ] Add progress indicators

### 4. Backend Integration (Day 7-8)

#### 4.1 Connect Registry to Routes
**Files to modify**:
- `app/routes/instructor/assignments.py`
- `app/routes/student/submissions.py`
- `app/services/feedback_generator.py`

Tasks:
- [ ] Import AssessmentRegistry
- [ ] Register handlers on startup
- [ ] Use registry.get_handler() for processing
- [ ] Pass type config to handlers
- [ ] Handle preprocessing results

#### 4.2 Update Feedback Generation
**File**: `app/services/feedback_generator.py`

- [ ] Use handler.generate_prompt() method
- [ ] Apply type-specific scoring
- [ ] Format feedback per type
- [ ] Store preprocessing results

### 5. Testing & Validation (Day 9-10)

#### 5.1 Manual Testing Checklist
- [ ] Create assignment with each type
- [ ] Submit draft for each type
- [ ] Verify preprocessing works
- [ ] Check feedback generation
- [ ] Test edge cases

#### 5.2 Data Validation
- [ ] Verify database constraints
- [ ] Check JSON field storage
- [ ] Test foreign key relationships
- [ ] Validate type configurations

## Implementation Order

### Day 1-2: Database
1. Write migration script
2. Test on development database
3. Document changes

### Day 3-4: Instructor UI
1. Update assignment creation form
2. Add type selector
3. Implement configuration forms

### Day 5-6: Student UI
1. Update submission page
2. Add type-specific forms
3. Handle file uploads

### Day 7-8: Backend
1. Connect registry
2. Update feedback pipeline
3. Test handler integration

### Day 9-10: Testing
1. Full workflow testing
2. Bug fixes
3. Documentation

## Code Snippets

### Migration Script Template
```python
def migrate_up():
    """Add assessment type fields"""
    db.execute('''
        ALTER TABLE assignments 
        ADD COLUMN assessment_type_id INTEGER 
        REFERENCES assessment_types(id)
    ''')
    
    db.execute('''
        ALTER TABLE assignments 
        ADD COLUMN type_config TEXT
    ''')
    
    # Set defaults for existing assignments
    db.execute('''
        UPDATE assignments 
        SET assessment_type_id = 1 
        WHERE assessment_type_id IS NULL
    ''')
```

### Registry Usage Example
```python
from app.assessment.registry import AssessmentRegistry

# In route handler
registry = AssessmentRegistry()
handler = registry.get_handler(assessment_type)
prompt = handler.generate_prompt(submission_content, assignment)
```

### Type-Specific Form Example
```python
def render_submission_form(assessment_type):
    if assessment_type == "essay":
        return essay_submission_form()
    elif assessment_type == "code":
        return code_submission_form()
    elif assessment_type == "video":
        return video_submission_form()
```

## Validation Points

### After Database Migration
- All tables have new columns
- Foreign keys are valid
- No data loss occurred
- Defaults are set correctly

### After UI Integration
- Type selector appears and works
- Configuration saves correctly
- Submission forms adapt to type
- File uploads work

### After Backend Integration
- Handlers process correctly
- Feedback generates properly
- Preprocessing completes
- Errors handled gracefully

## Rollback Plan

### If Migration Fails
1. Restore database backup
2. Fix migration script
3. Re-test on copy
4. Re-attempt migration

### If Integration Fails
1. Feature flag to disable
2. Default to essay type
3. Fix integration issues
4. Re-enable gradually

## Success Criteria

Phase 1 is complete when:
1. ✅ Database has all assessment type fields
2. ✅ Instructors can select assessment type when creating assignments
3. ✅ Students see type-appropriate submission forms
4. ✅ Each handler processes its type correctly
5. ✅ Feedback generates for all types
6. ✅ No regression in existing functionality

## Next Steps After Phase 1

1. Add external service integration (Phase 3)
2. Implement advanced type features
3. Add type-specific analytics
4. Create type migration tools
5. Document for other developers

---

*Note: The framework code already exists. This phase is purely about integration and connection, not building new components.*