# 009: API Key Management for LLM Providers

## Status
Proposed

## Context
FeedForward integrates with multiple Large Language Model (LLM) providers to generate feedback on student assignments. Each provider requires different authentication methods, typically API keys. These keys represent sensitive credentials that need to be securely stored and managed, while still being accessible for making API calls.

Additionally, we need to determine who can provide these keys (administrators vs instructors) and how they are associated with specific LLM instances in the system.

## Decision
We will implement a secure, flexible API key management system with the following characteristics:

1. **Provider vs Model Separation**:
   - API keys are associated with providers (e.g., OpenAI, Anthropic, Hugging Face)
   - Providers can offer multiple models (e.g., GPT-4, Claude-3)
   - Model configurations (temperature, context size) are separate from provider authentication

2. **Encryption**:
   - All API keys will be encrypted in the database using Fernet symmetric encryption
   - Encryption keys will be derived from the application's SECRET_KEY using PBKDF2HMAC
   - Keys will only be decrypted when needed for API calls

3. **Ownership Model**:
   - API keys can be owned by:
     - The system (institution-wide keys configured by administrators)
     - Individual instructors (private keys only used for their courses)
   - System-owned models are available to all instructors
   - Instructor-owned models are private to that instructor

4. **Flexible Model Instances**:
   - Instructors can create "model instances" that combine:
     - A specific provider (with its API key)
     - A specific model from that provider
     - Custom parameters (temperature, context size, etc.)
   - Multiple model instances can be used for a single assignment
   - Each instance can be configured for a different number of runs

5. **Default Configuration**:
   - System administrators can define default models and configurations
   - Instructors can use system defaults or create custom configurations
   - Sensible defaults are provided for all configurable parameters

## Consequences

### Positive
- Instructors have flexibility to use institution-provided APIs or their own
- Sensitive API keys are securely stored with encryption
- The separation of providers, models, and instances allows for high configurability
- Default configurations simplify the experience for instructors who don't need customization
- The system can support a wide variety of LLM providers with different authentication needs

### Negative
- Additional complexity in the database schema
- Need to carefully manage encryption keys and secrets
- Multiple ownership levels may create confusion about which models are available
- Requires implementation of secure encryption/decryption routines

### Risks
- If the application's SECRET_KEY is compromised, encrypted API keys could be at risk
- API keys stored in the database could potentially be accessed by unauthorized personnel with database access
- Instructors might inadvertently use expensive API calls if not properly informed about costs

## Implementation Notes
- API keys will be encrypted using Python's cryptography library with Fernet
- The database will store the encrypted keys in the `api_config` JSON field
- A utility function will handle decryption when keys are needed for API calls
- UI will clearly indicate which models are system-owned vs instructor-owned
- Cost monitoring and limits should be considered in future iterations