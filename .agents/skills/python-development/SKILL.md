---
name: python-development
description: Write, format, lint, test, and review Python code using the project interpreter and tools. Use for Python source, scripts, tests, and Python-specific development tasks.
---

# Python Development

- Identify the supported Python version, environment, dependency manager, and project commands in its docs and configuration. Use the harness interpreter for harness tooling and the project interpreter for project code.
- Keep I/O and validation at clear boundaries. Use types to clarify contracts, context managers for resources, and explicit error handling where callers can recover. Match the project’s sync or async conventions.
- Prefer Ruff for linting, formatting, and complexity analysis. Follow the project’s configured commands. Use `ruff check PATHS` for linting and `ruff format --check PATHS` for formatting checks. Use the project’s type checker separately. With BasedPyright, pass the project configuration and interpreter and confirm the files analyzed. [Ruff](https://docs.astral.sh/ruff/) · [BasedPyright](https://docs.basedpyright.com/)
- For complexity, use Ruff’s `C901` rule. Configure it in the project’s Ruff settings or use `ruff check --select C901 PATHS` for a focused check. The default limit is 10. Honor the project’s configured limit and treat violations as validation failures. [Ruff complexity rule](https://docs.astral.sh/ruff/rules/complex-structure/)
- If Ruff and any configured alternative are unavailable, run [the bundled complexity checker](scripts/check_complexity.py) with Python 3.11 or later on the changed files or directories. Use `--max-complexity N` for the project’s explicit limit. Record the tool used, since branch counts can vary across analyzers.
- Use the configured test framework. For a standard-library suite, run `python -m unittest discover -s TEST_DIRECTORY`. With pytest configured, run the project’s pytest command. Start with public behavior for the changed paths, then run the required full suite. [Python unittest](https://docs.python.org/3/library/unittest.html) · [pytest](https://docs.pytest.org/)
