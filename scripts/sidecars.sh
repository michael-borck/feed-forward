#!/usr/bin/env bash
#
# Start (or stop) the lens analyser sidecars FeedForward consumes for signals
# (ADR 012). They are sibling repos with their own venvs/builds, not Python
# dependencies of FeedForward — this script just launches them on the ports the
# app expects so you don't have to remember three commands.
#
#   scripts/sidecars.sh start   # start any that aren't already up (default)
#   scripts/sidecars.sh stop    # stop the ones this script started
#   scripts/sidecars.sh status  # show reachability
#
# Override locations/ports with env vars (defaults shown):
#   LENS_DIR=~/Projects/lens
#   DOCUMENT_ANALYSER_PORT=8000  CODE_ANALYSER_PORT=8004  CITE_SIGHT_PORT=3001
#
# Tested against: document-analyser 0.7.x, code-analyser 1.2.x, cite-sight 0.4.x
# (keep in sync with the analyser versions pinned in .env.example).

set -euo pipefail

LENS_DIR="${LENS_DIR:-$HOME/Projects/lens}"
DOC_PORT="${DOCUMENT_ANALYSER_PORT:-8000}"
CODE_PORT="${CODE_ANALYSER_PORT:-8004}"
CITE_PORT="${CITE_SIGHT_PORT:-3001}"
RUN_DIR="${TMPDIR:-/tmp}/feedforward-sidecars"
mkdir -p "$RUN_DIR"

doc_bin="$LENS_DIR/document-analyser/.venv/bin/document-analyser"
code_bin="$LENS_DIR/code-analyser/.venv/bin/code-analyser"
cite_entry="$LENS_DIR/cite-sight/packages/server/dist/index.js"

is_up() { curl -s -m 2 -o /dev/null "http://127.0.0.1:$1/health" 2>/dev/null; }

start_one() { # name port workdir cmd...
  local name=$1 port=$2 workdir=$3; shift 3
  if is_up "$port"; then echo "  $name already up on :$port"; return; fi
  if [ ! -e "$1" ] && [ "$1" != node ]; then
    echo "  ! $name not found ($1) — skipping"; return
  fi
  echo "  starting $name on :$port ..."
  # Run from the analyser's own repo dir so its pydantic settings read ITS
  # .env, not FeedForward's (whose LLM keys would fail extra-forbidden checks).
  (cd "$workdir" && "$@" >"$RUN_DIR/$name.log" 2>&1 & echo $! >"$RUN_DIR/$name.pid")
}

cmd="${1:-start}"
case "$cmd" in
  start)
    echo "Starting lens sidecars (LENS_DIR=$LENS_DIR):"
    start_one document-analyser "$DOC_PORT" "$LENS_DIR/document-analyser" \
      "$doc_bin" serve --port "$DOC_PORT"
    start_one code-analyser "$CODE_PORT" "$LENS_DIR/code-analyser" \
      "$code_bin" serve --port "$CODE_PORT"
    PORT="$CITE_PORT" start_one cite-sight "$CITE_PORT" \
      "$LENS_DIR/cite-sight/packages/server" node "$cite_entry"
    echo "Logs in $RUN_DIR/*.log"
    ;;
  stop)
    echo "Stopping sidecars this script started:"
    for name in document-analyser code-analyser cite-sight; do
      pidfile="$RUN_DIR/$name.pid"
      if [ -f "$pidfile" ] && kill "$(cat "$pidfile")" 2>/dev/null; then
        echo "  stopped $name"
      fi
      rm -f "$pidfile"
    done
    ;;
  status)
    for pair in "document-analyser:$DOC_PORT" "code-analyser:$CODE_PORT" "cite-sight:$CITE_PORT"; do
      name=${pair%:*}; port=${pair#*:}
      if is_up "$port"; then echo "  ● $name up   (:$port)"; else echo "  ○ $name down (:$port)"; fi
    done
    ;;
  *)
    echo "usage: $0 [start|stop|status]" >&2; exit 2 ;;
esac
