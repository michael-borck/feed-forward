# ADR 011: Assessment Type Extensibility Architecture

## Status

Proposed

## Context

FeedForward currently supports only text-based essay assessments. However, educational assessment needs are diverse and include:

- Code submissions (programming assignments)
- Mathematical proofs and calculations
- Multimedia content (video presentations, audio recordings)
- Diagrams and visual content
- Mixed-format assignments

Additionally, we have existing Electron applications that can analyze video and speech, converting them to text for LLM processing. We need an architecture that can:

1. Support multiple assessment types without major code changes
2. Allow external services to process specialized content
3. Maintain the existing rubric-based evaluation system
4. Enable reuse of existing tools as microservices
5. Provide a consistent experience across all assessment types

## Decision

We will implement a plugin-based assessment architecture with the following components:

### 1. Assessment Type Framework

Create an abstract `AssessmentHandler` base class that defines the interface for all assessment types:

```python
class AssessmentHandler(ABC):
    @abstractmethod
    def validate_submission(self, content: Any) -> bool
    @abstractmethod
    def preprocess(self, content: Any) -> str
    @abstractmethod
    def get_prompt_template(self) -> str
    @abstractmethod
    def format_feedback(self, raw_feedback: dict) -> dict
```

### 2. Service Integration Layer

Implement an external service interface that allows assessment handlers to delegate processing:

```python
class ExternalAssessmentService:
    def process(self, content: bytes, metadata: dict) -> dict
    def health_check(self) -> bool
    def get_capabilities(self) -> dict
```

### 3. Database Schema Extensions

- Add `assessment_type` field to Assignment model
- Create `AssessmentTypeConfig` model for type-specific settings
- Add `submission_metadata` JSON field to Draft model
- Maintain backward compatibility with existing essay assessments

### 4. Registration and Discovery

Create an `AssessmentRegistry` that:
- Manages available assessment types
- Handles service registration/deregistration
- Provides type-to-handler mapping
- Supports dynamic plugin loading

## Consequences

### Positive

1. **Extensibility**: New assessment types can be added without modifying core code
2. **Reusability**: Existing tools can be wrapped as services and integrated
3. **Separation of Concerns**: Assessment logic is isolated from core application
4. **Scalability**: Different assessment types can be scaled independently
5. **Flexibility**: Institutions can enable/disable assessment types as needed
6. **Consistency**: All assessment types follow the same evaluation pipeline

### Negative

1. **Complexity**: Adds architectural complexity with service communication
2. **Latency**: External services may introduce processing delays
3. **Reliability**: Depends on external service availability
4. **Development Effort**: Requires significant refactoring of existing code
5. **Testing**: More complex testing scenarios with service mocking

### Neutral

1. **Migration**: Existing essays will be migrated to use the new framework
2. **Configuration**: Requires additional configuration for external services
3. **Documentation**: Needs comprehensive documentation for plugin developers
4. **Security**: Service-to-service authentication must be implemented

## Implementation Plan

### Phase 1: Core Framework (Weeks 1-2)
- Create assessment handler abstraction
- Implement registry system
- Refactor existing essay handling

### Phase 2: Service Integration (Weeks 3-4)
- Design service API
- Implement service discovery
- Add authentication layer

### Phase 3: Database Updates (Week 5)
- Schema migrations
- Model updates
- Data migration scripts

### Phase 4: Initial Types (Weeks 6-7)
- Code assessment handler
- Math/LaTeX handler
- Basic multimedia handler

### Phase 5: UI Updates (Weeks 8-9)
- Dynamic submission forms
- Type-specific feedback display
- Instructor configuration

### Phase 6: Testing & Documentation (Week 10)
- Integration tests
- Plugin development guide
- API documentation

## Alternatives Considered

### 1. Monolithic Multi-Type Support
Add all assessment types directly to the core application.
- **Rejected**: Limits extensibility and increases maintenance burden

### 2. Separate Applications
Create separate applications for each assessment type.
- **Rejected**: Fragments the user experience and duplicates code

### 3. Client-Side Processing
Process specialized content in the browser before submission.
- **Rejected**: Limits processing capabilities and security

## References

- ADR-007: Educational Workflow Architecture
- ADR-010: Model Instance Configuration
- Plugin Architecture patterns
- Microservice communication patterns

## Notes

This architecture enables the conversion of existing Electron applications into microservices that can be consumed by FeedForward or other educational platforms. The design prioritizes extensibility while maintaining the core educational feedback workflow.