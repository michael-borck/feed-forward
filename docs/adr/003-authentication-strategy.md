# ADR 003: Authentication Strategy

## Status

Accepted

## Context

FeedForward needs a secure and user-friendly authentication system. We considered several options:

1. **Single Sign-On (SSO)** with institutional identity providers
2. **Custom authentication** with email verification
3. **Third-party authentication** providers (OAuth with Google, Microsoft, etc.)

Key factors in this decision:
- FeedForward is designed as an independent application, not tightly integrated with institution systems
- Different institutions have different identity management systems
- Need for a flexible approach that works for various deployment scenarios
- Need to support different user roles (students, instructors, administrators)
- Need for email communication with users for other app features

## Decision

We have chosen to implement a custom authentication system with email verification, with these key components:

1. **Email-based registration** with verification links
2. **Role-based access control** (student, instructor, admin)
3. **Instructor approval workflow** for added security
4. **Password reset via email**
5. **Session-based authentication** for web access

This approach allows:
- Institution independence (no integration with specific SSO systems required)
- Confirmation that users have valid email addresses (important for system communications)
- Administrative control over instructor accounts
- Student invitation workflow by instructors

## Consequences

### Positive

- Simpler implementation and deployment (no external dependencies)
- Works consistently across any institution or individual deployment
- Full control over the authentication flow and user experience
- Ensures all users have working email addresses for system notifications
- Supports the invitation workflow for student enrollment

### Negative

- Users need to create and remember another set of credentials
- No automatic integration with institutional identity systems
- Requires maintaining email sending infrastructure
- Potential for email delivery issues affecting account verification

## Future Considerations

While custom authentication is the initial approach, the system is designed to potentially add SSO options in the future:

1. The user schema includes fields that would be compatible with additional auth methods
2. The authentication flow could be extended to include SSO providers
3. Specific institutional deployments could add custom SSO integration

This gives us a solid starting point while leaving the door open for more sophisticated authentication methods as needs evolve.