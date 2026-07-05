"""
Submission-related utility helpers.

Retention decision (2026-07-06): FeedForward retains draft content so
students and instructors can track progress across drafts. The earlier
"temporary content storage" machinery (automatic wiping of draft text once
feedback was ready, plus a never-implemented scheduled cleanup) was removed
by product decision — see docs/security-audit-2026-07.md. Students can
still hide individual drafts from their own view.
"""


def calculate_word_count(text):
    """Calculate the word count of a text submission"""
    if not text:
        return 0
    return len(text.split())
