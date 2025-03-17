# 1. Introduction

This document outlines the technical implementation plan for the FeedForward MVP, a system designed to provide AI-driven formative feedback on student assignments. The MVP will implement a foundation that supports the core multi-model assessment approach while focusing on a simplified implementation with a single AI model and multiple runs.
# 2. System Architecture

## 2.1 High-Level Data Flow

```
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│                 │          │                 │          │                 │
│    Student      │          │   FeedForward   │          │   Instructor    │
│    Interface    │◄────────►│     System      │◄────────►│   Interface     │
│                 │          │                 │          │                 │
└────────┬────────┘          └────────┬────────┘          └────────┬────────┘
         │                            │                            │
         │                            ▼                            │
         │                   ┌─────────────────┐                   │
         │                   │                 │                   │
         │                   │    Database     │                   │
         │                   │                 │                   │
         │                   └────────┬────────┘                   │
         │                            │                            │
         │                            ▼                            │
         │                   ┌─────────────────┐                   │
         │                   │                 │                   │
         └──────────────────►│   AI Model      │◄──────────────────┘
                             │   Integration   │
                             │                 │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │                 │
                             │  External AI    │
                             │  Service APIs   │
                             │                 │
                             └─────────────────┘
```

## 2.2 Component Overview

1. **Student Interface**:
   - Draft submission system
   - Feedback review dashboard
   - Progress tracking
   - Built with FastHTML + HTMX + Tailwind CSS

2. **Instructor Interface**:
   - Course and assignment management
   - Rubric creation
   - Feedback settings configuration
   - Review and oversight tools
   - Built with FastHTML + HTMX + Tailwind CSS

3. **Core System**:
   - Assignment processing
   - Feedback aggregation
   - Data management
   - Built with FastAPI + SQLAlchemy

4. **AI Integration Layer**:
   - Model integration and management
   - Prompt engineering
   - Run coordination
   - Built with Python + API clients

5. **Database**:
   - SQLite for MVP
   - SQLAlchemy ORM
   - Migration path to PostgreSQL
# 3. Database Schema

```
┌───────────────────┐
                   ┌───────────────────────────────────────────►│     AIModel        │
                   │                                             ├───────────────────┤
┌───────────────┐  │                         ┌───────────────┐   │ id (PK)           │
│     User      │  │                         │    Course     │   │ name              │
├───────────────┤  │                         ├───────────────┤   │ api_provider      │
│ id (PK)       │  │                         │ id (PK)       │   │ version           │
│ email         │  │                         │ code          │   │ active            │
│ name          │◄─┼─────────────┐          │ title         │   │ api_config        │
│ password_hash │  │             │          │ term          │   └───────────────────┘
│ role          │  │             │          │ department    │            ▲
└───────┬───────┘  │         ┌───┴─────────┐│ instructor_id │◄───┐       │
        │          │         │ Enrollment  ││ (FK)          │    │       │
        │          │         ├─────────────┤└───────────────┘    │       │
        │          │         │ id (PK)     │        ▲            │       │
        ▼          │         │ student_id  │        │            │       │
┌───────────────┐  │         │ (FK)        │        │            │       │
│  Instructor   │  │         │ course_id   │  ┌─────┴───────┐    │       │
├───────────────┤  │         │ (FK)        │  │ Assignment  │    │       │
│ id (PK)       │  │         └─────────────┘  ├─────────────┤    │       │
│ user_id (FK)  │  │                          │ id (PK)     │    │       │
│ department    │  │                          │ course_id   │    │       │
└───────────────┘  │                          │ (FK)        │    │       │
        ▲          │                          │ title       │    │       │
        │          │                          │ description │    │       │
┌───────┴───────┐  │                          │ due_date    │    │       │
│    Student    │  │                          │ max_drafts  │    │       │
├───────────────┤  │                          │ created_by  │◄───┘       │
│ id (PK)       │  │                          │ (FK)        │            │
│ user_id (FK)  │  │                          └───────┬─────┘            │
└───────────────┘  │                                  │                  │
        ▲          │                                  ▼                  │
        │          │                          ┌───────────────┐          │
        │          │                          │    Rubric     │          │
        │          │                          ├───────────────┤          │
        │          │                          │ id (PK)       │          │
        │          │                          │ assignment_id │          │
        │          │                          │ (FK)          │          │
        │          │                          └───────┬───────┘          │
        │          │                                  │                  │
        │          │                                  ▼                  │
        │          │                          ┌───────────────┐          │
        │          │                          │RubricCategory │          │
        │          │                          ├───────────────┤          │
        │          │                          │ id (PK)       │          │
        │          │                          │ rubric_id (FK)│          │
        │          │                          │ name          │          │
        │          │                          │ description   │          │
        │          │                          │ weight        │          │
        │          │                          └───────────────┘          │
        │          │                                                     │
        │          │                                                     │
        │          │         ┌───────────────┐         ┌───────────────┐│
        └──────────────────►│     Draft     │◄───────►│  ModelRun     ││
                            ├───────────────┤         ├───────────────┤│
                            │ id (PK)       │         │ id (PK)       ││
                            │ assignment_id │         │ draft_id (FK) ││
                            │ (FK)          │         │ model_id (FK) ││
                            │ student_id    │         │ run_number    ││
                            │ (FK)          │         │ timestamp     ││
                            │ version       │         └───────┬───────┘│
                            │ content       │                 │        │
                            │ submission_   │                 │        │
                            │ date          │                 │        │
                            └───────┬───────┘                 │        │
                                    │                         │        │
                                    ▼                         ▼        │
                            ┌───────────────┐         ┌───────────────┐│
                            │ FeedbackItem  │◄────────│CategoryScore  ││
                            ├───────────────┤         ├───────────────┤│
                            │ id (PK)       │         │ id (PK)       ││
                            │ modelrun_id   │         │ modelrun_id   ││
                            │ (FK)          │         │ (FK)          ││
                            │ type          │         │ category_id   ││
                            │ content       │         │ (FK)          ││
                            │ is_strength   │         │ score         ││
                            │ is_aggregated │         │ confidence    ││
                            └───────────────┘         └───────────────┘
                           
                           
                           ┌────────────────────┐       ┌───────────────────┐
                           │ AggregationMethod  │       │SystemConfiguration│
                           ├────────────────────┤       ├───────────────────┤
                           │ id (PK)            │       │ id (PK)           │
                           │ name               │       │ setting_key       │
                           │ description        │       │ setting_value     │
                           │ is_active          │       │ description       │
                           └────────────────────┘       └───────────────────┘
                                    ▲
                                    │
┌───────────────────┐      ┌───────┴───────────┐
│   FeedbackStyle   │      │AssignmentSettings │
├───────────────────┤      ├───────────────────┤
│ id (PK)           │      │ id (PK)           │
│ name              │      │ assignment_id (FK)│
│ description       │      │ ai_model_id (FK)  │◄─────────┐
│ is_active         │      │ num_runs          │          │
└───────────────────┘      │ aggregation_      │          │
         ▲                 │ method_id (FK)    │          │
         │                 │ feedback_style_id │          │
         └─────────────────│ (FK)              │          │
                           │ require_review    │          │
                           └───────────────────┘          │
                                                          │
                                                          │
                           ┌───────────────────┐          │
                           │ FeedbackHistory   │          │
                           ├───────────────────┤          │
                           │ id (PK)           │          │
                           │ draft_id (FK)     │          │
                           │ aggregated_score  │          │
                           │ instructor_      │           │
                           │ reviewed         │           │
                           │ instructor_id (FK)│           │
                           │ release_date     │           │
                           └───────────────────┘           │
                                                           │
                                                           │
                           ┌───────────────────────────────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │ AggregatedFeedback│
                  ├───────────────────┤
                  │ id (PK)           │
                  │ feedback_history_ │
                  │ id (FK)           │
                  │ category_id (FK)  │
                  │ aggregated_score  │
                  │ feedback_text     │
                  │ edited_by_        │
                  │ instructor        │
                  └───────────────────┘
```

## 3.1 Core User and Role Management

```sql
CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE Student (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Instructor (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    department TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Course (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    term TEXT NOT NULL,
    department TEXT,
    instructor_id INTEGER NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES Instructor(id)
);

CREATE TABLE Enrollment (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(id),
    FOREIGN KEY (course_id) REFERENCES Course(id)
);
```

## 3.2 Assignment and Rubric Management

```sql
CREATE TABLE Assignment (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATETIME NOT NULL,
    max_drafts INTEGER NOT NULL DEFAULT 3,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(id),
    FOREIGN KEY (created_by) REFERENCES Instructor(id)
);

CREATE TABLE Rubric (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES Assignment(id)
);

CREATE TABLE RubricCategory (
    id INTEGER PRIMARY KEY,
    rubric_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    weight REAL NOT NULL,
    FOREIGN KEY (rubric_id) REFERENCES Rubric(id)
);
```

## 3.3 Draft and Feedback System

```sql
CREATE TABLE Draft (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    submission_date DATETIME NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES Assignment(id),
    FOREIGN KEY (student_id) REFERENCES Student(id)
);

CREATE TABLE AIModel (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    api_provider TEXT NOT NULL,
    version TEXT,
    active BOOLEAN NOT NULL DEFAULT 1,
    api_config TEXT
);

CREATE TABLE ModelRun (
    id INTEGER PRIMARY KEY,
    draft_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    run_number INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (draft_id) REFERENCES Draft(id),
    FOREIGN KEY (model_id) REFERENCES AIModel(id)
);

CREATE TABLE CategoryScore (
    id INTEGER PRIMARY KEY,
    modelrun_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    score REAL NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (modelrun_id) REFERENCES ModelRun(id),
    FOREIGN KEY (category_id) REFERENCES RubricCategory(id)
);

CREATE TABLE FeedbackItem (
    id INTEGER PRIMARY KEY,
    modelrun_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    is_strength BOOLEAN NOT NULL,
    is_aggregated BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (modelrun_id) REFERENCES ModelRun(id)
);
```

## 3.4 Configuration and Settings

```sql
CREATE TABLE SystemConfiguration (
    id INTEGER PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT
);

CREATE TABLE AggregationMethod (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE FeedbackStyle (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE MarkDisplayOption (
    id INTEGER PRIMARY KEY,
    display_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon_type TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE AssignmentSettings (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL,
    ai_model_id INTEGER NOT NULL,
    num_runs INTEGER NOT NULL DEFAULT 3,
    aggregation_method_id INTEGER NOT NULL,
    feedback_style_id INTEGER NOT NULL,
    require_review BOOLEAN NOT NULL DEFAULT 1,
    mark_display_option_id INTEGER NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES Assignment(id),
    FOREIGN KEY (ai_model_id) REFERENCES AIModel(id),
    FOREIGN KEY (aggregation_method_id) REFERENCES AggregationMethod(id),
    FOREIGN KEY (feedback_style_id) REFERENCES FeedbackStyle(id),
    FOREIGN KEY (mark_display_option_id) REFERENCES MarkDisplayOption(id)
);
```

## 3.5 Feedback Processing

```sql
CREATE TABLE FeedbackHistory (
    id INTEGER PRIMARY KEY,
    draft_id INTEGER NOT NULL,
    aggregated_score REAL,
    instructor_reviewed BOOLEAN NOT NULL DEFAULT 0,
    instructor_id INTEGER,
    release_date DATETIME,
    FOREIGN KEY (draft_id) REFERENCES Draft(id),
    FOREIGN KEY (instructor_id) REFERENCES Instructor(id)
);

CREATE TABLE AggregatedFeedback (
    id INTEGER PRIMARY KEY,
    feedback_history_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    aggregated_score REAL NOT NULL,
    feedback_text TEXT NOT NULL,
    edited_by_instructor BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (feedback_history_id) REFERENCES FeedbackHistory(id),
    FOREIGN KEY (category_id) REFERENCES RubricCategory(id)
);
```
# 4. SQLAlchemy ORM Models

