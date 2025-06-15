# ADR 001: AI Model Ownership Structure

## Status

Accepted

## Context

FeedForward allows the use of AI models for providing feedback on student assignments. There are two potential sources of API keys for these models:

1. Institution-wide API keys (managed by administrators)
2. Personal API keys (provided by individual instructors)

We need a database schema that supports both cases while ensuring proper separation of concerns.

## Decision

We have decided to enhance the `ai_models` table with two additional fields:

1. `owner_type`: Indicates whether the model is system-wide ('system') or instructor-specific ('instructor')
2. `owner_id`: For instructor-specific models, stores the instructor's email

This allows us to:
- Clearly separate system models from instructor models
- Enable instructors to use their own API keys
- Allow administrators to provide institution-wide models
- Support filtering models based on access rights
- Maintain clean separation of concerns between admin and instructor roles

## Consequences

### Positive

- Instructors can use their own API keys before institutional funding is secured
- System can mix and match various models from different sources
- Clear ownership model prevents unauthorized access to API keys
- Flexible structure that works for both small and large deployments
- Simple query pattern to find available models for a specific instructor

### Negative

- Slightly more complex queries when retrieving available models
- Additional migration step for existing databases
- Need to implement ownership checks in UI and API endpoints

## Implementation

The implementation includes:
1. Adding the new fields to the `ai_models` table schema
2. Creating a migration script to update existing databases
3. Updating model retrieval logic to filter based on ownership
4. Adding UI elements for instructors to manage their models