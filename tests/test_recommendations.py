"""Tests for next-step recommendations (Phase 2.3) on the real feedback schema."""

from types import SimpleNamespace

from app.services.progress_analyzer import ProgressAnalyzer


def _cat(cid, name, weight=1.0, description=""):
    return SimpleNamespace(id=cid, name=name, weight=weight, description=description)


def _fb(category_id, score, text=""):
    return SimpleNamespace(
        draft_id=1,
        category_id=category_id,
        aggregated_score=score,
        feedback_text=text,
        status="released",
    )


FEEDBACK_TEXT = """Strengths:
- Clear thesis statement

Areas for improvement:
- Add topic sentences to paragraphs three and four
- Reduce passive constructions
"""


def _analyzer():
    return ProgressAnalyzer([], [])


def test_recommendations_use_per_category_rows():
    cats = [_cat(1, "Structure", weight=2.0), _cat(2, "Clarity", weight=1.0)]
    feedback = [_fb(1, 55.0, FEEDBACK_TEXT), _fb(2, 80.0)]

    recs = _analyzer().get_next_steps_recommendations(feedback, cats)

    assert [r["category"] for r in recs] == ["Structure", "Clarity"]
    assert recs[0]["priority"] == "high"
    assert recs[0]["current_score"] == 55.0
    assert recs[1]["priority"] == "low"


def test_excellent_categories_are_skipped():
    cats = [_cat(1, "Structure"), _cat(2, "Clarity")]
    feedback = [_fb(1, 95.0), _fb(2, 92.0)]
    assert _analyzer().get_next_steps_recommendations(feedback, cats) == []


def test_prioritised_by_weighted_impact():
    # Same score gap, but Structure carries 3x the weight -> ranked first.
    cats = [_cat(1, "Clarity", weight=1.0), _cat(2, "Structure", weight=3.0)]
    feedback = [_fb(1, 70.0), _fb(2, 70.0)]

    recs = _analyzer().get_next_steps_recommendations(feedback, cats)
    assert [r["category"] for r in recs] == ["Structure", "Clarity"]
    assert recs[0]["potential_impact"] == 3.0 * 0.3


def test_example_lifted_from_improvement_section():
    cats = [_cat(1, "Structure")]
    feedback = [_fb(1, 60.0, FEEDBACK_TEXT)]

    recs = _analyzer().get_next_steps_recommendations(feedback, cats)
    assert recs[0]["example"] == "Add topic sentences to paragraphs three and four"


def test_example_falls_back_to_first_bullet():
    text = "Overall comments:\n- Tighten the introduction\n"
    recs = _analyzer().get_next_steps_recommendations(
        [_fb(1, 60.0, text)], [_cat(1, "Structure")]
    )
    assert recs[0]["example"] == "Tighten the introduction"


def test_resources_match_category_keywords():
    cats = [_cat(1, "Referencing"), _cat(2, "Code quality"), _cat(3, "Originality")]
    feedback = [_fb(1, 60.0), _fb(2, 60.0), _fb(3, 60.0)]

    recs = {
        r["category"]: r
        for r in _analyzer().get_next_steps_recommendations(feedback, cats)
    }

    assert "Citation" in recs["Referencing"]["resources"][0]["title"]
    assert "PEP 8" in recs["Code quality"]["resources"][0]["title"]
    assert recs["Originality"]["resources"] == []  # no keyword match -> no links


def test_empty_feedback_returns_empty():
    assert _analyzer().get_next_steps_recommendations([], [_cat(1, "X")]) == []


def test_category_without_feedback_row_is_skipped():
    cats = [_cat(1, "Structure"), _cat(2, "Clarity")]
    feedback = [_fb(1, 60.0)]  # no row for Clarity
    recs = _analyzer().get_next_steps_recommendations(feedback, cats)
    assert [r["category"] for r in recs] == ["Structure"]
