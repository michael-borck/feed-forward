"""The practice feedback engine: rubric + draft -> prompt -> parsed feedback.

Pure functions over plain dicts — no database, no accounts. The prompt
skeleton and JSON response contract come from the vendored shared contract
(see contracts.py); providers.py performs the actual model call.
"""

import json
import re
import statistics
from typing import Any

from feedforward_practice.contracts import level_for, prompt_contract


class RubricError(ValueError):
    """The .ffrubric payload is not usable."""


def validate_rubric(rubric: dict) -> dict:
    """Light structural validation of a parsed .ffrubric payload.

    (Full JSON-schema validation happens app-side where jsonschema is
    available; the engine only needs the fields it consumes.)
    """
    if not isinstance(rubric, dict) or rubric.get("kind") != "ffrubric":
        raise RubricError("Not a .ffrubric file")
    cats = rubric.get("rubric", {}).get("categories") or []
    if not cats:
        raise RubricError("Rubric has no categories")
    for cat in cats:
        if not cat.get("name"):
            raise RubricError("Rubric category missing a name")
    return rubric


def build_prompt(rubric: dict, draft_text: str) -> dict:
    """Render the shared prompt contract into {system, user} messages."""
    contract = prompt_contract()
    system = _section(contract, "System")
    user_template = _section(contract, "User")

    assignment = rubric.get("assignment", {})
    categories = rubric["rubric"]["categories"]
    rubric_lines = "\n".join(
        f"- {c['name']} ({c.get('weight', 0):.0f}%): {c.get('description', '')}"
        for c in categories
    )

    user = (
        user_template.replace("{{assignment_title}}", assignment.get("title", ""))
        .replace("{{assignment_description}}", assignment.get("description", ""))
        .replace("{{rubric_categories}}", rubric_lines)
        .replace("{{submission_text}}", draft_text)
    )
    return {"system": system.strip(), "user": user.strip()}


def _section(contract: str, heading: str) -> str:
    """Extract the System or User block from the prompt contract.

    Only ``## System`` and ``## User`` are structural markers; any other
    ``##`` headings (Assignment Context, Instructions, …) are part of the
    prompt text itself and must be preserved.
    """
    if heading == "System":
        m = re.search(r"^## System\n(.*?)(?=^## User)", contract, re.M | re.S)
    elif heading == "User":
        m = re.search(r"^## User\n(.*)", contract, re.M | re.S)
    else:
        m = None
    if not m:
        raise RuntimeError(f"prompt contract is missing the {heading} section")
    return m.group(1)


def parse_response(raw: str, rubric: dict) -> dict:
    """Parse a model response against the JSON contract.

    Tolerates code fences and stray prose around the JSON object. Categories
    are matched to rubric names case-insensitively; unmatched model
    categories are dropped, missing ones reported.
    """
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("No JSON object found in model response")
        text = text[start : end + 1]

    data = json.loads(text)
    wanted = {
        c["name"].strip().lower(): c["name"] for c in rubric["rubric"]["categories"]
    }
    categories = []
    for cat in data.get("categories", []):
        key = str(cat.get("name", "")).strip().lower()
        if key not in wanted:
            continue
        score = max(0.0, min(100.0, float(cat.get("score", 0))))
        categories.append(
            {
                "name": wanted[key],
                "score": score,
                "feedback": str(cat.get("feedback", "")).strip(),
                "strengths": [str(s) for s in cat.get("strengths", [])][:3],
                "improvements": [str(s) for s in cat.get("improvements", [])][:3],
            }
        )
    return {
        "overall_feedback": str(data.get("overall_feedback", "")).strip(),
        "categories": categories,
        "missing_categories": [
            name
            for key, name in wanted.items()
            if key not in {c["name"].strip().lower() for c in categories}
        ],
    }


def aggregate_runs(runs: list[dict], rubric: dict) -> dict:
    """Aggregate 1..N parsed runs into the final feedback payload.

    Scores: mean per category. Text: taken from the run whose category score
    is closest to the aggregated mean (a 'most representative run' rule —
    deliberately simple, mirroring the server's mean aggregation default).
    """
    if not runs:
        raise ValueError("No successful runs to aggregate")

    weights = {
        c["name"]: float(c.get("weight", 0)) for c in rubric["rubric"]["categories"]
    }
    by_name: dict[str, list[dict]] = {}
    for run in runs:
        for cat in run["categories"]:
            by_name.setdefault(cat["name"], []).append(cat)

    categories: list[dict[str, Any]] = []
    for name, cats in by_name.items():
        mean = statistics.fmean(c["score"] for c in cats)
        representative = min(cats, key=lambda c: abs(c["score"] - mean))
        categories.append(
            {
                "name": name,
                "weight": weights.get(name, 0),
                "score": round(mean, 1),
                "level": level_for(mean),
                "feedback": representative["feedback"],
                "strengths": representative["strengths"],
                "improvements": representative["improvements"],
                "runs": len(cats),
            }
        )
    # Keep rubric order
    order = [c["name"] for c in rubric["rubric"]["categories"]]
    categories.sort(key=lambda c: order.index(c["name"]) if c["name"] in order else 99)

    total_weight = sum(c["weight"] for c in categories)
    if total_weight > 0:
        overall = sum(c["score"] * c["weight"] for c in categories) / total_weight
    else:
        overall = statistics.fmean(c["score"] for c in categories)

    return {
        "overall": {"score": round(overall, 1), "level": level_for(overall)},
        "overall_feedback": next(
            (r["overall_feedback"] for r in runs if r["overall_feedback"]), ""
        ),
        "categories": categories,
        "runs": len(runs),
    }
