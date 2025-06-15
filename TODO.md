# FeedForward Development Roadmap

## Immediate Priorities (Critical Path to MVP)
1. **Terms of Service/Privacy** (Legal requirement)
   - [x] Add ToS/Privacy acceptance during registration
   - [x] Update registration flow to include acceptance tracking

2. **File Upload Support** (Prerequisite for feedback)
   - [x] Add file upload handling for student submissions
   - [x] Support docx, pdf, txt file formats
   - [x] Implement file content extraction

3. **Feedback Generation Pipeline** (Core functionality)
   - [x] Implement prompt template system with rubric integration
   - [x] Create feedback generation service
   - [x] Build aggregation logic for multiple AI runs
   - [ ] Add feedback generation UI for students
   - [ ] Implement instructor feedback review/approval interface

4. **Testing Infrastructure** (Quality assurance)
   - [ ] Set up pytest framework
   - [ ] Create unit tests for core models
   - [ ] Add integration tests for authentication flow
   - [ ] Test feedback generation pipeline

## ADR Candidates
- [ ] Feedback Generation Strategy - How multiple AI models are run and results aggregated
- [x] Database Choice - Using SQLite vs other options for data persistence (ADR-004)
- [ ] API Design - RESTful vs GraphQL or other approaches for potential future API needs
- [x] UI Framework Selection - Current HTML/CSS/HTMX approach vs component libraries (ADR-005)
- [ ] Deployment Strategy - How the application is packaged and deployed
- [x] Privacy & Security Model - Student submission privacy (ADR-008)
- [x] Data Lifecycle Management - How data is preserved with soft deletion (ADR-002)
- [x] Authentication Strategy - Email verification and role-based access (ADR-003)
- [x] AI Model Ownership - Configuring and running models (ADR-001)
- [x] Educational Workflow Architecture - Component relationships and lifecycles (ADR-007)
- [x] Student Enrollment Lifecycle - Invitation and enrollment process (ADR-006)
- [x] API Key Management - Secure storage and access of provider credentials (ADR-009)
- [x] Model Instance Configuration - Flexible model selection and parameter tuning (ADR-010)

## Core Infrastructure
- [x] Initialize git repository
- [x] Set up project structure
- [x] Create README.md and documentation
- [x] Implement core database models
- [x] Setup proper app initialization
- [x] Implement encryption for sensitive data

## Authentication System
- [x] Refine existing authentication
- [x] Add domain-based role assignment via domain whitelist
- [x] Implement "forgot password" functionality
- [x] Add instructor approval workflow
- [x] Create student invitation system
- [x] Add admin interface for student enrollment management
- [x] Add instructor removal functionality for admins
- [ ] Add terms of service/privacy policy acceptance during account verification

## Database Schema
- [x] Define model for AI models configuration
- [x] Define model for runs (model_runs table implemented)
- [x] Define model for assignments
- [x] Define model for drafts (drafts table implemented)
- [x] Define model for feedback (feedback_items, category_scores implemented)
- [x] Define model for aggregated feedback (aggregated_feedback table implemented)
- [x] Implement relationships between models

## Instructor Features
- [x] Course management (create, edit, list)
- [x] Course status management (active, closed, archived)
- [x] Student roster management
  - [x] CSV/TSV upload for student email invitations (MVP)
  - [ ] Enhanced email invitation: validation, batch processing, and support for additional file formats
- [x] Assignment creation with rubrics
  - [x] Rubric templates (essay, research paper, presentation)
  - [x] Weight-based rubric categories
  - [x] Assignment status management
- [ ] Feedback configuration
- [ ] Student progress monitoring
- [ ] Feedback approval workflow

## Student Features
- [x] Dashboard with pending assignments
- [x] Course view with assignment listing
- [x] Draft submission interface
- [ ] Draft submission file upload support (docx, pdf, txt)
- [x] Feedback viewing interface (implemented in student.py)
- [x] Progress tracking across drafts (draft history implemented)
- [ ] Draft comparison view
- [x] Assignment status indicators (upcoming, open, closed)

## AI Integration
- [x] Admin interface for LLM provider configuration
- [x] Instructor interface for LLM selection and configuration (assignment settings)
- [x] Implement API client for LLM services (litellm_client.py implemented)
- [x] LiteLLM integration for multiple providers support
- [ ] Create prompt template system for rubric-based feedback
- [ ] Build multi-run feedback aggregation logic
- [ ] Implement feedback extraction and normalization
- [ ] Add feedback generation endpoint and UI
- [ ] Implement instructor feedback approval workflow

