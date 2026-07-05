"""Tests for the code-analyser signal slice (S4 first half).

Covers: assessment-type routing in signal extraction, code-response flattening,
filename resolution for language detection, the type-aware scorer suggestions,
the analyse_code client, and code-file text extraction.
"""

import asyncio
import io
from datetime import datetime

import requests

from app.services import signal_scorer, signal_service
from app.utils import analyser_client

# A representative code-analyser /analyse response (single Python file).
CODE_SAMPLE = {
    "input": "submission.py",
    "file_count": 1,
    "languages_detected": ["python"],
    "files": [
        {
            "filename": "submission.py",
            "language": "python",
            "metrics": {
                "syntax_valid": True,
                "lint_error_count": 0,
                "lint_warning_count": 2,
                "lint_violations": [{"code": "W291", "line": 3, "message": "x"}],
                "cyclomatic_complexity": 1.8,
                "max_nesting_depth": 1,
                "loc": 25,
                "comment_lines": 0,
                "blank_lines": 10,
                "function_count": 5,
                "class_count": 1,
                "docstring_coverage": 0.5,
                "naming_convention": "snake_case",
                "imports": [],
                "todo_count": 0,
                "print_count": 1,
                "type_annotation_coverage": 0.0,
                "has_main_guard": True,
                "bare_except_count": 0,
                "comprehension_count": 0,
            },
            "llm_signals": None,
        }
    ],
    "cross_file": {"file_count": 1, "languages_detected": ["python"]},
    "llm_signals": None,
}

PY_CONTENT = (
    "def main():\n    print('hi')\n\n\nif __name__ == '__main__':\n    main()\n"
)


def _make_code_assignment():
    """An assignment linked to a 'code' assessment type; returns assignment id."""
    from app.models.assessment import AssessmentType, assessment_types
    from app.models.assignment import Assignment, assignments

    atype = assessment_types.insert(
        AssessmentType(
            type_code="code",
            display_name="Code",
            is_active=True,
            created_at=datetime.now().isoformat(),
        )
    )
    assignment = assignments.insert(
        Assignment(
            course_id=1,
            title="Lab 3",
            created_by="i@example.com",
            status="active",
            assessment_type_id=atype.id,
            created_at=datetime.now().isoformat(),
        )
    )
    return assignment.id


def _make_draft(assignment_id=1, content=PY_CONTENT):
    from app.models.feedback import Draft, drafts

    res = drafts.insert(
        Draft(
            assignment_id=assignment_id,
            student_email="s@example.com",
            version=1,
            content=content,
            submission_date=datetime.now().isoformat(),
            status="submitted",
            word_count=len(content.split()),
        )
    )
    return res.id if hasattr(res, "id") else res


# ---- _flatten_code_response (pure) ----


def test_flatten_code_extracts_numeric_metrics():
    flat = signal_service._flatten_code_response(CODE_SAMPLE)
    assert flat["cyclomatic_complexity"] == 1.8
    assert flat["loc"] == 25.0
    assert flat["docstring_coverage"] == 0.5
    assert flat["lint_warning_count"] == 2.0
    assert flat["file_count"] == 1.0
    assert "lint_violations" not in flat  # list excluded
    assert "naming_convention" not in flat  # string excluded
    assert all(isinstance(v, float) for v in flat.values())


def test_flatten_code_keeps_meaningful_bools_as_01():
    flat = signal_service._flatten_code_response(CODE_SAMPLE)
    assert flat["syntax_valid"] == 1.0
    assert flat["has_main_guard"] == 1.0


def test_flatten_code_empty_response():
    assert signal_service._flatten_code_response({}) == {}
    assert signal_service._flatten_code_response({"files": []}) == {}


# ---- _code_filename ----


def test_code_filename_prefers_uploaded_original(monkeypatch):
    from app.models.assessment import SubmissionFile, submission_files

    did = _make_draft()
    submission_files.insert(
        SubmissionFile(
            draft_id=did,
            filename="abc.js",
            original_filename="solution.js",
            file_path="x",
            file_size=10,
            mime_type="text/plain",
            checksum="c",
            uploaded_at=datetime.now().isoformat(),
        )
    )
    from app.models.feedback import drafts
    from app.utils.db_query import by_id

    assert signal_service._code_filename(by_id(drafts, did)) == "solution.js"


def test_code_filename_sniffs_python_from_text():
    from app.models.feedback import drafts
    from app.utils.db_query import by_id

    did = _make_draft(content="def f():\n    return 1\n")
    assert signal_service._code_filename(by_id(drafts, did)) == "submission.py"


def test_code_filename_sniffs_javascript_from_text():
    from app.models.feedback import drafts
    from app.utils.db_query import by_id

    did = _make_draft(content="const x = 1;\nconsole.log(x);\n")
    assert signal_service._code_filename(by_id(drafts, did)) == "submission.js"


# ---- extraction routing by assessment type ----


