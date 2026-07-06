# feedforward-practice

Private practice feedback on drafts against an instructor rubric — the
engine and sidecar API behind **FeedForward Desktop**.

A student opens a `.ffrubric` file (exported by their instructor from
[FeedForward](https://github.com/michael-borck/feed-forward)), pastes or
opens a draft, points the app at a model endpoint they control, and gets
rubric-aligned formative feedback rendered with FeedForward's qualitative
levels (the dartboard: "Closing in", "On the board", …). Nothing is stored
on a server; there are no accounts.

## Model endpoints

One OpenAI-compatible client covers all supported setups:

| Setup | Base URL | Key |
|---|---|---|
| Local Ollama (default) | `http://localhost:11434/v1` | none |
| Remote Ollama behind a proxy | your server's URL | bearer token |
| BYOK (OpenAI, Anthropic-compat, OpenRouter, Groq…) | provider URL | your key |

Configure via arguments or `FEEDFORWARD_PRACTICE_BASE_URL`,
`FEEDFORWARD_PRACTICE_API_KEY`, `FEEDFORWARD_PRACTICE_MODEL`.

## Usage

```bash
pip install feedforward-practice            # engine + CLI
pip install "feedforward-practice[serve]"   # + the HTTP API for the desktop shell

feedforward-practice assess --rubric essay1.ffrubric --draft draft.md
feedforward-practice serve --port 8022
```

## Contracts

The rubric format, level words, and prompt/JSON contract are vendored at
build time from the FeedForward repo's `shared/` directory — the single
source of truth both the server and this package test against.

Part of the FeedForward project · MIT
