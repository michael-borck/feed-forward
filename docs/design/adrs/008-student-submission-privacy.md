# ADR 008: Student Submission Privacy

## Status

Accepted

## Context

The FeedForward platform processes student assignments to provide automated feedback. These submissions contain academic work that may include personal perspectives, ideas, and writing styles that could be considered personally identifiable or sensitive. A key concern for educational technology platforms is balancing functionality with student privacy.

Traditional learning management systems typically store student submissions indefinitely, creating potential privacy concerns:

1. Long-term storage of student work increases the privacy risk footprint
2. Academic writing often contains personal perspectives and information
3. There is minimal educational benefit to retaining the raw submission content once feedback is generated
4. Storage of submissions could be misused as an unauthorized file repository

We need to determine the appropriate data lifecycle for student submissions that balances:
- Providing effective feedback functionality
- Respecting student privacy
- Minimizing data storage
- Maintaining useful analytics and progress tracking

## Decision

We have decided to implement a privacy-focused approach for student submissions:

1. **Temporary Content Storage**:
   - Student submissions will be stored only temporarily during the feedback generation process
   - After feedback is generated, the original content will be automatically removed
   - A scheduled cleanup process will ensure that any submissions that haven't been automatically cleaned are addressed

2. **Metadata Retention**:
   - We will retain submission metadata such as:
     - Word count
     - Submission date and time
     - Draft version
     - Assignment information
   - This metadata allows for progress tracking without storing actual content

3. **Feedback Preservation**:
   - All generated feedback will be preserved
   - Rubric scores and category-specific feedback will be stored
   - This enables students to track their improvement over multiple drafts

4. **User Transparency**:
   - Students will be clearly informed that their submission content is temporary
   - Submission forms will include explicit notices about content removal
   - Documentation will advise students to maintain their own copies

5. **Technical Implementation**:
   - Added `content_preserved` flag (defaults to false) to control whether content should be exceptionally preserved
   - Added `content_removed_date` field to track when content was removed
   - Implemented automated cleanup utility that can run as a scheduled task
   - Added word count calculation to preserve this statistic after content removal

## Consequences

### Positive

- **Enhanced Privacy**: Significantly reduces the risk of unauthorized access to student work
- **Reduced Data Footprint**: Minimizes the amount of sensitive data stored in the system
- **Regulatory Compliance**: Better aligns with data minimization principles in privacy regulations
- **Clear Expectations**: Students understand that the system is not a storage platform for their work
- **Focused Purpose**: The system focuses on its core function (feedback) without becoming a content repository

### Negative

- **Limited Historical Review**: Students cannot review the exact content of their previous submissions within the system
- **Technical Complexity**: Requires implementation of cleanup processes and careful handling of feedback relationships
- **Additional Communication**: Requires clear explanation to users about the data lifecycle
- **Limited Instructor Review**: Instructors can't review exact submission content after feedback is generated

### Mitigations

- **Student Awareness**: Clear instructions advise students to keep their own copies of submitted work
- **Metadata Retention**: Sufficient metadata is kept to track progress and improvement
- **Optional Preservation**: System maintains the capability to flag specific submissions for preservation if required for legitimate educational purposes

## Implementation Notes

The implementation includes:

1. **Updated Data Model**:
   - Modified `Draft` model to include privacy-related fields
   - Added word count tracking to preserve statistics after content removal

2. **Privacy Utility Functions**:
   - Created `privacy.py` module with functions for managing content lifecycle
   - Implemented word count calculation function

3. **User Interface Updates**:
   - Added privacy notices to submission forms
   - Modified submission display to show appropriate messages for removed content
   - Added word count display to provide context even when content is removed

4. **Cleanup Process**:
   - Implemented scheduled task capability via `cleanup_drafts.py`
   - Added instructions for periodic execution in the README