"""
Signal evidence (ADR 012, phase S2).

Records signal-derived rubric scores as a synthetic "Signal Engine" ModelRun so
they flow through the SAME aggregation as LLM scores (the synthetic-model-run
decision in ADR 012 §4). Aggregation keys off ``CategoryScore.model_run_id``,
not model identity, so a sentinel ``model_id`` is enough — no ``ai_models`` row,
and the generator's active-model lookup is unaffected.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from app.models.feedback import (
    CategoryScore,
    ModelRun,
    category_scores,
    drafts,
    model_runs,
)
from app.services import signal_scorer
from app.utils.db_query import by_id, first, where

logger = logging.getLogger(__name__)

# Sentinel model id for the Signal Engine. Distinct from real LLM ids (positive)
# and the mock-feedback run (0).
SIGNAL_MODEL_ID = -1


def produce_signal_run(draft_id: int) -> Optional[int]:
    """
    Create a synthetic ModelRun carrying signal-derived CategoryScores for a draft.

    Returns the new model_run id, or None if there's no rubric or no estimate
    (so callers can simply skip it). Pure persistence — no LLM, no network.
    """
    from app.models.assignment import rubric_categories, rubrics

    draft = by_id(drafts, draft_id)
    if draft is None:
        logger.warning("signal evidence: draft %s not found", draft_id)
        return None

    rubric = first(rubrics, assignment_id=draft.assignment_id)
    if rubric is None:
        return None
    categories = where(rubric_categories, rubric_id=rubric.id)
    if not categories:
        return None

    estimates = signal_scorer.category_estimates(draft_id, categories)
    if not estimates:
        return None

    run = model_runs.insert(
        ModelRun(
            draft_id=draft_id,
            model_id=SIGNAL_MODEL_ID,
            run_number=1,
            timestamp=datetime.now().isoformat(),
            prompt="signal-based assessment (lens)",
            raw_response=json.dumps(estimates),
            status="complete",
        )
    )
    run_id = run.id if hasattr(run, "id") else run

    for category_id, estimate in estimates.items():
        category_scores.insert(
            CategoryScore(
                model_run_id=run_id,
                category_id=category_id,
                score=estimate["score"],
                confidence=estimate["confidence"],
            )
        )

    logger.info(
        "signal evidence: stored %d category scores for draft %s (run %s)",
        len(estimates),
        draft_id,
        run_id,
    )
    return run_id
