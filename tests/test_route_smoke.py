"""Route-level smoke tests: log in as each role, assert key pages render (200).

This is the bug class that keeps recurring (async-decorator breakage, stale
model field refs, AttributeErrors on list pages) — service tests never see it.
Redirect-following is OFF so a permission bounce or error redirect fails the
test instead of silently passing as the destination page's 200.
"""

import importlib.util
import os
import sys
from datetime import datetime

import pytest
from starlette.testclient import TestClient

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASSWORD = "smoke-Pass1!"
ADMIN = "smoke-admin@test.local"
INSTRUCTOR = "smoke-inst@test.local"
STUDENT = "smoke-stud@test.local"


def _load_app_main():
    """Import top-level app.py once (registers landing/legal routes)."""
    if "app_main" in sys.modules:
        return
    spec = importlib.util.spec_from_file_location(
        "app_main", os.path.join(REPO, "app.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["app_main"] = mod
    spec.loader.exec_module(mod)


def _ensure_user(email: str, role: str):
    from app.models.user import User, users
    from app.utils.auth import get_password_hash

    try:
        users[email]
        return
    except Exception:
        pass
    users.insert(
        User(
            email=email,
            name=email.split("@")[0],
            password=get_password_hash(PASSWORD),
            role=role,
            verified=True,
            verification_token="",
            approved=True,
            department="",
            reset_token="",
            reset_token_expiry="",
            status="active",
            last_active=datetime.now().isoformat(),
        )
    )


@pytest.fixture(scope="module")
def client():
    _load_app_main()
    from app import app

    for email, role in (
        (ADMIN, "admin"),
        (INSTRUCTOR, "instructor"),
        (STUDENT, "student"),
    ):
        _ensure_user(email, role)
    return TestClient(app, follow_redirects=False)


def _login(client, email):
    resp = client.post("/login", data={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    assert resp.headers.get("hx-redirect"), f"login as {email} did not redirect"


def _assert_renders(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} -> {resp.status_code}"


# ---- public pages ----

PUBLIC_PAGES = [
    "/landing",
    "/login",
    "/register",
    "/privacy",
    "/terms",
    "/contact",
    "/forgot-password",
]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
def test_public_page_renders(client, path):
    _assert_renders(client, path)


def test_root_redirects_to_landing(client):
    resp = client.get("/")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/landing"


# ---- role dashboards and list pages ----

ADMIN_PAGES = [
    "/admin/dashboard",
    "/admin/ai-models",
    "/admin/ai-models/new",
    "/admin/domains",
    "/admin/instructors",
    "/admin/signal-services",
    "/admin/usage",
]
# /instructor/invite-students is covered in the scenario tests — without a
# course it legitimately 303s to course creation.
INSTRUCTOR_PAGES = [
    "/instructor/dashboard",
    "/instructor/courses",
    "/instructor/courses/new",
    "/instructor/manage-students",
    "/instructor/models",
    "/instructor/models/new",
]
STUDENT_PAGES = ["/student/dashboard", "/student/assignments", "/student/submissions"]


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_page_renders(client, path):
    _login(client, ADMIN)
    _assert_renders(client, path)


@pytest.mark.parametrize("path", INSTRUCTOR_PAGES)
def test_instructor_page_renders(client, path):
    _login(client, INSTRUCTOR)
    _assert_renders(client, path)


@pytest.mark.parametrize("path", STUDENT_PAGES)
def test_student_page_renders(client, path):
    _login(client, STUDENT)
    _assert_renders(client, path)


# ---- parameterized pages over a seeded scenario ----


@pytest.fixture()
def scenario(client):
    """A course owned by the smoke instructor with one enrolled student,
    one assignment + rubric, and one draft with released feedback."""
    from app.models.assignment import (
        Assignment,
        Rubric,
        RubricCategory,
        assignments,
        rubric_categories,
        rubrics,
    )
    from app.models.course import Course, Enrollment, courses, enrollments
    from app.models.feedback import (
        AggregatedFeedback,
        Draft,
        aggregated_feedback,
        drafts,
    )

    now = datetime.now().isoformat()
    course = courses.insert(
        Course(
            code="SMK101",
            title="Smoke Testing",
            term="S1",
            department="CS",
            instructor_email=INSTRUCTOR,
            status="active",
            created_at=now,
            updated_at=now,
        )
    )
    enrollments.insert(Enrollment(course_id=course.id, student_email=STUDENT))
    assignment = assignments.insert(
        Assignment(
            course_id=course.id,
            title="Essay 1",
            description="d",
            instructions="i",
            due_date=now,
            max_drafts=3,
            created_by=INSTRUCTOR,
            status="active",
            created_at=now,
            updated_at=now,
        )
    )
    rubric = rubrics.insert(Rubric(assignment_id=assignment.id, assessment_type_id=0))
    cat = rubric_categories.insert(
        RubricCategory(
            rubric_id=rubric.id,
            name="Clarity",
            description="",
            weight=1.0,
        )
    )
    draft = drafts.insert(
        Draft(
            assignment_id=assignment.id,
            student_email=STUDENT,
            version=1,
            content="An essay.",
            submission_date=now,
            status="feedback_ready",
            word_count=2,
        )
    )
    from app.services.feedback_review import RELEASED

    aggregated_feedback.insert(
        AggregatedFeedback(
            draft_id=draft.id,
            category_id=cat.id,
            aggregated_score=75.0,
            feedback_text="Strengths:\n- ok\n\nAreas for improvement:\n- more",
            edited_by_instructor=False,
            instructor_email="",
            status=RELEASED,
            release_date=now,
        )
    )
    yield {"course": course, "assignment": assignment, "draft": draft}
    # rows are wiped by the autouse _clean_tables fixture (courses/enrollments
    # are session-lived, so remove them here to keep reruns deterministic)
    enrollments.delete_where("course_id = ?", [course.id])
    courses.delete(course.id)


def test_instructor_submission_pages_render(client, scenario):
    _login(client, INSTRUCTOR)
    a_id = scenario["assignment"].id
    d_id = scenario["draft"].id
    for path in (
        f"/instructor/assignments/{a_id}/submissions",
        f"/instructor/assignments/{a_id}/signal-rules",
        f"/instructor/assignments/{a_id}/signal-calibration",
        f"/instructor/submissions/{d_id}",
        f"/instructor/submissions/{d_id}/signals",
        f"/instructor/submissions/{d_id}/review",
        "/instructor/invite-students",
        f"/instructor/courses/{scenario['course'].id}/edit",
        f"/instructor/courses/{scenario['course'].id}/assignments/new",
        f"/instructor/assignments/{a_id}/edit",
    ):
        _assert_renders(client, path)


def test_student_assignment_view_renders(client, scenario):
    _login(client, STUDENT)
    _assert_renders(client, f"/student/assignments/{scenario['assignment'].id}")
    _assert_renders(client, f"/student/assignments/{scenario['assignment'].id}/submit")


def test_student_join_form_renders_with_token(client):
    """The invitation join form (anonymous, token-gated)."""
    from app.models.user import users

    _ensure_user("smoke-invitee@test.local", "student")
    invitee = users["smoke-invitee@test.local"]
    invitee.verified = False
    invitee.verification_token = "smoke-join-token"
    users.update(invitee)

    resp = client.get("/student/join?token=smoke-join-token")
    assert resp.status_code == 200


# ---- POST dispatch regression (the dead-handler bug class) ----
#
# Same-path GET+POST pairs with custom function names both registered for both
# methods; Starlette's first match swallowed every POST, so form submissions
# silently re-rendered the form. Fixed with explicit methods=[...] — this
# round-trip pins the fix.


def test_course_creation_post_actually_creates(client):
    from app.models.course import courses, enrollments

    _login(client, INSTRUCTOR)
    before = len(list(courses()))
    resp = client.post(
        "/instructor/courses/new",
        data={
            "code": "SMK999",
            "title": "Post Dispatch",
            "term": "S1",
            "description": "smoke",
        },
    )
    created = [c for c in courses() if c.code == "SMK999"]
    assert len(list(courses())) == before + 1, "POST hit the form handler, not create"
    assert resp.status_code == 303
    assert resp.headers["location"].endswith("/students")
    assert created[0].description == "smoke"
    # cleanup (courses table outlives the per-test wipe)
    for c in created:
        enrollments.delete_where("course_id = ?", [c.id])
        courses.delete(c.id)