## 4.1 User Management Models

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)
    instructor = relationship("Instructor", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")
    drafts = relationship("Draft", back_populates="student")

class Instructor(Base):
    __tablename__ = 'instructors'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="instructor")
    courses = relationship("Course", back_populates="instructor")
    assignments_created = relationship("Assignment", back_populates="created_by")
    feedback_reviewed = relationship("FeedbackHistory", back_populates="instructor")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    term = Column(String, nullable=False)
    department = Column(String)
    instructor_id = Column(Integer, ForeignKey('instructors.id'), nullable=False)
    
    # Relationships
    instructor = relationship("Instructor", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
```

## 4.2 Assignment and Rubric Models

```python
class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime, nullable=False)
    max_drafts = Column(Integer, nullable=False, default=3)
    created_by_id = Column(Integer, ForeignKey('instructors.id'), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="assignments")
    created_by = relationship("Instructor", back_populates="assignments_created")
    rubric = relationship("Rubric", back_populates="assignment", uselist=False)
    drafts = relationship("Draft", back_populates="assignment")
    settings = relationship("AssignmentSettings", back_populates="assignment", uselist=False)

class Rubric(Base):
    __tablename__ = 'rubrics'
    
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="rubric")
    categories = relationship("RubricCategory", back_populates="rubric")

