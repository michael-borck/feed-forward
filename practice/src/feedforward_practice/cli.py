"""CLI: `feedforward-practice assess` (direct) and `serve` (desktop sidecar)."""

import argparse
import json
import pathlib
import sys

from feedforward_practice.providers import ProviderConfig
from feedforward_practice.run import practice_feedback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="feedforward-practice",
        description="Practice feedback on a draft against an instructor rubric",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_assess = sub.add_parser("assess", help="Run practice feedback once")
    p_assess.add_argument("--rubric", required=True, help=".ffrubric file")
    p_assess.add_argument("--draft", required=True, help="draft text file (.txt/.md)")
    p_assess.add_argument("--runs", type=int, default=1)
    p_assess.add_argument("--base-url", default="")
    p_assess.add_argument("--api-key", default="")
    p_assess.add_argument("--model", default="")
    p_assess.add_argument("--json", action="store_true", help="raw JSON output")
    p_assess.set_defaults(func=_cmd_assess)

    p_serve = sub.add_parser(
        "serve",
        help=(
            "Run the HTTP API (needs the [serve] extra). Set "
            "FEEDFORWARD_PRACTICE_AUTH_TOKEN to require a bearer token."
        ),
    )
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8022)
    p_serve.set_defaults(func=_cmd_serve)

    args = parser.parse_args(argv)
    return args.func(args)


def _cmd_assess(args) -> int:
    rubric = json.loads(pathlib.Path(args.rubric).read_text())
    draft = pathlib.Path(args.draft).read_text()
    provider = ProviderConfig.from_env().merged(
        {"base_url": args.base_url, "api_key": args.api_key, "model": args.model}
    )
    result = practice_feedback(rubric, draft, provider, args.runs)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    overall = result["overall"]
    print(f"\nOverall: {overall['level']['label']}\n")
    for cat in result["categories"]:
        print(f"## {cat['name']} — {cat['level']['label']}")
        if cat["feedback"]:
            print(f"   {cat['feedback']}")
        for s in cat["strengths"]:
            print(f"   + {s}")
        for i in cat["improvements"]:
            print(f"   > {i}")
        print()
    return 0


def _cmd_serve(args) -> int:
    try:
        import uvicorn
    except ImportError:
        print(
            "serve needs the [serve] extra: pip install 'feedforward-practice[serve]'",
            file=sys.stderr,
        )
        return 1
    uvicorn.run("feedforward_practice.api:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
