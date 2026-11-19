# Harness Python Environment

Keep harness Python dependencies in a dedicated, Git-ignored `.harness/.venv/`.
Declare them in `.harness/scripts/requirements.txt`. Project dependencies
belong in the project's manifest and environment.

## At the start of every session

- Route setup from `AGENTS.md` before any other harness scripts. Use a focused
  bootstrap script under `.harness/scripts/` with an available Python 3.11+.
  In this project, run `python3 .harness/scripts/init_venv.py` from the project root.
- Create the environment with uv when available. Otherwise try
  `python -m venv`, then `python -m virtualenv` if standard creation fails.
  Reuse an existing usable environment and install the harness manifest with
  an explicit environment interpreter via uv or that interpreter's pip.
- Keep setup safe to repeat. Ignore generated local files, including any
  bootstrap lock and uv cache. Default uv subprocesses to
  `.harness/.uv-cache/` and honor an explicit `UV_CACHE_DIR`. Verify first
  setup and reuse in a temporary project.

## When running or changing harness Python automation

- Invoke `.harness/.venv/bin/python` explicitly for harness scripts, memory
  operations, and validation on macOS and Linux. Run project scripts using
  the project's own runtime. The bootstrap runs with available host Python.
- Rerun setup when the harness manifest changes. Validate with the harness
  interpreter and check that setup preserves any existing project environment.
