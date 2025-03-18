# FeedForward Development Roadmap

## ADR Candidates
- [ ] Feedback Generation Strategy - How multiple AI models are run and results aggregated
- [x] Database Choice - Using SQLite vs other options for data persistence (ADR-004)
- [ ] API Design - RESTful vs GraphQL or other approaches for potential future API needs
- [x] UI Framework Selection - Current HTML/CSS/HTMX approach vs component libraries (ADR-005)
- [ ] Deployment Strategy - How the application is packaged and deployed
- [ ] Privacy & Security Model - How student data and API keys are protected

## Core Infrastructure
- [x] Initialize git repository
- [x] Set up project structure
- [x] Create README.md and documentation
- [ ] Implement core database models
- [ ] Setup proper app initialization

## Authentication System
- [ ] Refine existing authentication
- [ ] Add domain-based role assignment (curtin.edu.au, student.curtin.edu.au)
- [ ] Implement "forgot password" functionality
- [ ] Add instructor approval workflow
- [ ] Create student invitation system

## Database Schema
- [ ] Define model for AI models configuration
- [ ] Define model for runs
- [ ] Define model for assignments
- [ ] Define model for drafts
- [ ] Define model for feedback
- [ ] Define model for aggregated feedback
- [ ] Implement relationships between models

## Instructor Features
- [ ] Course management
- [ ] Student roster management
- [ ] Assignment creation with rubrics
- [ ] Feedback configuration
- [ ] Student progress monitoring
- [ ] Feedback approval workflow

## Student Features
- [ ] Dashboard with pending assignments
- [ ] Draft submission interface
- [ ] Feedback viewing interface
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