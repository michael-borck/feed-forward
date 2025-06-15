# ADR 004: Database Choice - SQLite

## Status

Accepted

## Context

FeedForward requires a database system to store user information, assignments, submitted drafts, and feedback. We needed to select an appropriate database technology considering:

1. **Expected Usage Patterns**:
   - Up to 20,000 total users at the institution level
   - Approximately 1,000 active users at any given time
   - Around 100 concurrent feedback requests
   - Predominantly read operations after data is written

2. **Performance Requirements**:
   - Non-real-time feedback generation (1-2 minute processing time is acceptable)
   - Data consistency is important for academic records
   - Local deployment within institutions

3. **Development and Operational Constraints**:
   - Limited resources for database administration
   - Preference for technologies compatible with the Python stack
   - Need for simplicity in deployment and maintenance

4. **Alternatives Considered**:
   - **PocketBase**: An open-source backend with built-in user management and SQLite storage
   - **PostgreSQL**: A full-featured client-server database
   - **MongoDB**: A document-oriented NoSQL database
   - **Firebase/Firestore**: Cloud-based NoSQL database with authentication services

## Decision

We have chosen SQLite with FastLite as the primary database for FeedForward based on the following considerations:

1. **Appropriate for Low Concurrency**: SQLite can handle the expected load of ~100 concurrent requests effectively, as it's designed for low to medium concurrency applications.

2. **File-Based Database**: As a file-based database, SQLite requires no separate server process, simplifying deployment and reducing operational overhead.

3. **Non-Real-Time Requirements**: The application's tolerance for 1-2 minute processing times aligns well with SQLite's transaction handling capabilities.

4. **Python Integration**: SQLite has excellent Python support through the standard library and various ORMs.

5. **Zero Configuration**: SQLite requires minimal setup and maintenance, making it ideal for deployments where dedicated database administration is not available.

6. **Proven in Similar Contexts**: SQLite has demonstrated reliability in embedded and local applications with similar usage patterns.

7. **Direct Control Over Schema**: Using SQLite directly with FastLite gives us complete control over the database schema, authentication flow, and data manipulation.

### Why Not PocketBase?

PocketBase was a strong alternative we considered as it provides:
- SQLite as its underlying database
- Built-in authentication and user management
- Admin UI out of the box

However, we chose direct SQLite with FastLite instead for these reasons:
- **Technology Stack Unity**: We preferred to maintain a pure Python stack rather than introducing a Go-based service
- **Custom Authentication Needs**: Our specific workflow for instructors and students required custom authentication logic
- **Schema Flexibility**: We needed fine-grained control over database schema for handling specialized feedback data models
- **Learning Curve**: Using our existing SQLite expertise was more efficient than learning PocketBase's conventions
- **Integration Simplicity**: Direct database access simplified integration with LLM APIs and feedback generation

## Consequences

### Positive

- **Simplified Deployment**: No separate database server to configure and maintain
- **Reduced Operational Complexity**: No need for database user management, network configuration, etc.
- **Zero Administration**: No ongoing database administration required
- **Portability**: The entire database is contained in a single file
- **Reliability**: SQLite is known for its stability and data integrity guarantees
- **Familiar Technology**: SQL interface is well understood by most developers

### Negative

- **Scalability Limitations**: Not suitable for very high concurrency (thousands of simultaneous writes)
- **Limited Networking**: Not designed for multiple servers accessing the same database
- **Feature Constraints**: Some advanced database features are not available
- **Migration Path**: Potential complexity if the application later needs to migrate to a client-server database

## Implementation

The implementation uses SQLite through:

1. The `fastlite` library which provides a clean abstraction over SQLite
2. Database files stored in the `data/` directory
3. Table schemas defined in the application's model files
4. Migration scripts for schema updates

The design maintains flexibility by using SQL abstractions that would be compatible with other SQL databases if migration becomes necessary in the future.