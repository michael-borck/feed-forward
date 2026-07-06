"""Family manifest — feedforward-practice is a lens, not an analyser."""

from lens_contract import make_manifest

MANIFEST = make_manifest(
    name="feedforward-practice",
    role="lens",
    accepts=["text"],
    produces="rubric-aligned formative feedback (practice)",
    auto_routable=False,
)
