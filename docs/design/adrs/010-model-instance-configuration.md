# 010: Model Instance Configuration

## Status
Proposed

## Context
FeedForward uses multiple AI models to generate formative feedback on student assignments. Each assignment may benefit from different models or model configurations. We need to design a flexible system for configuring and managing these AI model instances.

The key considerations include:
1. How multiple models can be assigned to a single assignment
2. How to configure different parameters for the same model across different assignments
3. How to balance flexibility for power users with simplicity for typical users
4. How to allow instructors to select from available models based on ownership and capability

## Decision
We will implement a "model instance" configuration system with three levels of abstraction:

1. **Provider Level**: 
   - LLM providers (OpenAI, Anthropic, etc.) with their authentication details
   - Providers are associated with API keys and connection details
   - Providers can offer multiple models

2. **Model Level**:
   - Individual AI models (GPT-4, Claude-3, Llama, etc.)
   - Models have core capabilities (text, code, vision, audio)
   - Models have default parameters (temperature, context size)
   - Models are linked to providers

3. **Model Instance Level**:
   - Specific configurations of models for particular assignments
   - Can override default parameters (temperature, tokens, etc.)
   - Defines number of runs for this model on this assignment
   - Multiple instances can be used in a single assignment

This design will be implemented through the following database structure:
- `AIModel` table defines the available models and their providers
- `AssignmentSettings` table defines the assignment-level configuration including aggregation method
- `AssignmentModelRun` table connects assignments to specific model instances with run counts

## Consequences

### Positive
- Instructors can use multiple models for a single assignment
- Configuration can be as simple as selecting defaults or as detailed as custom tuning
- Institution-level model access can coexist with instructor-specific models
- Parameters can be tuned differently for different types of assignments
- The system supports future expansion to new model types and providers

### Negative
- Increased complexity in the database schema
- Potential for confusion with multiple abstraction layers
- UI must carefully explain the different levels of configuration
- May require additional computation resources to run multiple models

### Risks
- Instructors could unintentionally configure costly model runs
- Complex configurations might be difficult to troubleshoot
- Different models may produce inconsistent feedback that's difficult to aggregate

## Implementation Notes
- Default configurations will be provided for common use cases
- UI will offer both simple (use defaults) and advanced (customize) workflows
- Clear ownership indicators will show which models are system-wide vs instructor-specific
- Gradual rollout of advanced features to avoid overwhelming users
- Cost estimation features should be considered for future iterations