# ADR 005: UI Framework Selection - FastHTML with HTMX

## Status

Accepted

## Context

FeedForward requires a web-based user interface that balances several factors:

1. **Development Efficiency**:
   - Limited development resources
   - Preference for unified technology stack
   - Desire to minimize context switching between languages

2. **Application Requirements**:
   - Server-rendered pages with selective interactivity
   - Form-heavy user interfaces for assignments and feedback
   - Non-real-time nature (feedback generation has acceptable delays)
   - Need for both student and instructor interfaces

3. **Technical Considerations**:
   - Team's existing expertise in Python
   - Need for maintainability and ease of onboarding
   - Balance between developer experience and user experience

4. **Alternatives Considered**:
   - **React/Vue/Angular**: Client-side JavaScript frameworks
   - **Django**: Full-featured Python web framework
   - **Flask**: Lightweight Python web framework
   - **Streamlit**: Python-based data app framework

## Decision

We have chosen FastHTML with HTMX for the frontend, paired with FastAPI for backend services, based on the following considerations:

1. **Unified Python Environment**: This combination allows development entirely in Python, simplifying the development process, debugging, and maintenance.

2. **Reduced Context Switching**: By staying within a single language ecosystem, we minimize the cognitive load of switching between different programming paradigms.

3. **Server-Side Rendering with Progressive Enhancement**: FastHTML provides server-side rendering while HTMX enables interactive features without complex client-side JavaScript.

4. **Familiarity and Expertise**: The team has existing Python expertise, making this approach more efficient than learning entirely new frontend frameworks.

5. **Appropriate for Non-Real-Time Requirements**: Since the application doesn't require instant feedback (1-2 minute delays are acceptable), a server-rendered approach with selective interactivity is well-suited.

6. **Simplified State Management**: Server-side state management is often simpler to reason about than complex client-side state.

7. **Direct Integration with Backend Services**: Using Python throughout allows for seamless integration with the LLM services and database operations.

### Why Not React/Vue/Angular?

Modern JavaScript frameworks were considered but not chosen for these reasons:
- **Additional Complexity**: Would require maintaining separate frontend and backend codebases
- **Learning Curve**: Would necessitate expertise in both Python and JavaScript ecosystems
- **Overhead for Requirements**: The interactivity needs of the application don't justify the complexity of a full SPA framework
- **Development Speed**: Server-side rendering with targeted interactivity allows for faster development for our specific needs

## Consequences

### Positive

- **Development Efficiency**: Faster development cycle with a single language
- **Simpler Architecture**: Fewer moving parts and technologies to maintain
- **Easier Debugging**: End-to-end Python traceability for errors
- **Reduced Bundle Size**: Minimal JavaScript sent to clients
- **Lower Barrier to Entry**: New developers only need Python knowledge
- **Progressive Enhancement**: Basic functionality works even without JavaScript

### Negative

- **Limited Rich Interactions**: Complex client-side interactions are more difficult
- **Performance Considerations**: Server rendering can be slower for highly interactive features
- **Ecosystem Size**: Smaller ecosystem compared to popular JavaScript frameworks
- **Future Scaling**: May require architecture changes if very complex UI interactions are needed later

## Implementation

The implementation uses:

1. **FastHTML**: For server-side component rendering and composition
2. **HTMX**: For adding interactivity without extensive JavaScript
3. **Tailwind CSS**: For styling without writing custom CSS
4. **FastAPI**: For backend API endpoints and server logic

This approach maintains a clean separation of concerns while keeping the technology stack unified around Python.