def test_extract_routes_code_assignment_to_code_analyser(monkeypatch):
    calls = {"code": 0, "text": 0}

    def fake_code(content, filename):
        calls["code"] += 1
        assert filename.endswith(".py")
        return CODE_SAMPLE

    def fake_text(text):
        calls["text"] += 1
        return None

    monkeypatch.setattr(signal_service.analyser_client, "analyse_code", fake_code)
    monkeypatch.setattr(signal_service.analyser_client, "analyse_text", fake_text)

    aid = _make_code_assignment()
    did = _make_draft(assignment_id=aid)
    assert signal_service.extract_signals_for_draft(did) is True
    sigs = signal_service.get_signals_for_draft(did)
    assert calls == {"code": 1, "text": 0}
    assert all(s.source == "code-analyser" for s in sigs)
    assert {"cyclomatic_complexity", "syntax_valid", "loc"} <= {s.name for s in sigs}


def test_extract_untyped_assignment_still_uses_document_analyser(monkeypatch):
    """Assignments without a type linkage keep the essay/prose path."""
    sample = {"analysis": {"text_metrics": {"word_count": 10}}}
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_text", lambda t: sample
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_sentiment", lambda t: None
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_citations", lambda t, **kw: None
    )

    did = _make_draft(assignment_id=999)  # no such assignment -> default essay
    assert signal_service.extract_signals_for_draft(did) is True
    sigs = signal_service.get_signals_for_draft(did)
    assert all(s.source == "document-analyser" for s in sigs)


def test_extract_code_analyser_down_returns_false(monkeypatch):
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_code", lambda c, f: None
    )
    aid = _make_code_assignment()
    did = _make_draft(assignment_id=aid)
    assert signal_service.extract_signals_for_draft(did) is False
    assert signal_service.get_signals_for_draft(did) == []


# ---- type-aware scorer suggestions ----


def test_code_style_category_maps_to_code_signals():
    rules = signal_scorer.suggest_rules_for_category("Code style", type_code="code")
    names = {r.signal_name for r in rules}
    assert "lint_warning_count" in names
    assert "passive_voice_percentage" not in names
    assert all(r.signal_source == "code-analyser" for r in rules)


def test_essay_style_category_unchanged():
    rules = signal_scorer.suggest_rules_for_category("Style", type_code="essay")
    names = {r.signal_name for r in rules}
    assert "passive_voice_percentage" in names
    assert all(r.signal_source == "document-analyser" for r in rules)


def test_documentation_category_uses_docstring_coverage():
    rules = signal_scorer.suggest_rules_for_category("Documentation", type_code="code")
    assert [r.signal_name for r in rules] == ["docstring_coverage"]
    # 0-1 fraction maps onto a 20-95 score range
    assert signal_scorer.apply_transform(0.5, rules[0].transform) == 57.5


def test_unknown_type_falls_back_to_essay_suggestions():
    rules = signal_scorer.suggest_rules_for_category("Clarity", type_code="martian")
    assert {r.signal_name for r in rules} == {"flesch_score"}


def test_code_estimates_end_to_end(monkeypatch):
    """Signals + code-type assignment -> per-category estimates via auto-match."""
    from app.models.assignment import Rubric, RubricCategory, rubric_categories, rubrics
    from app.models.signals import Signal, signals

    aid = _make_code_assignment()
    did = _make_draft(assignment_id=aid)
    rubric = rubrics.insert(Rubric(assignment_id=aid, assessment_type_id=0))
    cat = rubric_categories.insert(
        RubricCategory(
            rubric_id=rubric.id,
            name="Complexity & design",
            description="",
            weight=1.0,
        )
    )
    now = datetime.now().isoformat()
    for name, value in (("cyclomatic_complexity", 1.8), ("max_nesting_depth", 1.0)):
        signals.insert(
            Signal(
                draft_id=did,
                source="code-analyser",
                name=name,
                value=value,
                raw="",
                created_at=now,
            )
        )

    estimates = signal_scorer.category_estimates(did, [cat])
    assert cat.id in estimates
    assert estimates[cat.id]["score"] == 90.0  # both signals in their best band
    assert estimates[cat.id]["suggested"] is True


# ---- registry resolution ----


def test_type_code_for_assignment_resolves_code():
    from app.assessment.registry import type_code_for_assignment

    aid = _make_code_assignment()
    assert type_code_for_assignment(aid) == "code"
    assert type_code_for_assignment(999999) == "essay"  # missing -> default


# ---- analyse_code client ----


def test_analyse_code_empty_returns_none():
    assert analyser_client.analyse_code("", "a.py") is None


def test_analyse_code_service_down_returns_none(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "post", boom)
    assert analyser_client.analyse_code(PY_CONTENT, "a.py") is None


def test_analyse_code_posts_multipart_with_filename(monkeypatch):
    seen = {}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return CODE_SAMPLE

    def fake_post(url, files=None, timeout=None):
        seen["url"] = url
        seen["files"] = files
        return FakeResp()

    monkeypatch.setattr(analyser_client.requests, "post", fake_post)
    assert analyser_client.analyse_code(PY_CONTENT, "solution.py") == CODE_SAMPLE
    assert seen["url"].endswith("/analyse")
    assert seen["files"]["file"][0] == "solution.py"


# ---- code files extract as plain text ----


def test_extract_file_content_reads_python_file():
    from starlette.datastructures import UploadFile

    from app.utils.file_handlers import extract_file_content

    upload = UploadFile(filename="solution.py", file=io.BytesIO(PY_CONTENT.encode()))
    assert asyncio.run(extract_file_content(upload)) == PY_CONTENT.strip()