## UI/UX
- [x] Implement base templates
- [x] Create responsive design with Tailwind
- [x] Implement HTMX interactions
- [ ] Design feedback display components
- [x] Branded error pages (404, 403) with user-friendly messages
- [x] Dynamic header with role-based navigation
- [ ] User profile page with account settings
- [ ] Form validation improvements with better error messages
- [ ] Rich text editor for assignment submissions
- [ ] Notifications system for important events
- [ ] Dashboard analytics and visualizations
- [ ] Accessibility improvements (WCAG compliance) 
- [ ] Mobile responsiveness optimizations
- [ ] File upload with progress indicators and previews
- [ ] Search functionality across assignments and feedback
- [ ] Theme switching with dark mode option

## Testing
- [ ] Unit tests for core components
- [ ] Integration tests for workflows
- [ ] Performance testing with multiple runs

## Deployment
- [ ] Document deployment process
- [ ] Create deployment scripts
- [ ] Setup CI/CD pipeline

## Completed Major Features
### Authentication & User Management
- ✅ Multi-role authentication system (Admin, Instructor, Student)
- ✅ Email verification with token-based system
- ✅ Domain whitelist for instructor auto-approval
- ✅ Instructor approval workflow
- ✅ Student invitation system
- ✅ Password reset functionality

### Course & Assignment Management
- ✅ Full course CRUD operations with status management
- ✅ Assignment creation with custom rubrics
- ✅ Rubric templates (essay, research paper, presentation)
- ✅ Weight-based rubric categories
- ✅ Student roster management with CSV import

### Database & Models
- ✅ Comprehensive schema with 20+ tables
- ✅ Soft deletion pattern implementation
- ✅ Encryption for sensitive data
- ✅ Full model relationships established

### AI Configuration
- ✅ AI provider and model management
- ✅ Model instance configuration with parameters
- ✅ Assignment-specific AI settings
- ✅ LiteLLM client implementation

### UI/UX
- ✅ Responsive design with Tailwind CSS
- ✅ HTMX-powered dynamic interactions
- ✅ Role-based navigation
- ✅ Student and instructor dashboards
- ✅ Assignment submission interface

## Relevant Files

### Terms of Service/Privacy Implementation
- `app/models/user.py` - Added tos_accepted, privacy_accepted, and acceptance_date fields to User model
- `app/routes/auth.py` - Updated registration form and handler to include ToS/Privacy checkboxes
- `app/routes/student.py` - Updated student join form and handler for invited students
- `app/routes/legal.py` - Created new routes for displaying ToS and Privacy Policy pages
- `docs/terms-of-service.md` - Created Terms of Service document
- `docs/privacy-policy.md` - Existing Privacy Policy document
- `app/routes/__init__.py` - Added legal routes to registration

### File Upload Support Implementation
- `app/routes/student.py` - Updated submission form to support file uploads with toggle between text/file input
- `app/utils/file_handlers.py` - Created file processing utilities for extracting content from txt, pdf, and docx files
- `requirements.txt` - Added pypdf, python-docx, and aiofiles dependencies
- File content extraction fully integrated with:
  - Text extraction from PDF (including encrypted PDF detection)
  - Text extraction from DOCX (including table content)
  - UTF-8/Latin-1 encoding support for text files
  - File size validation (10MB limit)
  - Comprehensive error handling for corrupted/invalid files

### Prompt Template System Implementation
- `app/services/prompt_templates.py` - Created comprehensive prompt template system with:
  - Base `PromptTemplate` class for standard feedback generation
  - `IterativePromptTemplate` class for multi-draft assignments
  - Context-aware prompt generation based on rubric criteria
  - Support for different feedback levels (overall, criterion-specific, or both)
  - Integration with feedback styles (encouraging, direct, analytical, balanced)
  - JSON-structured output format for easy parsing
  - Weighted rubric criteria in prompt generation

### Feedback Generation Service Implementation
- `app/services/feedback_generator.py` - Created feedback generation service with:
  - Asynchronous processing of student drafts
  - Multiple model runs per assignment configuration
  - LiteLLM integration for multi-provider AI support
  - Structured feedback storage (scores, strengths, improvements)
  - Error handling and retry logic
  - Privacy-aware content cleanup after processing
- `app/services/background_tasks.py` - Background task management for:
  - Queuing feedback generation tasks
  - Task status tracking
  - Concurrent processing with thread pool
- `app/routes/student.py` - Updated to:
  - Trigger feedback generation on submission
  - Added API endpoint for checking feedback status