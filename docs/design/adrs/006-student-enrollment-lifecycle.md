# ADR 006: Student Enrollment Lifecycle Management

## Status

Accepted

## Context

FeedForward requires a structured approach to managing student enrollments, including invitation, verification, and course participation. We needed to determine:

1. How students are added to courses
2. What the enrollment states should be
3. How to handle verification and account creation
4. How to manage failed invitations or incorrect email addresses
5. What tools instructors need to manage student enrollments

## Decision

We have implemented a student enrollment lifecycle with these key components:

1. **Instructor-Driven Enrollment**
   - Only instructors can initiate student enrollment
   - Students cannot self-register without an invitation
   - Instructors invite students by email address

2. **Two-Phase Enrollment Process**
   - Phase 1: Invitation - Student is added to course roster (unverified)
   - Phase 2: Verification - Student creates account and becomes active

3. **Enrollment States**
   - Invited: Student has been added to course but hasn't created account
   - Verified: Student has created account and can access course

4. **Email-Based Verification**
   - Students receive a unique token via email
   - Token is used to verify identity and create account
   - Tokens can be regenerated and resent as needed

5. **Instructor Management Tools**
   - View all students in a course with verification status
   - Resend invitations to students who haven't verified
   - Remove students from course as needed

6. **Exception Handling**
   - Invalid emails handled through instructor intervention
   - No automatic tracking of bounced emails
   - Students report non-receipt of invitations to instructors who can resend

## Consequences

### Positive

- Ensures only instructor-approved students can access courses
- Provides clear visibility into student verification status
- Allows instructors to manage the entire student lifecycle
- Keeps student rosters clean through easy removal of invalid entries
- Supports the educational hierarchy where instructors control class composition
- Minimizes administrative overhead for system administrators

### Negative

- No automatic handling of bounced emails
- Requires instructor intervention for invitation failures
- Students cannot self-register for courses they're interested in
- Instructors must manually manage their course rosters

## Implementation Details

The system maintains two key pieces of information for each student:

1. **Enrollment Record**: Links student email to a specific course
2. **User Record**: Contains verification status and account details

The workflow is as follows:

1. Instructor invites student(s) to a course
2. System creates enrollment record and unverified user record with verification token
3. Student receives email with verification link
4. Student clicks link, completes registration form, creating verified account
5. Student is now enrolled and verified

Instructors can view all students in the "Manage Students" page for each course, where they can:
- See which students have verified their accounts
- Resend invitations to unverified students
- Remove students from the course

## Future Considerations

- Consider automated handling of bounced emails
- Explore bulk operations for student management
- Evaluate potential for limited self-enrollment with access codes
- Consider integration with institutional student information systems