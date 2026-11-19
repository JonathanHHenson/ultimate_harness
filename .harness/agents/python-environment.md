# Harness Python Instructions

## At the start of every session

- From the project root, run `python3 .harness/scripts/init_venv.py` with an available Python 3.11+ (use `python` if that is its command). Setup creates or reuses `.harness/.venv/` and installs the harness requirements. Resolve setup errors before using the environment.
- When using uv, setup defaults to the ignored `.harness/.uv-cache/`. An explicit `UV_CACHE_DIR` overrides this default.

## When running a Python script or check for the harness

- Invoke it with `.harness/.venv/bin/python` from the project root. This includes harness scripts, harness validation, and ad hoc Python scripts used for harness work. The environment bootstrap uses the available host Python. Use the project environment for project scripts and checks.

## When changing harness Python dependencies

- Declare them in `.harness/scripts/requirements.txt` and rerun the bootstrap before validation.
