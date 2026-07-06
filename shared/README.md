# Shared contracts — server ↔ desktop

Single source of truth for everything the FeedForward server (Python) and
FeedForward Desktop (Tauri, `desktop/`) must agree on. Both apps read these
files — the server at runtime/test time, the desktop app vendored at build
time — so a change here is one commit that moves both products together.
CI contract tests fail if either side hard-codes values that disagree.

| File | Contract |
|---|---|
| `ffrubric.schema.json` | The `.ffrubric` file format: what the server's "Export rubric" emits and the desktop app imports |
| `levels.json` | Score bands → qualitative level words + semantic colour, used everywhere feedback is shown to students |
| `feedback-prompt.md` | Canonical feedback prompt skeleton and the JSON response contract expected from models |

Rules:
- Never edit generated copies elsewhere; edit here.
- Additive schema changes bump `formatVersion` minor; breaking changes bump
  major and must keep an import path for the previous version.
