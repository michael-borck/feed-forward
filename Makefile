.PHONY: run test fmt lint sidecars sidecars-stop sidecars-status

# Run the dev server (http://localhost:5001)
run:
	python app.py

# Tests
test:
	uv run pytest

# Format + lint (Ruff)
fmt:
	uv run ruff format .
	uv run ruff check . --fix

lint:
	uv run ruff check .

# Lens analyser sidecars (signals; ADR 012). See scripts/sidecars.sh for
# overrides (LENS_DIR, *_PORT). These are sibling repos, not pip deps.
sidecars:
	@bash scripts/sidecars.sh start

sidecars-stop:
	@bash scripts/sidecars.sh stop

sidecars-status:
	@bash scripts/sidecars.sh status
