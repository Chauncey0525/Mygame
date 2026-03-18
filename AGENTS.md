# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a Python/Flask web game called **巅峰对决 (Peak Showdown)** — a gacha/RPG featuring historical heroes. It is a single monolithic Flask application with an embedded SQLite database (no external services required).

### Running the dev server

```bash
python3 run.py
```

Server runs at `http://localhost:5000` with debug mode enabled. See `README.md` for full details.

### Key caveats

- **`instance/` directory**: The SQLite database is stored at `instance/history_heroes.db`. This directory must exist before starting the server; if missing, create it with `mkdir -p instance`. The app auto-creates tables on first run.
- **`python3` not `python`**: The VM does not have `python` aliased to `python3`. Always use `python3` explicitly.
- **SMS verification in dev mode**: Registration requires phone + SMS code. In dev mode, the verification code is printed to the Flask console output (look for `[DEV SMS] phone=... code=...`). No real SMS is sent.
- **No automated test suite**: The repository does not include unit or integration tests. Validation is done via manual testing through the browser.
- **No dedicated linter config**: The codebase does not include flake8/pylint/ruff configuration. Use `python3 -m py_compile <file>` for basic syntax checks.
- **Flask debug reloader**: When starting with `python3 run.py`, the Flask reloader spawns a child process. This is normal behavior — the server is ready when you see "Running on http://..." in the logs.
- **Pre-commit hook**: An optional pre-commit hook auto-updates the README's "recent commits" section. Install with `pip install pre-commit && pre-commit install` if needed.
