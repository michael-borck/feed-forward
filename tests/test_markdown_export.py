"""Tests for ``build_feedback_markdown`` (per-draft feedback export)."""

from app.utils.markdown_export import build_feedback_markdown


class _Draft:
    def __init__(self, student_email: str, version: int, submission_date: str):
        self.student_email = student_email
        self.version = version
        self.submission_date = submission_date


class _Assignment:
    def __init__(self, title: str):
        self.title = title


class _Agg:
    def __init__(
        self,
        category_id: int,
        score: float,
        text: str = "",
        status: str = "approved",
        release_date: str = "",
        edited: bool = False,
        instructor: str = "",
    ):
        self.category_id = category_id
        self.aggregated_score = score
        self.feedback_text = text
        self.status = status
        self.release_date = release_date
        self.edited_by_instructor = edited
        self.instructor_email = instructor


def _md(rows, cat_names=None, **overrides):
    draft = _Draft(
        overrides.get("email", "s@x.com"),
        overrides.get("version", 1),
        overrides.get("submission_date", "2026-05-01"),
    )
    assignment = _Assignment(overrides.get("title", "Essay 1"))
    return build_feedback_markdown(
        draft,
        assignment,
        overrides.get("course", "Intro to AI"),
        rows,
        cat_names or {},
    )


# ---- header ----


def test_header_includes_assignment_title_student_and_course():
    md = _md([], title="Reflection 1", course="Intro to AI", email="alice@x.com")
    assert "# Feedback - Reflection 1" in md
    assert "**Student:** alice@x.com" in md
    assert "**Course:** Intro to AI" in md


def test_header_includes_version_and_submission_date():
    md = _md([], version=3, submission_date="2026-05-15T09:30:00")
    assert "version 3" in md
    assert "2026-05-15T09:30:00" in md


# ---- overall + status ----


def test_overall_is_unweighted_average_of_category_scores():
    md = _md(
        [_Agg(1, 80.0), _Agg(2, 60.0)],
        cat_names={1: "Clarity", 2: "Structure"},
    )
    assert "**Overall:** 70.0/100" in md


def test_status_released_includes_release_date():
    md = _md([_Agg(1, 50.0, status="approved", release_date="2026-05-15")])
    assert "Released" in md and "2026-05-15" in md


def test_status_pending_when_no_row_is_approved():
    md = _md([_Agg(1, 50.0, status="pending_review")])
    assert "Pending review" in md
    assert "Released" not in md


def test_no_rows_omits_overall_and_status_lines():
    md = _md([])
    assert "**Overall:**" not in md
    assert "Status:" not in md
    assert "_No aggregated feedback yet._" in md


# ---- per-category ----


def test_each_category_renders_with_score_heading_and_text():
    md = _md(
        [
            _Agg(1, 80.0, text="Strong claims"),
            _Agg(2, 60.0, text="Loose structure"),
        ],
        cat_names={1: "Clarity", 2: "Structure"},
    )
    assert "### Clarity - 80.0/100" in md
    assert "Strong claims" in md
    assert "### Structure - 60.0/100" in md
    assert "Loose structure" in md


def test_unknown_category_id_falls_back_to_id_label():
    md = _md([_Agg(99, 50.0)], cat_names={})  # no name for id 99
    assert "Category 99" in md


def test_empty_feedback_text_uses_placeholder():
    md = _md([_Agg(1, 50.0, text="")], cat_names={1: "Clarity"})
    assert "_(no feedback text)_" in md


def test_instructor_review_footer_appears_when_edited():
    md = _md(
        [_Agg(1, 50.0, edited=True, instructor="i@x.com")],
        cat_names={1: "Clarity"},
    )
    assert "Reviewed by i@x.com" in md


def test_no_footer_when_not_edited():
    md = _md([_Agg(1, 50.0, edited=False)], cat_names={1: "Clarity"})
    assert "Reviewed by" not in md
