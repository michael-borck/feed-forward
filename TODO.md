# FeedForward Development Roadmap

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

## Core Infrastructure
- [x] Initialize git repository
- [x] Set up project structure
- [x] Create README.md and documentation
- [x] Implement core database models
- [x] Setup proper app initialization

## Authentication System
- [x] Refine existing authentication
- [x] Add domain-based role assignment via domain whitelist
- [x] Implement "forgot password" functionality
- [x] Add instructor approval workflow
- [x] Create student invitation system
- [x] Add admin interface for student enrollment management
- [x] Add instructor removal functionality for admins

## Database Schema
- [ ] Define model for AI models configuration
- [ ] Define model for runs
- [x] Define model for assignments
- [ ] Define model for drafts
- [ ] Define model for feedback
- [ ] Define model for aggregated feedback
- [ ] Implement relationships between models

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
- [x] Feedback viewing interface
- [ ] Progress tracking across drafts
- [ ] Draft comparison view

## AI Integration
- [ ] Implement API client for LLM services
- [ ] Create prompt template system
- [ ] Build multi-run feedback aggregation
- [ ] Implement feedback extraction and normalization

## UI/UX
- [ ] Implement base templates
- [ ] Create responsive design with Tailwind
- [ ] Implement HTMX interactions
- [ ] Design feedback display components

## Testing
- [ ] Unit tests for core components
- [ ] Integration tests for workflows
- [ ] Performance testing with multiple runs

## Deployment
- [ ] Document deployment process
- [ ] Create deployment scripts
- [ ] Setup CI/CD pipeline