class RubricCategory(Base):
    __tablename__ = 'rubric_categories'
    
    id = Column(Integer, primary_key=True)
    rubric_id = Column(Integer, ForeignKey('rubrics.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    weight = Column(Float, nullable=False)
    
    # Relationships
    rubric = relationship("Rubric", back_populates="categories")
    category_scores = relationship("CategoryScore", back_populates="category")
    aggregated_feedback = relationship("AggregatedFeedback", back_populates="category")
```

## 4.3 Draft and Feedback Models

```python
class Draft(Base):
    __tablename__ = 'drafts'
    
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    version = Column(Integer, nullable=False)
    submission_date = Column(DateTime, nullable=False)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="drafts")
    student = relationship("Student", back_populates="drafts")
    model_runs = relationship("ModelRun", back_populates="draft")
    feedback_history = relationship("FeedbackHistory", back_populates="draft", uselist=False)

class AIModel(Base):
    __tablename__ = 'ai_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_provider = Column(String, nullable=False)
    version = Column(String)
    active = Column(Boolean, nullable=False, default=True)
    api_config = Column(String)  # JSON string with API configuration
    
    # Relationships
    model_runs = relationship("ModelRun", back_populates="model")
    assignment_settings = relationship("AssignmentSettings", back_populates="ai_model")

class ModelRun(Base):
    __tablename__ = 'model_runs'
    
    id = Column(Integer, primary_key=True)
    draft_id = Column(Integer, ForeignKey('drafts.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    run_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    draft = relationship("Draft", back_populates="model_runs")
    model = relationship("AIModel", back_populates="model_runs")
    category_scores = relationship("CategoryScore", back_populates="model_run")
    feedback_items = relationship("FeedbackItem", back_populates="model_run")

class CategoryScore(Base):
    __tablename__ = 'category_scores'
    
    id = Column(Integer, primary_key=True)
    modelrun_id = Column(Integer, ForeignKey('model_runs.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('rubric_categories.id'), nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Relationships
    model_run = relationship("ModelRun", back_populates="category_scores")
    category = relationship("RubricCategory", back_populates="category_scores")

class FeedbackItem(Base):
    __tablename__ = 'feedback_items'
    
    id = Column(Integer, primary_key=True)
    modelrun_id = Column(Integer, ForeignKey('model_runs.id'), nullable=False)
    type = Column(String, nullable=False)  # 'strength', 'improvement', 'general'
    content = Column(String, nullable=False)
    is_strength = Column(Boolean, nullable=False)
    is_aggregated = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    model_run = relationship("ModelRun", back_populates="feedback_items")
```

## 4.4 Configuration and Settings Models

```python
class SystemConfiguration(Base):
    __tablename__ = 'system_configurations'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(String, nullable=False)
    description = Column(String)

class AggregationMethod(Base):
    __tablename__ = 'aggregation_methods'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    assignment_settings = relationship("AssignmentSettings", back_populates="aggregation_method")

class FeedbackStyle(Base):
    __tablename__ = 'feedback_styles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    assignment_settings = relationship("AssignmentSettings", back_populates="feedback_style")

class MarkDisplayOption(Base):
    __tablename__ = 'mark_display_options'
    
    id = Column(Integer, primary_key=True)
    display_type = Column(String, nullable=False)  # 'numeric', 'hidden', 'icon'
    name = Column(String, nullable=False)
    description = Column(String)
    icon_type = Column(String)  # 'bullseye', 'track', 'first-aid'
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    assignment_settings = relationship("AssignmentSettings", back_populates="mark_display_option")

class AssignmentSettings(Base):
    __tablename__ = 'assignment_settings'
    
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    ai_model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    num_runs = Column(Integer, nullable=False, default=3)
    aggregation_method_id = Column(Integer, ForeignKey('aggregation_methods.id'), nullable=False)
    feedback_style_id = Column(Integer, ForeignKey('feedback_styles.id'), nullable=False)
    require_review = Column(Boolean, nullable=False, default=True)
    mark_display_option_id = Column(Integer, ForeignKey('mark_display_options.id'), nullable=False)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="settings")
    ai_model = relationship("AIModel", back_populates="assignment_settings")
    aggregation_method = relationship("AggregationMethod", back_populates="assignment_settings")
    feedback_style = relationship("FeedbackStyle", back_populates="assignment_settings")
    mark_display_option = relationship("MarkDisplayOption", back_populates="assignment_settings")
```

## 4.5 Feedback Processing Models

```python
class FeedbackHistory(Base):
    __tablename__ = 'feedback_histories'
    
    id = Column(Integer, primary_key=True)
    draft_id = Column(Integer, ForeignKey('drafts.id'), nullable=False)
    aggregated_score = Column(Float)
    instructor_reviewed = Column(Boolean, nullable=False, default=False)
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    release_date = Column(DateTime)
    
    # Relationships
    draft = relationship("Draft", back_populates="feedback_history")
    instructor = relationship("Instructor", back_populates="feedback_reviewed")
    aggregated_feedbacks = relationship("AggregatedFeedback", back_populates="feedback_history")

class AggregatedFeedback(Base):
    __tablename__ = 'aggregated_feedbacks'
    
    id = Column(Integer, primary_key=True)
    feedback_history_id = Column(Integer, ForeignKey('feedback_histories.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('rubric_categories.id'), nullable=False)
    aggregated_score = Column(Float, nullable=False)
    feedback_text = Column(String, nullable=False)
    edited_by_instructor = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    feedback_history = relationship("FeedbackHistory", back_populates="aggregated_feedbacks")
    category = relationship("RubricCategory", back_populates="aggregated_feedback")
```
# 5. Core Business Logic

## 5.1 Draft Submission Processing

```python
async def process_draft_submission(draft_id: int, db: Session):
    """
    Process a submitted draft through multiple runs of the configured AI model.
    """
    # Get the draft and related objects
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    assignment = draft.assignment
    settings = assignment.settings
    
    # Get AI model configuration
    ai_model = settings.ai_model
    num_runs = settings.num_runs
    
    # Get draft content
    draft_content = await get_draft_content(draft_id)  # Retrieves from temporary storage
    
    # Get rubric data
    rubric = assignment.rubric
    rubric_categories = rubric.categories
    
    # Create prompt from rubric and assignment details
    prompt = create_assessment_prompt(assignment, rubric_categories, draft_content)
    
    # Process multiple runs
    for run_number in range(1, num_runs + 1):
        # Create model run record
        model_run = ModelRun(
            draft_id=draft_id,
            model_id=ai_model.id,
            run_number=run_number,
            timestamp=datetime.now()
        )
        db.add(model_run)
        db.commit()
        
        # Send to AI API
        ai_response = await call_ai_api(ai_model, prompt)
        
        # Parse and store feedback
        process_ai_response(ai_response, model_run.id, rubric_categories, db)
    
    # Aggregate feedback from all runs
    aggregate_feedback(draft_id, settings.aggregation_method_id, db)
    
    # Create feedback history record
    feedback_history = FeedbackHistory(
        draft_id=draft_id,
        aggregated_score=calculate_overall_score(draft_id, db),
        instructor_reviewed=False,
        release_date=None if settings.require_review else datetime.now()
    )
    db.add(feedback_history)
    db.commit()
    
    # Delete draft content if not needed for privacy
    await delete_draft_content(draft_id)
    
    return feedback_history.id
```

## 5.2 Feedback Aggregation

```python
def aggregate_feedback(draft_id: int, aggregation_method_id: int, db: Session):
    """
    Aggregate feedback and scores from multiple runs.
    """
    # Get all model runs for this draft
    model_runs = db.query(ModelRun).filter(ModelRun.draft_id == draft_id).all()
    
    # Get aggregation method
    aggregation_method = db.query(AggregationMethod).filter(AggregationMethod.id == aggregation_method_id).first()
    
    # Get all rubric categories
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    assignment = draft.assignment
    rubric = assignment.rubric
    categories = rubric.categories
    
    # Create feedback history
    feedback_history = FeedbackHistory(
        draft_id=draft_id,
        instructor_reviewed=False
    )
    db.add(feedback_history)
    db.commit()
    
    # Process each category
    for category in categories:
        # Get all scores for this category across all runs
        scores = db.query(CategoryScore).join(ModelRun).filter(
            ModelRun.draft_id == draft_id,
            CategoryScore.category_id == category.id
        ).all()
        
        # Apply aggregation method
        aggregated_score = apply_aggregation_method(
            scores=[s.score for s in scores],
            confidences=[s.confidence for s in scores],
            method=aggregation_method.name
        )
        
        # Aggregate feedback text
        feedback_text = aggregate_feedback_text(
            model_runs=model_runs,
            category_id=category.id,
            db=db
        )
        
        # Create aggregated feedback record
        aggregated_feedback = AggregatedFeedback(
            feedback_history_id=feedback_history.id,
            category_id=category.id,
            aggregated_score=aggregated_score,
            feedback_text=feedback_text,
            edited_by_instructor=False
        )
        db.add(aggregated_feedback)
    
    # Calculate overall score as weighted average
    overall_score = calculate_weighted_overall_score(feedback_history.id, db)
    feedback_history.aggregated_score = overall_score
    db.commit()
    
    return feedback_history.id
```

## 5.3 Mark Display Logic

```python
def get_mark_display(score: float, display_option_id: int, db: Session):
    """
    Convert a numerical score to its display representation based on settings.
    """
    display_option = db.query(MarkDisplayOption).filter(
        MarkDisplayOption.id == display_option_id
    ).first()
    
    if not display_option:
        return str(score)  # Default fallback
    
    if display_option.display_type == 'hidden':
        return None
    
    elif display_option.display_type == 'numeric':
        return f"{score:.1f}"
    
    elif display_option.display_type == 'icon':
        if display_option.icon_type == 'bullseye':
            if score >= 90:
                return {
                    'icon': 'bullseye-center',
                    'label': 'Outstanding',
                    'class': 'icon-outstanding'
                }
            elif score >= 70:
                return {
                    'icon': 'bullseye-middle',
                    'label': 'Good Progress',
                    'class': 'icon-good'
                }
            else:
                return {
                    'icon': 'bullseye-outer',
                    'label': 'Needs Work',
                    'class': 'icon-needs-work'
                }
                
        elif display_option.icon_type == 'track':
            if score >= 90:
                return {
                    'icon': 'track-ahead',
                    'label': 'Ahead of Track',
                    'class': 'icon-ahead'
                }
            elif score >= 70:
                return {
                    'icon': 'track-on',
                    'label': 'On Track',
                    'class': 'icon-on-track'
                }
            else:
                return {
                    'icon': 'track-behind',
                    'label': 'Behind Track',
                    'class': 'icon-behind'
                }
                
        elif display_option.icon_type == 'first-aid':
            if score >= 90:
                return {
                    'icon': 'checkmark',
                    'label': 'Excellent',
                    'class': 'icon-excellent'
                }
            elif score >= 70:
                return {
                    'icon': 'bandage',
                    'label': 'Minor Fixes',
                    'class': 'icon-minor'
                }
            else:
                return {
                    'icon': 'first-aid',
                    'label': 'Needs Attention',
                    'class': 'icon-attention'
                }
    
    # Fallback
    return str(score)
```

## 5.4 Draft Comparison

```python
def get_draft_comparison(student_id: int, assignment_id: int, db: Session):
    """
    Compare feedback across multiple drafts of the same assignment.
    """
    # Fetch drafts for this student and assignment
    drafts = db.query(Draft).filter(
        Draft.student_id == student_id, 
        Draft.assignment_id == assignment_id
    ).order_by(Draft.version).all()
    
    comparison_data = []
    for draft in drafts:
        # Get the aggregated feedback and scores for this draft
        feedback_history = db.query(FeedbackHistory).filter(
            FeedbackHistory.draft_id == draft.id
        ).first()
        
        if not feedback_history:
            continue
            
        aggregated_feedback = db.query(AggregatedFeedback).filter(
            AggregatedFeedback.feedback_history_id == feedback_history.id
        ).all()
        
        # Organize by category
        category_scores = {}
        for feedback in aggregated_feedback:
            category = db.query(RubricCategory).get(feedback.category_id)
            category_scores[category.name] = {
                'score': feedback.aggregated_score,
                'feedback': feedback.feedback_text
            }
        
        comparison_data.append({
            'draft_version': draft.version,
            'submission_date': draft.submission_date,
            'overall_score': feedback_history.aggregated_score,
            'category_scores': category_scores
        })
    
    # Calculate improvements between drafts
    for i in range(1, len(comparison_data)):
        current = comparison_data[i]
        previous = comparison_data[i-1]
        
        current['score_improvement'] = current['overall_score'] - previous['overall_score']
        current['category_improvements'] = {}
        
        for category, data in current['category_scores'].items():
            if category in previous['category_scores']:
                current['category_improvements'][category] = {
                    'score_change': data['score'] - previous['category_scores'][category]['score'],
                    'resolved_issues': identify_resolved_issues(
                        previous['category_scores'][category]['feedback'],
                        data['feedback']
                    )
                }
    
    return comparison_data# 6. API Integration

## 6.1 AI Model Integration

```python
import openai
import json
from typing import Dict, List, Any
from datetime import datetime

async def call_ai_api(ai_model: AIModel, prompt: str) -> Dict[str, Any]:
    """
    Call the AI API with the provided prompt.
    """
    # Parse API configuration from model
    config = json.loads(ai_model.api_config)
    
    if ai_model.api_provider.lower() == 'openai':
        return await call_openai_api(prompt, config)
    elif ai_model.api_provider.lower() == 'anthropic':
        return await call_anthropic_api(prompt, config)
    else:
        raise ValueError(f"Unsupported API provider: {ai_model.api_provider}")

async def call_openai_api(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the OpenAI API with the provided prompt.
    """
    # Set API key
    openai.api_key = config.get('api_key')
    
    try:
        response = await openai.ChatCompletion.create(
            model=config.get('model', 'gpt-4'),
            messages=[
                {"role": "system", "content": config.get('system_prompt', 'You are an educational feedback assistant.')},
                {"role": "user", "content": prompt}
            ],
            temperature=config.get('temperature', 0.2),
            max_tokens=config.get('max_tokens', 2000)
        )
        
        return {
            'text': response.choices[0].message.content,
            'confidence': 1.0 - response.choices[0].finish_reason == 'length',
            'metadata': {
                'model': response.model,
                'usage': response.usage.to_dict() if hasattr(response, 'usage') else {},
                'finish_reason': response.choices[0].finish_reason
            }
        }
    except Exception as e:
        # Log the error
        print(f"Error calling OpenAI API: {str(e)}")
        raise

def create_assessment_prompt(assignment: Assignment, rubric_categories: List[RubricCategory], draft_content: str) -> str:
    """
    Create a prompt for the AI model to assess a draft.
    """
    # Build the instruction part
    instruction = (
        f"You are an expert educational assessor evaluating a student submission. "
        f"Please provide detailed, constructive feedback on the following {assignment.title} submission. "
        f"Analyze the work according to the rubric categories below. "
        f"For each category, provide a score and specific feedback highlighting strengths and areas for improvement."
    )
    
    # Build the rubric part
    rubric_text = "RUBRIC:\n"
    for category in rubric_categories:
        rubric_text += f"- {category.name} (Weight: {category.weight}%): {category.description}\n"
    
    # Build the response format instructions
    response_format = """
    RESPONSE FORMAT:
    Please structure your response in the following JSON format:
    {
        "overall_feedback": "A summary of the overall assessment",
        "category_scores": [
            {
                "category_name": "Name of category 1",
                "score": <numerical score 0-100>,
                "confidence": <your confidence in this score 0-1>,
                "strengths": ["Specific strength 1", "Specific strength 2"],
                "improvements": ["Specific improvement area 1", "Specific improvement area 2"]
            },
            // Additional categories...
        ],
        "general_strengths": ["Overall strength 1", "Overall strength 2"],
        "general_improvements": ["Overall improvement 1", "Overall improvement 2"]
    }
    """
    
    # Combine all parts into a complete prompt
    complete_prompt = f"{instruction}\n\n{rubric_text}\n\n{response_format}\n\nSTUDENT SUBMISSION:\n{draft_content}"
    
    return complete_prompt

def process_ai_response(ai_response: Dict[str, Any], model_run_id: int, rubric_categories: List[RubricCategory], db: Session):
    """
    Process and store AI response for a model run.
    """
    try:
        # Parse the response text as JSON
        response_data = json.loads(ai_response['text'])
        
        # Process category scores
        for category_score_data in response_data.get('category_scores', []):
            # Find matching rubric category
            category_name = category_score_data.get('category_name')
            category = next((c for c in rubric_categories if c.name == category_name), None)
            
            if not category:
                continue
                
            # Store category score
            category_score = CategoryScore(
                modelrun_id=model_run_id,
                category_id=category.id,
                score=category_score_data.get('score', 0),
                confidence=category_score_data.get('confidence', 0.5)
            )
            db.add(category_score)
            
            # Store strengths as feedback items
            for strength in category_score_data.get('strengths', []):
                feedback_item = FeedbackItem(
                    modelrun_id=model_run_id,
                    type='category_strength',
                    content=strength,
                    is_strength=True,
                    is_aggregated=False
                )
                db.add(feedback_item)
                
            # Store improvement areas as feedback items
            for improvement in category_score_data.get('improvements', []):
                feedback_item = FeedbackItem(
                    modelrun_id=model_run_id,
                    type='category_improvement',
                    content=improvement,
                    is_strength=False,
                    is_aggregated=False
                )
                db.add(feedback_item)
        
        # Store general strengths
        for strength in response_data.get('general_strengths', []):
            feedback_item = FeedbackItem(
                modelrun_id=model_run_id,
                type='general_strength',
                content=strength,
                is_strength=True,
                is_aggregated=False
            )
            db.add(feedback_item)
            
        # Store general improvements
        for improvement in response_data.get('general_improvements', []):
            feedback_item = FeedbackItem(
                modelrun_id=model_run_id,
                type='general_improvement',
                content=improvement,
                is_strength=False,
                is_aggregated=False
            )
            db.add(feedback_item)
            
        # Store overall feedback
        overall_feedback = FeedbackItem(
            modelrun_id=model_run_id,
            type='overall',
            content=response_data.get('overall_feedback', ''),
            is_strength=None,
            is_aggregated=False
        )
        db.add(overall_feedback)
        
        db.commit()
        
    except json.JSONDecodeError:
        # Handle case where AI didn't return proper JSON
        error_feedback = FeedbackItem(
            modelrun_id=model_run_id,
            type='error',
            content="The AI model did not return properly formatted feedback. Please contact your instructor.",
            is_strength=False,
            is_aggregated=False
        )
        db.add(error_feedback)
        db.commit()
        
    except Exception as e:
        # Log the error and store a generic error message
        print(f"Error processing AI response: {str(e)}")
        error_feedback = FeedbackItem(
            modelrun_id=model_run_id,
            type='error',
            content="An error occurred while processing the feedback. Please contact your instructor.",
            is_strength=False,
            is_aggregated=False
        )
        db.add(error_feedback)
        db.commit()

def apply_aggregation_method(scores: List[float], confidences: List[float], method: str) -> float:
    """
    Apply the specified aggregation method to the scores.
    """
    if not scores:
        return 0.0
        
    if method.lower() == 'mean':
        return sum(scores) / len(scores)
        
    elif method.lower() == 'weighted_mean':
        if not confidences or len(confidences) != len(scores):
            return sum(scores) / len(scores)
            
        total_weight = sum(confidences)
        if total_weight == 0:
            return sum(scores) / len(scores)
            
        weighted_sum = sum(score * confidence for score, confidence in zip(scores, confidences))
        return weighted_sum / total_weight
        
    elif method.lower() == 'median':
        sorted_scores = sorted(scores)
        mid = len(sorted_scores) // 2
        if len(sorted_scores) % 2 == 0:
            return (sorted_scores[mid-1] + sorted_scores[mid]) / 2
        else:
            return sorted_scores[mid]
            
    elif method.lower() == 'trimmed_mean':
        # Remove highest and lowest scores if we have more than 2 scores
        if len(scores) <= 2:
            return sum(scores) / len(scores)
            
        sorted_scores = sorted(scores)
        trimmed_scores = sorted_scores[1:-1]
        return sum(trimmed_scores) / len(trimmed_scores)
    
    # Default to mean if method not recognized
    return sum(scores) / len(scores)

def aggregate_feedback_text(model_runs: List[ModelRun], category_id: int, db: Session) -> str:
    """
    Aggregate feedback text from multiple model runs for a specific category.
    """
    # Get all feedback items for this category from all runs
    strengths = []
    improvements = []
    
    for run in model_runs:
        # Get strengths
        strength_items = db.query(FeedbackItem).filter(
            FeedbackItem.modelrun_id == run.id,
            FeedbackItem.type == 'category_strength',
            # We would need additional filtering or metadata to link to specific category
        ).all()
        
        strengths.extend([item.content for item in strength_items])
        
        # Get improvements
        improvement_items = db.query(FeedbackItem).filter(
            FeedbackItem.modelrun_id == run.id,
            FeedbackItem.type == 'category_improvement',
            # We would need additional filtering or metadata to link to specific category
        ).all()
        
        improvements.extend([item.content for item in improvement_items])
    
    # Remove duplicates and near-duplicates
    unique_strengths = remove_duplicates(strengths)
    unique_improvements = remove_duplicates(improvements)
    
    # Format the aggregated feedback
    feedback_text = "Strengths:\n"
    for strength in unique_strengths[:3]:  # Limit to top 3 strengths
        feedback_text += f"- {strength}\n"
        
    feedback_text += "\nAreas for Improvement:\n"
    for improvement in unique_improvements[:3]:  # Limit to top 3 improvements
        feedback_text += f"- {improvement}\n"
    
    return feedback_text

def remove_duplicates(items: List[str]) -> List[str]:
    """
    Remove duplicate or very similar items from a list of strings.
    """
    # For MVP, we'll use a simple approach just removing exact duplicates
    return list(dict.fromkeys(items))

def calculate_weighted_overall_score(feedback_history_id: int, db: Session) -> float:
    """
    Calculate the overall weighted score from aggregated category scores.
    """
    # Get all aggregated feedback for this feedback history
    aggregated_feedbacks = db.query(AggregatedFeedback).filter(
        AggregatedFeedback.feedback_history_id == feedback_history_id
    ).all()
    
    if not aggregated_feedbacks:
        return 0.0
    
    total_weight = 0.0
    weighted_sum = 0.0
    
    for agg_feedback in aggregated_feedbacks:
        # Get the category to determine its weight
        category = db.query(RubricCategory).get(agg_feedback.category_id)
        if not category:
            continue
            
        weight = category.weight
        total_weight += weight
        weighted_sum += agg_feedback.aggregated_score * weight
    
    if total_weight == 0:
        return 0.0
        
    return weighted_sum / total_weight

def identify_resolved_issues(previous_feedback: str, current_feedback: str) -> List[str]:
    """
    Identify issues that were mentioned in previous feedback but not in current feedback.
    """
    # For the MVP, we'll use a simple approach
    # This can be enhanced with NLP in future versions
    
    # Extract improvement areas from previous feedback
    prev_improvements = []
    lines = previous_feedback.split('\n')
    in_improvements_section = False
    
    for line in lines:
        if "Areas for Improvement" in line:
            in_improvements_section = True
            continue
        
        if in_improvements_section and line.strip().startswith('-'):
            prev_improvements.append(line.strip()[2:].strip())  # Remove the "- " prefix
    
    # Extract improvement areas from current feedback
    current_improvements = []
    lines = current_feedback.split('\n')
    in_improvements_section = False
    
    for line in lines:
        if "Areas for Improvement" in line:
            in_improvements_section = True
            continue
        
        if in_improvements_section and line.strip().startswith('-'):
            current_improvements.append(line.strip()[2:].strip())  # Remove the "- " prefix
    
    # Find improvements that were in previous feedback but not in current
    resolved_issues = []
    
    for prev_issue in prev_improvements:
        # Check if this issue is mentioned in current improvements
        # This is a simplistic check - in a real system, you'd use semantic matching
        if not any(prev_issue.lower() in curr_issue.lower() for curr_issue in current_improvements):
            resolved_issues.append(prev_issue)
    
    return resolved_issues
```
# 7. API Endpoints

## 7.1 Auth Endpoints

```python
@app.post("/api/auth/login")
async def login(credentials: UserCredentials):
    """
    Authenticate user and return token.
    """
    # Validate credentials
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer", "role": user.role}

@app.post("/api/auth/register")
async def register(user_data: UserRegistration):
    """
    Register a new user.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    
    # Create role-specific record
    if user_data.role == "student":
        student = Student(user_id=new_user.id)
        db.add(student)
        db.commit()
    elif user_data.role == "instructor":
        instructor = Instructor(user_id=new_user.id, department=user_data.department)
        db.add(instructor)
        db.commit()
    
    return {"id": new_user.id, "email": new_user.email, "role": new_user.role}
```

## 7.2 Student Endpoints

```python
@app.get("/api/student/assignments")
async def get_student_assignments(current_user: User = Depends(get_current_user)):
    """
    Get all assignments for the current student.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Get courses the student is enrolled in
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.id).all()
    course_ids = [enrollment.course_id for enrollment in enrollments]
    
    # Get assignments for these courses
    assignments = db.query(Assignment).filter(Assignment.course_id.in_(course_ids)).all()
    
    # Get submission status for each assignment
    result = []
    for assignment in assignments:
        # Get the latest draft for this assignment
        latest_draft = db.query(Draft).filter(
            Draft.assignment_id == assignment.id,
            Draft.student_id == student.id
        ).order_by(Draft.version.desc()).first()
        
        # Get the course for this assignment
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        
        assignment_data = {
            "id": assignment.id,
            "title": assignment.title,
            "course_code": course.code if course else "Unknown",
            "course_title": course.title if course else "Unknown",
            "due_date": assignment.due_date.isoformat(),
            "max_drafts": assignment.max_drafts,
            "current_draft": latest_draft.version if latest_draft else 0,
            "submission_status": "Submitted" if latest_draft else "Not Started",
            "last_submission_date": latest_draft.submission_date.isoformat() if latest_draft else None
        }
        result.append(assignment_data)
    
    return result

@app.get("/api/student/assignments/{assignment_id}")
async def get_student_assignment_details(
    assignment_id: int, 
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific assignment.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Get assignment
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify student is enrolled in this course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.course_id == course.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get drafts for this assignment
    drafts = db.query(Draft).filter(
        Draft.assignment_id == assignment_id,
        Draft.student_id == student.id
    ).order_by(Draft.version).all()
    
    # Get rubric information
    rubric = db.query(Rubric).filter(Rubric.assignment_id == assignment_id).first()
    rubric_categories = []
    if rubric:
        categories = db.query(RubricCategory).filter(RubricCategory.rubric_id == rubric.id).all()
        rubric_categories = [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "weight": category.weight
            }
            for category in categories
        ]
    
    # Format draft information
    draft_data = []
    for draft in drafts:
        # Get feedback history for this draft
        feedback_history = db.query(FeedbackHistory).filter(FeedbackHistory.draft_id == draft.id).first()
        
        # Only include feedback if it has been released
        feedback_available = feedback_history and feedback_history.release_date and feedback_history.release_date <= datetime.now()
        
        draft_info = {
            "id": draft.id,
            "version": draft.version,
            "submission_date": draft.submission_date.isoformat(),
            "feedback_available": feedback_available,
            "feedback_id": feedback_history.id if feedback_available else None
        }
        draft_data.append(draft_info)
    
    # Format result
    result = {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "course_code": course.code,
        "course_title": course.title,
        "due_date": assignment.due_date.isoformat(),
        "max_drafts": assignment.max_drafts,
        "current_draft_count": len(drafts),
        "can_submit_new_draft": len(drafts) < assignment.max_drafts and assignment.due_date > datetime.now(),
        "drafts": draft_data,
        "rubric_categories": rubric_categories
    }
    
    return result

@app.post("/api/student/drafts")
async def submit_draft(
    draft_data: DraftSubmission,
    current_user: User = Depends(get_current_user)
):
    """
    Submit a new draft for an assignment.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Get assignment
    assignment = db.query(Assignment).filter(Assignment.id == draft_data.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check due date
    if assignment.due_date < datetime.now():
        raise HTTPException(status_code=400, detail="Assignment due date has passed")
    
    # Verify student is enrolled in this course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.course_id == course.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Check how many drafts have been submitted
    existing_drafts = db.query(Draft).filter(
        Draft.assignment_id == assignment.id,
        Draft.student_id == student.id
    ).count()
    
    if existing_drafts >= assignment.max_drafts:
        raise HTTPException(status_code=400, detail="Maximum number of drafts already submitted")
    
    # Get next draft version
    next_version = existing_drafts + 1
    
    # Create new draft record
    new_draft = Draft(
        assignment_id=assignment.id,
        student_id=student.id,
        version=next_version,
        submission_date=datetime.now()
    )
    db.add(new_draft)
    db.commit()
    
    # Store draft content temporarily
    await store_draft_content(new_draft.id, draft_data.content)
    
    # Process draft (this will be async in a real implementation)
    background_tasks.add_task(process_draft_submission, new_draft.id, db)
    
    return {"id": new_draft.id, "version": next_version, "message": "Draft submitted successfully"}

@app.get("/api/student/feedback/{feedback_id}")
async def get_feedback(
    feedback_id: int, 
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback for a specific draft.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Get feedback history
    feedback_history = db.query(FeedbackHistory).filter(FeedbackHistory.id == feedback_id).first()
    if not feedback_history:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check if feedback has been released
    if not feedback_history.release_date or feedback_history.release_date > datetime.now():
        raise HTTPException(status_code=403, detail="Feedback not yet released")
    
    # Get draft information
    draft = db.query(Draft).filter(Draft.id == feedback_history.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Verify this draft belongs to the student
    if draft.student_id != student.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this feedback")
    
    # Get assignment settings for mark display
    assignment = db.query(Assignment).filter(Assignment.id == draft.assignment_id).first()
    settings = db.query(AssignmentSettings).filter(AssignmentSettings.assignment_id == assignment.id).first()
    
    # Get aggregated feedback
    aggregated_feedback = db.query(AggregatedFeedback).filter(
        AggregatedFeedback.feedback_history_id == feedback_id
    ).all()
    
    # Format the response with appropriate mark display
    category_feedback = []
    for feedback in aggregated_feedback:
        category = db.query(RubricCategory).filter(RubricCategory.id == feedback.category_id).first()
        
        # Apply mark display formatting
        display_score = get_mark_display(feedback.aggregated_score, settings.mark_display_option_id, db)
        
        category_feedback.append({
            "category_name": category.name if category else "Unknown",
            "category_description": category.description if category else "",
            "weight": category.weight if category else 0,
            "score": display_score,
            "raw_score": feedback.aggregated_score if display_score else None,
            "feedback_text": feedback.feedback_text
        })
    
    # Get overall strengths and improvement areas
    strengths = []
    improvements = []
    
    # If this isn't the first draft, get comparison with previous drafts
    previous_draft = None
    if draft.version > 1:
        previous_draft = db.query(Draft).filter(
            Draft.assignment_id == draft.assignment_id,
            Draft.student_id == draft.student_id,
            Draft.version == draft.version - 1
        ).first()
    
    comparison_data = None
    if previous_draft:
        comparison_data = get_draft_comparison(student.id, draft.assignment_id, db)
    
    # Format the response
    result = {
        "id": feedback_id,
        "draft_version": draft.version,
        "submission_date": draft.submission_date.isoformat(),
        "overall_score": get_mark_display(feedback_history.aggregated_score, settings.mark_display_option_id, db),
        "raw_overall_score": feedback_history.aggregated_score,
        "category_feedback": category_feedback,
        "general_strengths": strengths,
        "general_improvements": improvements,
        "comparison_with_previous": comparison_data
    }
    
    return result

@app.get("/api/student/progress/{assignment_id}")
async def get_progress(
    assignment_id: int, 
    current_user: User = Depends(get_current_user)
):
    """
    Get progress tracking for all drafts of an assignment.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Get all drafts for this assignment
    drafts = db.query(Draft).filter(
        Draft.assignment_id == assignment_id,
        Draft.student_id == student.id
    ).order_by(Draft.version).all()
    
    if not drafts:
        raise HTTPException(status_code=404, detail="No drafts found for this assignment")
    
    # Get feedback history for each draft
    progress_data = []
    previous_scores = {}
    
    for draft in drafts:
        feedback_history = db.query(FeedbackHistory).filter(
            FeedbackHistory.draft_id == draft.id
        ).first()
        
        if not feedback_history or not feedback_history.release_date or feedback_history.release_date > datetime.now():
            continue
        
        # Get category scores
        category_progress = []
        aggregated_feedback = db.query(AggregatedFeedback).filter(
            AggregatedFeedback.feedback_history_id == feedback_history.id
        ).all()
        
        for feedback in aggregated_feedback:
            category = db.query(RubricCategory).filter(RubricCategory.id == feedback.category_id).first()
            if not category:
                continue
                
            previous_score = previous_scores.get(category.name, None)
            improvement = None
            if previous_score is not None:
                improvement = feedback.aggregated_score - previous_score
                
            category_progress.append({
                "category_name": category.name,
                "score": feedback.aggregated_score,
                "previous_score": previous_score,
                "improvement": improvement
            })
            
            # Update for next draft
            previous_scores[category.name] = feedback.aggregated_score
        
        # Add to progress data
        progress_data.append({
            "draft_version": draft.version,
            "submission_date": draft.submission_date.isoformat(),
            "overall_score": feedback_history.aggregated_score,
            "category_progress": category_progress
        })
    
    return progress_data# 7.4 Configuration Endpoints

```python
@app.get("/api/config/ai-models")
async def get_ai_models(current_user: User = Depends(get_current_user)):
    """
    Get available AI models.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    models = db.query(AIModel).filter(AIModel.active == True).all()
    
    result = []
    for model in models:
        result.append({
            "id": model.id,
            "name": model.name,
            "api_provider": model.api_provider,
            "version": model.version
        })
    
    return result

@app.get("/api/config/aggregation-methods")
async def get_aggregation_methods(current_user: User = Depends(get_current_user)):
    """
    Get available aggregation methods.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    methods = db.query(AggregationMethod).filter(AggregationMethod.is_active == True).all()
    
    result = []
    for method in methods:
        result.append({
            "id": method.id,
            "name": method.name,
            "description": method.description
        })
    
    return result

@app.get("/api/config/feedback-styles")
async def get_feedback_styles(current_user: User = Depends(get_current_user)):
    """
    Get available feedback styles.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    styles = db.query(FeedbackStyle).filter(FeedbackStyle.is_active == True).all()
    
    result = []
    for style in styles:
        result.append({
            "id": style.id,
            "name": style.name,
            "description": style.description
        })
    
    return result

@app.get("/api/config/mark-display-options")
async def get_mark_display_options(current_user: User = Depends(get_current_user)):
    """
    Get available mark display options.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    options = db.query(MarkDisplayOption).filter(MarkDisplayOption.is_active == True).all()
    
    result = []
    for option in options:
        result.append({
            "id": option.id,
            "name": option.name,
            "display_type": option.display_type,
            "description": option.description,
            "icon_type": option.icon_type
        })
    
    return result# 7.3 Instructor Endpoints

```python
@app.get("/api/instructor/courses")
async def get_instructor_courses(current_user: User = Depends(get_current_user)):
    """
    Get all courses for the current instructor.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get courses
    courses = db.query(Course).filter(Course.instructor_id == instructor.id).all()
    
    result = []
    for course in courses:
        # Get student count
        student_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
        
        # Get assignment count
        assignment_count = db.query(Assignment).filter(Assignment.course_id == course.id).count()
        
        course_data = {
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "term": course.term,
            "department": course.department,
            "student_count": student_count,
            "assignment_count": assignment_count
        }
        result.append(course_data)
    
    return result

@app.post("/api/instructor/courses")
async def create_course(
    course_data: CourseCreation,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new course.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Create course
    new_course = Course(
        code=course_data.code,
        title=course_data.title,
        term=course_data.term,
        department=course_data.department or instructor.department,
        instructor_id=instructor.id
    )
    db.add(new_course)
    db.commit()
    
    return {
        "id": new_course.id,
        "code": new_course.code,
        "title": new_course.title,
        "term": new_course.term,
        "department": new_course.department
    }

@app.get("/api/instructor/courses/{course_id}")
async def get_course_details(
    course_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific course.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor owns this course
    if course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this course")
    
    # Get assignments
    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()
    assignment_data = []
    
    for assignment in assignments:
        # Get submission stats
        total_submissions = db.query(Draft).join(Student).join(Enrollment).filter(
            Draft.assignment_id == assignment.id,
            Enrollment.course_id == course_id
        ).count()
        
        unique_students = db.query(Student).join(Draft).filter(
            Draft.assignment_id == assignment.id
        ).distinct().count()
        
        assignment_info = {
            "id": assignment.id,
            "title": assignment.title,
            "due_date": assignment.due_date.isoformat(),
            "max_drafts": assignment.max_drafts,
            "submission_count": total_submissions,
            "student_count": unique_students
        }
        assignment_data.append(assignment_info)
    
    # Get students
    students = db.query(Student).join(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    student_data = []
    for student in students:
        user = db.query(User).filter(User.id == student.user_id).first()
        student_info = {
            "id": student.id,
            "name": user.name if user else "Unknown",
            "email": user.email if user else "Unknown"
        }
        student_data.append(student_info)
    
    result = {
        "id": course.id,
        "code": course.code,
        "title": course.title,
        "term": course.term,
        "department": course.department,
        "assignments": assignment_data,
        "students": student_data
    }
    
    return result

@app.post("/api/instructor/assignments")
async def create_assignment(
    assignment_data: AssignmentCreation,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new assignment.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get course
    course = db.query(Course).filter(Course.id == assignment_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor owns this course
    if course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to create assignments for this course")
    
    # Create assignment
    new_assignment = Assignment(
        course_id=course.id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date,
        max_drafts=assignment_data.max_drafts,
        created_by=instructor.id
    )
    db.add(new_assignment)
    db.commit()
    
    # Create rubric
    new_rubric = Rubric(assignment_id=new_assignment.id)
    db.add(new_rubric)
    db.commit()
    
    # Create rubric categories
    for category_data in assignment_data.rubric_categories:
        category = RubricCategory(
            rubric_id=new_rubric.id,
            name=category_data.name,
            description=category_data.description,
            weight=category_data.weight
        )
        db.add(category)
    
    # Create assignment settings
    default_ai_model = db.query(AIModel).filter(AIModel.active == True).first()
    default_aggregation = db.query(AggregationMethod).filter(AggregationMethod.name == "mean").first()
    default_feedback_style = db.query(FeedbackStyle).filter(FeedbackStyle.name == "balanced").first()
    default_mark_display = db.query(MarkDisplayOption).filter(MarkDisplayOption.display_type == "numeric").first()
    
    settings = AssignmentSettings(
        assignment_id=new_assignment.id,
        ai_model_id=assignment_data.ai_model_id or default_ai_model.id,
        num_runs=assignment_data.num_runs or 3,
        aggregation_method_id=assignment_data.aggregation_method_id or default_aggregation.id,
        feedback_style_id=assignment_data.feedback_style_id or default_feedback_style.id,
        require_review=assignment_data.require_review,
        mark_display_option_id=assignment_data.mark_display_option_id or default_mark_display.id
    )
    db.add(settings)
    db.commit()
    
    return {
        "id": new_assignment.id,
        "title": new_assignment.title,
        "due_date": new_assignment.due_date.isoformat(),
        "max_drafts": new_assignment.max_drafts,
        "message": "Assignment created successfully"
    }

@app.get("/api/instructor/assignments/{assignment_id}/submissions")
async def get_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get all submissions for a specific assignment.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get assignment
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor owns this course
    if course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to view submissions for this course")
    
    # Get all students in the course
    students = db.query(Student).join(Enrollment).filter(
        Enrollment.course_id == course.id
    ).all()
    
    result = []
    for student in students:
        user = db.query(User).filter(User.id == student.user_id).first()
        
        # Get all drafts for this student
        drafts = db.query(Draft).filter(
            Draft.assignment_id == assignment_id,
            Draft.student_id == student.id
        ).order_by(Draft.version).all()
        
        draft_data = []
        for draft in drafts:
            # Get feedback history
            feedback_history = db.query(FeedbackHistory).filter(
                FeedbackHistory.draft_id == draft.id
            ).first()
            
            status = "Submitted"
            if feedback_history:
                if feedback_history.instructor_reviewed:
                    status = "Reviewed"
                if feedback_history.release_date and feedback_history.release_date <= datetime.now():
                    status = "Released"
            
            draft_info = {
                "id": draft.id,
                "version": draft.version,
                "submission_date": draft.submission_date.isoformat(),
                "status": status,
                "feedback_id": feedback_history.id if feedback_history else None,
                "requires_review": feedback_history and not feedback_history.instructor_reviewed if feedback_history else False
            }
            draft_data.append(draft_info)
        
        student_data = {
            "student_id": student.id,
            "name": user.name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "drafts": draft_data,
            "draft_count": len(drafts),
            "latest_submission": drafts[-1].submission_date.isoformat() if drafts else None
        }
        result.append(student_data)
    
    return result

@app.get("/api/instructor/feedback/{feedback_id}")
async def get_instructor_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback details for instructor review.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get feedback history
    feedback_history = db.query(FeedbackHistory).filter(FeedbackHistory.id == feedback_id).first()
    if not feedback_history:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Get draft
    draft = db.query(Draft).filter(Draft.id == feedback_history.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Get assignment
    assignment = db.query(Assignment).filter(Assignment.id == draft.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor owns this course
    if course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this feedback")
    
    # Get student information
    student = db.query(Student).filter(Student.id == draft.student_id).first()
    student_user = db.query(User).filter(User.id == student.user_id).first() if student else None
    
    # Get aggregated feedback
    aggregated_feedback = db.query(AggregatedFeedback).filter(
        AggregatedFeedback.feedback_history_id == feedback_id
    ).all()
    
    # Get individual model runs for this draft
    model_runs = db.query(ModelRun).filter(ModelRun.draft_id == draft.id).all()
    
    # Format model run data
    model_run_data = []
    for run in model_runs:
        # Get AI model info
        model = db.query(AIModel).filter(AIModel.id == run.model_id).first()
        
        # Get category scores
        scores = db.query(CategoryScore).filter(CategoryScore.modelrun_id == run.id).all()
        score_data = []
        
        for score in scores:
            category = db.query(RubricCategory).filter(RubricCategory.id == score.category_id).first()
            score_data.append({
                "category_name": category.name if category else "Unknown",
                "score": score.score,
                "confidence": score.confidence
            })
        
        # Get feedback items
        feedback_items = db.query(FeedbackItem).filter(FeedbackItem.modelrun_id == run.id).all()
        feedback_data = {
            "strengths": [],
            "improvements": [],
            "overall": ""
        }
        
        for item in feedback_items:
            if item.type == 'overall':
                feedback_data["overall"] = item.content
            elif item.is_strength:
                feedback_data["strengths"].append(item.content)
            else:
                feedback_data["improvements"].append(item.content)
        
        model_run_data.append({
            "run_id": run.id,
            "run_number": run.run_number,
            "model_name": model.name if model else "Unknown",
            "timestamp": run.timestamp.isoformat(),
            "scores": score_data,
            "feedback": feedback_data
        })
    
    # Format aggregated feedback data
    aggregated_data = []
    for feedback in aggregated_feedback:
        category = db.query(RubricCategory).filter(RubricCategory.id == feedback.category_id).first()
        aggregated_data.append({
            "category_name": category.name if category else "Unknown",
            "aggregated_score": feedback.aggregated_score,
            "feedback_text": feedback.feedback_text,
            "edited_by_instructor": feedback.edited_by_instructor,
            "category_id": feedback.category_id
        })
    
    result = {
        "feedback_id": feedback_id,
        "draft_id": draft.id,
        "assignment_title": assignment.title,
        "course_code": course.code,
        "draft_version": draft.version,
        "submission_date": draft.submission_date.isoformat(),
        "student_name": student_user.name if student_user else "Unknown",
        "student_email": student_user.email if student_user else "Unknown",
        "overall_score": feedback_history.aggregated_score,
        "instructor_reviewed": feedback_history.instructor_reviewed,
        "release_date": feedback_history.release_date.isoformat() if feedback_history.release_date else None,
        "aggregated_feedback": aggregated_data,
        "model_runs": model_run_data
    }
    
    return result

@app.post("/api/instructor/feedback/{feedback_id}/review")
async def review_feedback(
    feedback_id: int,
    review_data: FeedbackReview,
    current_user: User = Depends(get_current_user)
):
    """
    Review and potentially edit feedback before release to student.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get feedback history
    feedback_history = db.query(FeedbackHistory).filter(FeedbackHistory.id == feedback_id).first()
    if not feedback_history:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Verify ownership through course chain
    draft = db.query(Draft).filter(Draft.id == feedback_history.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    assignment = db.query(Assignment).filter(Assignment.id == draft.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course or course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to review this feedback")
    
    # Update overall score if provided
    if review_data.overall_score is not None:
        feedback_history.aggregated_score = review_data.overall_score
    
    # Update category feedback if provided
    if review_data.category_feedback:
        for category_update in review_data.category_feedback:
            # Find the aggregated feedback for this category
            agg_feedback = db.query(AggregatedFeedback).filter(
                AggregatedFeedback.feedback_history_id == feedback_id,
                AggregatedFeedback.category_id == category_update.category_id
            ).first()
            
            if not agg_feedback:
                continue
                
            # Update score if provided
            if category_update.score is not None:
                agg_feedback.aggregated_score = category_update.score
                
            # Update feedback text if provided
            if category_update.feedback_text:
                agg_feedback.feedback_text = category_update.feedback_text
                agg_feedback.edited_by_instructor = True
    
    # Mark as reviewed
    feedback_history.instructor_reviewed = True
    feedback_history.instructor_id = instructor.id
    
    # Set release date if requested
    if review_data.release_now:
        feedback_history.release_date = datetime.now()
    elif review_data.release_date:
        feedback_history.release_date = review_data.release_date
    
    db.commit()
    
    return {
        "feedback_id": feedback_id,
        "message": "Feedback reviewed successfully",
        "release_status": "Released" if feedback_history.release_date and feedback_history.release_date <= datetime.now() else "Scheduled" if feedback_history.release_date else "Not Released"
    }

@app.post("/api/instructor/students/import")
async def import_students(
    course_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Import students into a course via CSV or TSV file.
    """
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Not an instructor")
    
    # Get instructor record
    instructor = db.query(Instructor).filter(Instructor.user_id == current_user.id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor record not found")
    
    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor owns this course
    if course.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="Not authorized to import students for this course")
    
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # Determine file format (CSV or TSV)
    delimiter = ',' if file.filename.endswith('.csv') else '\t'
    
    # Parse the file
    lines = content_str.strip().split('\n')
    header = lines[0].split(delimiter)
    
    # Validate header
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in [h.lower() for h in header]:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Process each line
    name_index = [h.lower() for h in header].index('name')
    email_index = [h.lower() for h in header].index('email')
    
    result = {
        "success_count": 0,
        "error_count": 0,
        "errors": []
    }
    
    for i in range(1, len(lines)):
        try:
            line = lines[i].split(delimiter)
            if len(line) <= max(name_index, email_index):
                result["errors"].append(f"Line {i+1}: Not enough fields")
                result["error_count"] += 1
                continue
                
            name = line[name_index].strip()
            email = line[email_index].strip()
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Create new user
                hashed_password = hash_password(generate_temporary_password())
                user = User(
                    email=email,
                    name=name,
                    password_hash=hashed_password,
                    role="student"
                )
                db.add(user)
                db.commit()
                
                # Create student record
                student = Student(user_id=user.id)
                db.add(student)
                db.commit()
            else:
                # Get student record
                student = db.query(Student).filter(Student.user_id == user.id).first()
                if not student:
                    if user.role != "student":
                        result["errors"].append(f"Line {i+1}: User exists but is not a student")
                        result["error_count"] += 1
                        continue
                        
                    # Create student record
                    student = Student(user_id=user.id)
                    db.add(student)
                    db.commit()
            
            # Check if already enrolled
            enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.course_id == course_id
            ).first()
            
            if not enrollment:
                # Create enrollment
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course_id
                )
                db.add(enrollment)
                db.commit()
                
            result["success_count"] += 1
                
        except Exception as e:
            result["errors"].append(f"Line {i+1}: {str(e)}")
            result["error_count"] += 1
    
    return result
```
# 8. Frontend Templates and Components

## 8.1 Student Dashboard

```html
<div class="dashboard">
  <h1>Welcome, {{ user.name }}</h1>
  
  <div class="upcoming-assignments">
    <h2>Upcoming Assignments</h2>
    <div class="assignment-cards">
      {% for assignment in upcoming_assignments %}
      <div class="assignment-card">
        <h3>{{ assignment.title }}</h3>
        <p class="course">{{ assignment.course_code }} - {{ assignment.course_title }}</p>
        <p class="due-date">Due: {{ format_date(assignment.due_date) }}</p>
        <div class="status-bar">
          <div class="draft-status">
            Draft {{ assignment.current_draft }}/{{ assignment.max_drafts }}
          </div>
          <div class="action-buttons">
            {% if assignment.current_draft > 0 %}
            <a href="/feedback/{{ assignment.latest_feedback_id }}" class="button">View Feedback</a>
            {% endif %}
            {% if assignment.can_submit_next_draft %}
            <a href="/submit/{{ assignment.id }}" class="button primary">Submit Draft</a>
            {% endif %}
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  
  <div class="recent-feedback">
    <h2>Recent Feedback</h2>
    <div class="feedback-list">
      {% for feedback in recent_feedback %}
      <div class="feedback-item">
        <div class="feedback-header">
          <h3>{{ feedback.assignment_title }}</h3>
          <p class="course">{{ feedback.course_code }}</p>
          <p class="draft">Draft {{ feedback.draft_version }}/{{ feedback.max_drafts }}</p>
        </div>
        <div class="feedback-summary">
          <div class="score-display">
            {% if feedback.display_score %}
            <div class="score {% if feedback.display_score.icon %}icon-{{ feedback.display_score.class }}{% endif %}">
              {% if feedback.display_score.icon %}
              <span class="icon">{{ feedback.display_score.icon }}</span>
              <span class="label">{{ feedback.display_score.label }}</span>
              {% else %}
              {{ feedback.display_score }}
              {% endif %}
            </div>
            {% endif %}
          </div>
          <div class="improvement">
            {% if feedback.improvement %}
            <span class="improvement-value {% if feedback.improvement > 0 %}positive{% elif feedback.improvement < 0 %}negative{% endif %}">
              {{ format_percentage(feedback.improvement) }}
            </span>
            {% endif %}
          </div>
        </div>
        <a href="/feedback/{{ feedback.id }}" class="view-full">View Full Feedback</a>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
```

## 8.2 Draft Submission Form

```html
<div class="submission-form">
  <h1>Submit Draft: {{ assignment.title }}</h1>
  <p class="course">{{ course.code }} - {{ course.title }}</p>
  
  <div class="draft-info">
    <p>Draft {{ next_draft_number }}/{{ assignment.max_drafts }}</p>
    <p>Due: {{ format_date(assignment.due_date) }}</p>
  </div>
  
  {% if previous_draft %}
  <div class="previous-draft-notice">
    <h3>Previous Feedback</h3>
    <p>You've already submitted Draft {{ previous_draft.version }}. 
       <a href="/feedback/{{ previous_draft.feedback_id }}">View feedback</a> before submitting your next draft.</p>
  </div>
  {% endif %}
  
  <form hx-post="/api/student/drafts" hx-swap="outerHTML">
    <input type="hidden" name="assignment_id" value="{{ assignment.id }}">
    
    <div class="form-group">
      <label for="content">Submission Content</label>
      <textarea id="content" name="content" rows="12" required></textarea>
    </div>
    
    <div class="submission-actions">
      <button type="button" onclick="window.history.back();" class="button secondary">Cancel</button>
      <button type="submit" class="button primary">Submit Draft</button>
    </div>
  </form>
</div>
```

## 8.3 Feedback Display Component

```html
<div class="feedback-display">
  <div class="feedback-header">
    <h1>{{ assignment.title }} - Feedback</h1>
    <p class="course">{{ course.code }} - {{ course.title }}</p>
    <p class="draft-info">Draft {{ draft.version }}/{{ assignment.max_drafts }}</p>
    <p class="submitted-date">Submitted: {{ format_date(draft.submission_date) }}</p>
  </div>
  
  <div class="overall-score">
    <h2>Overall Assessment</h2>
    <div class="score-display">
      {% if display_score %}
      <div class="score {% if display_score.icon %}icon-{{ display_score.class }}{% endif %}">
        {% if display_score.icon %}
        <span class="icon">{{ display_score.icon }}</span>
        <span class="label">{{ display_score.label }}</span>
        {% else %}
        {{ display_score }}
        {% endif %}
      </div>
      {% endif %}
    </div>
    
    {% if comparison_data and comparison_data.score_improvement %}
    <div class="improvement">
      <span class="improvement-value {% if comparison_data.score_improvement > 0 %}positive{% elif comparison_data.score_improvement < 0 %}negative{% endif %}">
        {{ format_percentage(comparison_data.score_improvement) }}
      </span>
      <span class="improvement-label">since previous draft</span>
    </div>
    {% endif %}
  </div>
  
  <div class="feedback-sections">
    <div class="strengths-section">
      <h3>Strengths</h3>
      <ul class="strength-list">
        {% for strength in general_strengths %}
        <li>{{ strength }}</li>
        {% endfor %}
      </ul>
    </div>
    
    <div class="improvements-section">
      <h3>Areas for Improvement</h3>
      <ul class="improvement-list">
        {% for improvement in general_improvements %}
        <li>{{ improvement }}</li>
        {% endfor %}
      </ul>
    </div>
  </div>
  
  <div class="rubric-feedback">
    <h2>Detailed Feedback by Category</h2>
    
    {% for category in category_feedback %}
    <div class="category-section">
      <div class="category-header">
        <h3>{{ category.category_name }}</h3>
        <div class="category-score">
          {% if category.display_score %}
          <span class="score">{{ category.display_score }}</span>
          {% endif %}
          
          {% if category.improvement %}
          <span class="improvement {% if category.improvement > 0 %}positive{% elif category.improvement < 0 %}negative{% endif %}">
            {{ format_percentage(category.improvement) }}
          </span>
          {% endif %}
        </div>
      </div>
      
      <div class="category-feedback">
        {{ category.feedback_text | safe }}
      </div>
    </div>
    {% endfor %}
  </div>
  
  {% if draft.version < assignment.max_drafts and assignment.due_date > now %}
  <div class="next-actions">
    <a href="/submit/{{ assignment.id }}" class="button primary">Submit Next Draft</a>
  </div>
  {% endif %}
</div>
```

## 8.4 Instructor Assignment Creation Form

```html
<div class="assignment-creation">
  <h1>Create New Assignment</h1>
  <p class="course">{{ course.code }} - {{ course.title }}</p>
  
  <div class="step-indicator">
    <div class="step {% if step == 1 %}active{% endif %}">Basic Details</div>
    <div class="step {% if step == 2 %}active{% endif %}">Specifications</div>
    <div class="step {% if step == 3 %}active{% endif %}">Rubric</div>
    <div class="step {% if step == 4 %}active{% endif %}">Feedback Settings</div>
    <div class="step {% if step == 5 %}active{% endif %}">Review</div>
  </div>
  
  <form hx-post="/api/instructor/assignments" hx-swap="outerHTML">
    <input type="hidden" name="course_id" value="{{ course.id }}">
    
    <!-- Step 1: Basic Details -->
    {% if step == 1 %}
    <div class="form-step">
      <div class="form-group">
        <label for="title">Assignment Title</label>
        <input type="text" id="title" name="title" required value="{{ draft.title }}">
      </div>
      
      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="6">{{ draft.description }}</textarea>
      </div>
      
      <div class="form-group">
        <label for="due_date">Due Date</label>
        <input type="datetime-local" id="due_date" name="due_date" required value="{{ draft.due_date }}">
      </div>
      
      <div class="form-group">
        <label for="max_drafts">Maximum Drafts</label>
        <input type="number" id="max_drafts" name="max_drafts" min="1" max="5" value="{{ draft.max_drafts or 3 }}">
      </div>
      
      <div class="step-actions">
        <button type="button" class="button secondary">Save as Draft</button>
        <button type="button" hx-get="/assignment/create/{{ course.id }}/2" hx-swap="outerHTML" class="button primary">Next</button>
      </div>
    </div>
    {% endif %}
    
    <!-- Step 2: Specifications -->
    {% if step == 2 %}
    <div class="form-step">
      <div class="form-group">
        <label>Upload Specifications Document</label>
        <div class="file-upload">
          <input type="file" id="spec_file" name="spec_file" accept=".pdf,.docx,.txt">
          <p class="or-divider">OR</p>
        </div>
      </div>
      
      <div class="form-group">
        <label for="spec_content">Create in Text Editor</label>
        <textarea id="spec_content" name="spec_content" rows="12">{{ draft.spec_content }}</textarea>
      </div>
      
      <div class="step-actions">
        <button type="button" hx-get="/assignment/create/{{ course.id }}/1" hx-swap="outerHTML" class="button">Back</button>
        <button type="button" class="button secondary">Save as Draft</button>
        <button type="button" hx-get="/assignment/create/{{ course.id }}/3" hx-swap="outerHTML" class="button primary">Next</button>
      </div>
    </div>
    {% endif %}
    
    <!-- Step 3: Rubric -->
    {% if step == 3 %}
    <div class="form-step">
      <div class="rubric-creation">
        <div class="rubric-options">
          <button type="button" class="button" id="create-manual">Create Manually</button>
          <button type="button" class="button" id="create-ai">Generate from Specifications</button>
        </div>
        
        <div class="rubric-categories">
          {% for category in draft.rubric_categories %}
          <div class="category-item">
            <div class="category-header">
              <input type="text" name="category_name[]" placeholder="Category Name" value="{{ category.name }}">
              <input type="number" name="category_weight[]" placeholder="Weight %" min="0" max="100" value="{{ category.weight }}">
              <button type="button" class="remove-category">✕</button>
            </div>
            <div class="category-description">
              <textarea name="category_description[]" placeholder="Description of category criteria">{{ category.description }}</textarea>
            </div>
          </div>
          {% endfor %}
          
          <button type="button" id="add-category" class="button">Add Category</button>
        </div>
      </div>
      
      <div class="step-actions">
        <button type="button" hx-get="/assignment/create/{{ course.id }}/2" hx-swap="outerHTML" class="button">Back</button>
        <button type="button" class="button secondary">Save as Draft</button>
        <button type="button" hx-get="/assignment/create/{{ course.id }}/4" hx-swap="outerHTML" class="button primary">Next</button>
      </div>
    </div>
    {% endif %}
    
    <!-- Step 4: Feedback Settings -->
    {% if step == 4 %}
    <div class="form-step">
      <div class="feedback-settings">
        <div class="form-group">
          <label>AI Model</label>
          <select name="ai_model_id">
            {% for model in ai_models %}
            <option value="{{ model.id }}" {% if draft.ai_model_id == model.id %}selected{% endif %}>{{ model.name }}</option>
            {% endfor %}
          </select>
        </div>
        
        <div class="form-group">
          <label>Number of Runs</label>
          <select name="num_runs">
            <option value="1" {% if draft.num_runs == 1 %}selected{% endif %}>1</option>
            <option value="2" {% if draft.num_runs == 2 %}selected{% endif %}>2</option>
            <option value="3" {% if draft.num_runs == 3 or not draft.num_runs %}selected{% endif %}>3</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Aggregation Method</label>
          <select name="aggregation_method_id">
            {% for method in aggregation_methods %}
            <option value="{{ method.id }}" {% if draft.aggregation_method_id == method.id %}selected{% endif %}>{{ method.name }}</option>
            {% endfor %}
          </select>
        </div>
        
        <div class="form-group">
          <label>Feedback Style</label>
          <select name="feedback_style_id">
            {% for style in feedback_styles %}
            <option value="{{ style.id }}" {% if draft.feedback_style_id == style.id %}selected{% endif %}>{{ style.name }}</option>
            {% endfor %}
          </select>
        </div>
        
        <div class="form-group">
          <label>Score Display</label>
          <select name="mark_display_option_id">
            {% for option in mark_display_options %}
            <option value="{{ option.id }}" {% if draft.mark_display_option_id == option.id %}selected{% endif %}>{{ option.name }}</option>
            {% endfor %}
          </select>
        </div>
        
        <div class="form-group">
          <label>Review Requirements</label>
          <div class="checkbox-group">
            <input type="checkbox" id="require_review" name="require_review" {% if draft.require_review %}checked{% endif %}>
            <label for="require_review">Require instructor review before releasing feedback</label>
          </div>
        </div>
      </div>
      
      <div class="step-actions">
        <button type="button" hx-get="/assignment/create/{{ course.id }}/3" hx-swap="outerHTML" class="button">Back</button>
        <button type="button" class="button secondary">Save as Draft</button>
        <button type="button" hx-get="/assignment/create/{{ course.id }}/5" hx-swap="outerHTML" class="button primary">Next</button>
      </div>
    </div>
    {% endif %}
    
    <!-- Step 5: Review & Publish -->
    {% if step == 5 %}
    <div class="form-step">
      <div class="assignment-summary">
        <h2>Assignment Summary</h2>
        
        <div class="summary-section">
          <h3>Basic Details</h3>
          <p><strong>Title:</strong> {{ draft.title }}</p>
          <p><strong>Description:</strong> {{ draft.description }}</p>
          <p><strong>Due Date:</strong> {{ format_date(draft.due_date) }}</p>
          <p><strong>Maximum Drafts:</strong> {{ draft.max_drafts }}</p>
        </div>
        
        <div class="summary-section">
          <h3>Rubric</h3>
          <div class="rubric-summary">
            {% for category in draft.rubric_categories %}
            <div class="category-summary">
              <p><strong>{{ category.name }} ({{ category.weight }}%)</strong></p>
              <p>{{ category.description }}</p>
            </div>
            {% endfor %}
          </div>
        </div>
        
        <div class="summary-section">
          <h3>Feedback Settings</h3>
          <p><strong>AI Model:</strong> {{ get_model_name(draft.ai_model_id) }}</p>
          <p><strong>Number of Runs:</strong> {{ draft.num_runs }}</p>
          <p><strong>Aggregation Method:</strong> {{ get_method_name(draft.aggregation_method_id) }}</p>
          <p><strong>Feedback Style:</strong> {{ get_style_name(draft.feedback_style_id) }}</p>
          <p><strong>Score Display:</strong> {{ get_display_name(draft.mark_display_option_id) }}</p>
          <p><strong>Require Review:</strong> {{ "Yes" if draft.require_review else "No" }}</p>
        </div>
      </div>
      
      <div class="step-actions">
        <button type="button" hx-get="/assignment/create/{{ course.id }}/4" hx-swap="outerHTML" class="button">Back</button>
        <button type="button" class="button secondary">Save as Draft</button>
        <button type="submit" class="button primary">Publish Assignment</button>
      </div>
    </div>
    {% endif %}
  </form>
</div>
```

## 8.5 Instructor Feedback Review Interface

```html
<div class="feedback-review">
  <h1>Review Feedback</h1>
  
  <div class="review-header">
    <div class="assignment-info">
      <h2>{{ assignment.title }}</h2>
      <p class="course">{{ course.code }} - {{ course.title }}</p>
    </div>
    
    <div class="student-info">
      <p><strong>Student:</strong> {{ student.name }}</p>
      <p><strong>Email:</strong> {{ student.email }}</p>
    </div>
    
    <div class="draft-info">
      <p><strong>Draft:</strong> {{ draft.version }}/{{ assignment.max_drafts }}</p>
      <p><strong>Submitted:</strong> {{ format_date(draft.submission_date) }}</p>
    </div>
  </div>
  
  <div class="review-tabs">
    <button class="tab-button active" data-tab="aggregated">Aggregated Feedback</button>
    <button class="tab-button" data-tab="model-runs">Model Runs</button>
  </div>
  
  <div class="tab-content">
    <div id="aggregated" class="tab-pane active">
      <form hx-post="/api/instructor/feedback/{{ feedback_id }}/review" hx-swap="outerHTML">
        <div class="overall-score-edit">
          <h3>Overall Score</h3>
          <input type="number" name="overall_score" min="0" max="100" step="0.1" value="{{ overall_score }}">
        </div>
        
        <div class="category-feedback-edit">
          <h3>Category Feedback</h3>
          
          {% for category in aggregated_feedback %}
          <div class="category-edit">
            <div class="category-header">
              <h4>{{ category.category_name }}</h4>
              <input type="number" name="category_feedback[{{ loop.index0 }}].score" min="0" max="100" step="0.1" value="{{ category.aggregated_score }}">
              <input type="hidden" name="category_feedback[{{ loop.index0 }}].category_id" value="{{ category.category_id }}">
            </div>
            
            <div class="category-text">
              <textarea name="category_feedback[{{ loop.index0 }}].feedback_text" rows="6">{{ category.feedback_text }}</textarea>
            </div>
          </div>
          {% endfor %}
        </div>
        
        <div class="release-options">
          <h3>Release Options</h3>
          
          <div class="radio-group">
            <input type="radio" id="release_now" name="release_option" value="now" checked>
            <label for="release_now">Release immediately</label>
          </div>
          
          <div class="radio-group">
            <input type="radio" id="release_later" name="release_option" value="scheduled">
            <label for="release_later">Schedule release</label>
            <input type="datetime-local" id="release_date" name="release_date" disabled>
          </div>
          
          <div class="radio-group">
            <input type="radio" id="release_no" name="release_option" value="no">
            <label for="release_no">Save without releasing</label>
          </div>
        </div>
        
        <div class="review-actions">
          <button type="button" onclick="window.history.back();" class="button secondary">Cancel</button>
          <button type="submit" class="button primary">Save Review</button>
        </div>
      </form>
    </div>
    
    <div id="model-runs" class="tab-pane">
      <div class="model-runs-container">
        <div class="run-selector">
          <h3>Select Run</h3>
          <div class="run-buttons">
            {% for run in model_runs %}
            <button class="run-button {% if loop.first %}active{% endif %}" data-run="{{ run.run_id }}">
              {{ run.model_name }} (Run {{ run.run_number }})
            </button>
            {% endfor %}
          </div>
        </div>
        
        {% for run in model_runs %}
        <div class="run-details run-{{ run.run_id }} {% if not loop.first %}hidden{% endif %}">
          <h3>{{ run.model_name }} - Run {{ run.run_number }}</h3>
          <p class="timestamp">Generated: {{ format_date(run.timestamp) }}</p>
          
          <div class="run-overall">
            <h4>Overall Feedback</h4>
            <div class="feedback-text">{{ run.feedback.overall }}</div>
          </div>
          
          <div class="run-strengths">
            <h4>Strengths</h4>
            <ul>
              {% for strength in run.feedback.strengths %}
              <li>{{ strength }}</li>
              {% endfor %}
            </ul>
          </div>
          
          <div class="run-improvements">
            <h4>Areas for Improvement</h4>
            <ul>
              {% for improvement in run.feedback.improvements %}
              <li>{{ improvement }}</li>
              {% endfor %}
            </ul>
          </div>
          
          <div class="run-scores">
            <h4>Category Scores</h4>
            <table class="scores-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Score</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {% for score in run.scores %}
                <tr>
                  <td>{{ score.category_name }}</td>
                  <td>{{ score.score }}</td>
                  <td>{{ format_percentage(score.confidence) }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
```
# 9. Deployment and DevOps

## 9.1 Development Environment Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart python-jose[cryptography] passlib python-dotenv htmx aiofiles

# Create project structure
mkdir -p app/{models,routers,services,templates,static/{css,js}}

# Initialize database
python -c "
from app.database import Base, engine
from app.models import *
Base.metadata.create_all(bind=engine)
"

# Run the development server
uvicorn app.main:app --reload
```

## 9.2 Database Initialization

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedforward.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 9.3 Environment Configuration

```
# .env
# General Settings
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development  # development or production

# Database Settings
DATABASE_URL=sqlite:///./feedforward.db

# AI API Settings
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Security Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Default Admin Credentials
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-immediately

# File Storage Settings
TEMP_FILE_DIR=./temp_files
```

## 9.4 Systemd Service Configuration (Production)

```ini
# /etc/systemd/system/feedforward.service
[Unit]
Description=FeedForward AI Feedback Service
After=network.target

[Service]
User=feedforward
Group=feedforward
WorkingDirectory=/opt/feedforward
ExecStart=/opt/feedforward/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s
Environment="PATH=/opt/feedforward/venv/bin"
EnvironmentFile=/opt/feedforward/.env

[Install]
WantedBy=multi-user.target
```

## 9.5 Nginx Configuration (Production)

```nginx
# /etc/nginx/sites-available/feedforward
server {
    listen 80;
    server_name feedforward.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/feedforward/app/static;
        expires 1d;
    }

    client_max_body_size 10M;
}
```
# 10. Testing Strategy

## 10.1 Unit Tests

```python
# tests/test_aggregation.py
import unittest
from app.services.feedback_service import apply_aggregation_method

class TestAggregation(unittest.TestCase):
    def test_mean_aggregation(self):
        scores = [85.0, 90.0, 95.0]
        confidences = [0.8, 0.9, 0.7]
        result = apply_aggregation_method(scores, confidences, method="mean")
        self.assertEqual(result, 90.0)
    
    def test_weighted_mean_aggregation(self):
        scores = [85.0, 90.0, 95.0]
        confidences = [0.8, 0.9, 0.7]
        result = apply_aggregation_method(scores, confidences, method="weighted_mean")
        expected = (85.0 * 0.8 + 90.0 * 0.9 + 95.0 * 0.7) / (0.8 + 0.9 + 0.7)
        self.assertAlmostEqual(result, expected)
    
    def test_median_aggregation(self):
        scores = [85.0, 90.0, 95.0]
        confidences = [0.8, 0.9, 0.7]
        result = apply_aggregation_method(scores, confidences, method="median")
        self.assertEqual(result, 90.0)
    
    def test_trimmed_mean_aggregation(self):
        scores = [80.0, 85.0, 90.0, 95.0, 100.0]
        confidences = [0.8, 0.9, 0.7, 0.6, 0.5]
        result = apply_aggregation_method(scores, confidences, method="trimmed_mean")
        self.assertEqual(result, (85.0 + 90.0 + 95.0) / 3)
    
    def test_empty_scores(self):
        scores = []
        confidences = []
        result = apply_aggregation_method(scores, confidences, method="mean")
        self.assertEqual(result, 0.0)
    
    def test_single_score(self):
        scores = [90.0]
        confidences = [0.8]
        result = apply_aggregation_method(scores, confidences, method="median")
        self.assertEqual(result, 90.0)

# More unit tests for other components...
```

## 10.2 Integration Tests

```python
# tests/test_api_integration.py
from fastapi.testclient import TestClient
from app.main import app
import unittest
from app.database import Base, engine, get_db
from app.models import User, Student, Instructor, Course
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta

client = TestClient(app)

def get_test_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        # Create test database session
        Base.metadata.create_all(bind=engine)
        self.db = TestSession()
        
        # Create test user
        hashed_password = "hashed_password"  # In real tests, use actual hash function
        test_user = User(
            email="test@example.com",
            name="Test User",
            password_hash=hashed_password,
            role="student"
        )
        self.db.add(test_user)
        self.db.commit()
        
        # Create student record
        test_student = Student(user_id=test_user.id)
        self.db.add(test_student)
        self.db.commit()
        
        # Create access token
        token_data = {
            "sub": str(test_user.id),
            "email": test_user.email,
            "role": "student",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        self.access_token = jwt.encode(token_data, "test_secret", algorithm="HS256")
    
    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)
    
    def test_login_success(self):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
    
    def test_login_invalid_credentials(self):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrong_password"}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_get_student_assignments(self):
        response = client.get(
            "/api/student/assignments",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
    
    # More integration tests...
```

## 10.3 End-to-End Tests

```python
# tests/test_e2e.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

class TestStudentWorkflow(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000")
    
    def tearDown(self):
        self.driver.quit()
    
    def test_student_login_and_view_assignments(self):
        # Login
        self.driver.find_element(By.ID, "email").send_keys("student@example.com")
        self.driver.find_element(By.ID, "password").send_keys("password")
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
        
        # Check if assignments are displayed
        assignments = self.driver.find_elements(By.CLASS_NAME, "assignment-card")
        self.assertGreater(len(assignments), 0)
    
    def test_submit_draft(self):
        # Login first
        self.driver.find_element(By.ID, "email").send_keys("student@example.com")
        self.driver.find_element(By.ID, "password").send_keys("password")
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
        
        # Click on Submit Draft button for first assignment
        self.driver.find_element(By.XPATH, "//a[contains(text(), 'Submit Draft')]").click()
        
        # Wait for submission form to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "submission-form"))
        )
        
        # Enter draft content
        self.driver.find_element(By.ID, "content").send_keys("This is a test submission.")
        
        # Submit the form
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Draft')]").click()
        
        # Wait for success message
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        success_message = self.driver.find_element(By.CLASS_NAME, "success-message").text
        self.assertIn("submitted successfully", success_message)
    
    # More E2E tests...
```
# 11. Initialization and Seed Data

## 11.1 Initial Data Script

```python
# scripts/init_data.py
from app.database import SessionLocal
from app.models import (
    User, Student, Instructor, Course, AIModel, AggregationMethod,
    FeedbackStyle, MarkDisplayOption, SystemConfiguration
)
from app.security import hash_password
import json

def init_data():
    db = SessionLocal()
    
    # Create admin user
    admin_exists = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_exists:
        admin = User(
            email="admin@example.com",
            name="Admin User",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
    
    # Create demo instructor
    instructor_exists = db.query(User).filter(User.email == "instructor@example.com").first()
    if not instructor_exists:
        instructor_user = User(
            email="instructor@example.com",
            name="Demo Instructor",
            password_hash=hash_password("instructor123"),
            role="instructor"
        )
        db.add(instructor_user)
        db.commit()
        
        instructor = Instructor(
            user_id=instructor_user.id,
            department="Computer Science"
        )
        db.add(instructor)
        db.commit()
    else:
        instructor_user = instructor_exists
        instructor = db.query(Instructor).filter(Instructor.user_id == instructor_user.id).first()
    
    # Create demo student
    student_exists = db.query(User).filter(User.email == "student@example.com").first()
    if not student_exists:
        student_user = User(
            email="student@example.com",
            name="Demo Student",
            password_hash=hash_password("student123"),
            role="student"
        )
        db.add(student_user)
        db.commit()
        
        student = Student(user_id=student_user.id)
        db.add(student)
        db.commit()
    
    # Create AI models
    if db.query(AIModel).count() == 0:
        models = [
            AIModel(
                name="GPT-4",
                api_provider="OpenAI",
                version="gpt-4",
                active=True,
                api_config=json.dumps({
                    "model": "gpt-4",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "system_prompt": "You are an expert educational assessor providing detailed, constructive feedback."
                })
            )
        ]
        db.add_all(models)
        db.commit()
    
    # Create aggregation methods
    if db.query(AggregationMethod).count() == 0:
        methods = [
            AggregationMethod(
                name="Mean",
                description="Simple average of all scores",
                is_active=True
            ),
            AggregationMethod(
                name="Median",
                description="Middle value of all scores",
                is_active=True
            )
        ]
        db.add_all(methods)
        db.commit()
    
    # Create feedback styles
    if db.query(FeedbackStyle).count() == 0:
        styles = [
            FeedbackStyle(
                name="Balanced",
                description="Equal focus on strengths and areas for improvement",
                is_active=True
            ),
            FeedbackStyle(
                name="Encouraging",
                description="More emphasis on strengths with gentle suggestions for improvement",
                is_active=True
            ),
            FeedbackStyle(
                name="Detailed",
                description="In-depth analysis with specific recommendations",
                is_active=True
            )
        ]
        db.add_all(styles)
        db.commit()
    
    # Create mark display options
    if db.query(MarkDisplayOption).count() == 0:
        options = [
            MarkDisplayOption(
                display_type="numeric",
                name="Numeric Score",
                description="Display as a percentage (e.g., 85.5%)",
                is_active=True
            ),
            MarkDisplayOption(
                display_type="hidden",
                name="No Score",
                description="Hide numerical scores and show only feedback",
                is_active=True
            ),
            MarkDisplayOption(
                display_type="icon",
                name="Bullseye Icons",
                description="Visual representation using bullseye icons",
                icon_type="bullseye",
                is_active=True
            )
        ]
        db.add_all(options)
        db.commit()
    
    # Create system configuration
    if db.query(SystemConfiguration).count() == 0:
        configs = [
            SystemConfiguration(
                setting_key="default_max_drafts",
                setting_value="3",
                description="Default maximum number of drafts allowed per assignment"
            ),
            SystemConfiguration(
                setting_key="default_num_runs",
                setting_value="3",
                description="Default number of AI runs per submission"
            ),
            SystemConfiguration(
                setting_key="temp_file_retention_hours",
                setting_value="24",
                description="Hours to keep temporary draft files before deletion"
            )
        ]
        db.add_all(configs)
        db.commit()
    
    db.close()

if __name__ == "__main__":
    init_data()
    print("Initial data created successfully!")
```
# 12. Conclusion and Next Steps

The FeedForward MVP Technical Specification outlines a complete implementation plan for building a functioning AI-driven feedback system that supports multiple runs of a single AI model. This foundation will allow future expansion to a multi-model approach without significant restructuring.

## 12.1 Key MVP Features

1. **User Authentication and Role Management**: Separate interfaces for students and instructors with appropriate access controls.

2. **Assignment Creation and Management**: Structured 5-step workflow for instructors to create assignments with rubrics and AI feedback settings.

3. **Draft Submission and Feedback**: Students can submit multiple drafts and receive formative feedback aligned with assignment rubrics.

4. **Multi-Run Architecture**: Although limited to