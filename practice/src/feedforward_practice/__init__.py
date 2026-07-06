"""feedforward-practice — private practice feedback on drafts.

Students open an instructor-exported .ffrubric file, paste a draft, choose
their own model endpoint (local Ollama by default), and get rubric-aligned
formative feedback rendered with the same qualitative levels as FeedForward
itself. This package is the engine and sidecar API behind FeedForward
Desktop; it holds no accounts and stores nothing.
"""

__version__ = "0.1.0"

from feedforward_practice.providers import ProviderConfig  # noqa: F401
from feedforward_practice.run import practice_feedback  # noqa: F401
