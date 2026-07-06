"""Top-level orchestration: rubric + draft + provider -> aggregated feedback."""

from feedforward_practice import engine
from feedforward_practice.providers import ProviderConfig, ProviderError, chat


def practice_feedback(
    rubric: dict,
    draft_text: str,
    provider: ProviderConfig,
    num_runs: int = 1,
) -> dict:
    """Run the full practice loop.

    Returns the aggregated feedback payload plus run diagnostics. Raises
    RubricError / ProviderError / ValueError for unusable inputs; partial
    run failures are tolerated as long as one run parses.
    """
    rubric = engine.validate_rubric(rubric)
    if not draft_text or not draft_text.strip():
        raise ValueError("Draft is empty")
    num_runs = max(1, min(int(num_runs), 5))

    prompt = engine.build_prompt(rubric, draft_text)

    parsed_runs: list[dict] = []
    errors: list[str] = []
    for _ in range(num_runs):
        try:
            raw = chat(provider, prompt["system"], prompt["user"])
            parsed_runs.append(engine.parse_response(raw, rubric))
        except (ProviderError, ValueError) as e:  # noqa: PERF203
            errors.append(str(e))

    if not parsed_runs:
        raise ProviderError(
            "All model runs failed: " + (errors[0] if errors else "unknown error")
        )

    result = engine.aggregate_runs(parsed_runs, rubric)
    result["failed_runs"] = len(errors)
    result["word_count"] = len(draft_text.split())
    return result
