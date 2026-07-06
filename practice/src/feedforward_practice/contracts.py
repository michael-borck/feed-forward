"""Access to the vendored server↔desktop contract files.

In an installed wheel these live in ``feedforward_practice/contracts/``
(vendored at build time from the repo's ``shared/``); in a repo checkout we
fall back to ``../../shared`` so editable installs and tests use the live
files.
"""

import json
import pathlib
from functools import cache

_VENDORED = pathlib.Path(__file__).parent / "contracts"
_REPO_SHARED = pathlib.Path(__file__).resolve().parents[3] / "shared"


def _contract_path(name: str) -> pathlib.Path:
    vendored = _VENDORED / name
    if vendored.exists():
        return vendored
    return _REPO_SHARED / name


@cache
def levels_spec() -> dict:
    with open(_contract_path("levels.json")) as f:
        return json.load(f)


@cache
def rubric_schema() -> dict:
    with open(_contract_path("ffrubric.schema.json")) as f:
        return json.load(f)


@cache
def prompt_contract() -> str:
    return _contract_path("feedback-prompt.md").read_text()


def level_for(score: float) -> dict:
    """Qualitative level (label + colour) for a 0-100 score."""
    spec = levels_spec()
    label = next(
        (lv["label"] for lv in spec["levels"] if score >= lv["min"]),
        spec["levels"][-1]["label"],
    )
    color = next(
        (b["color"] for b in spec["colorBands"] if score >= b["min"]),
        spec["colorBands"][-1]["color"],
    )
    return {"label": label, "color": color}
