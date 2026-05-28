"""``mailto:`` URL builders.

Kept separate from the route modules so unit tests don't drag in the FastHTML
app initialisation (which still depends on ``.env`` existing at import time).
"""

from urllib.parse import quote


def student_mailto(student_email: str, assignment_title: str) -> str:
    """``mailto:`` link an instructor can use to email a student about their submission.

    The instructor's own mail client handles delivery — no SMTP infrastructure
    on the FeedForward side. Subject is URL-encoded so titles with spaces,
    ``&``, or other reserved characters survive the ``mailto:`` URL intact.
    """
    subject = f"Feedback on your submission for {assignment_title}"
    return f"mailto:{student_email}?subject={quote(subject)}"
