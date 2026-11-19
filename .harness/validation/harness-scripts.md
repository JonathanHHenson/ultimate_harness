# Harness Script Validation

## After changing harness scripts, CI check scripts, tests, or runtime dependencies

- Use the harness interpreter for diagnostics. If basedpyright is available and no checker is configured, run `basedpyright -p .harness/scripts --pythonpath .harness/.venv/bin/python --verbose` from the project root, passing the changed Python paths. Verify it found the expected files.
- For Python work, run `ruff check --config ruff.toml .harness/scripts scripts .agents/skills` from the project root and require a successful exit. Use the Ruff version pinned in the [packaging workflow](../../.github/workflows/build-harness-skills.yml). With uv, run the same check using `uvx --from ruff==VERSION ruff check --config ruff.toml .harness/scripts scripts .agents/skills`, where `VERSION` is the workflow pin.
- If Ruff is unavailable, run `.harness/.venv/bin/python .agents/skills/python-development/scripts/check_complexity.py .harness/scripts scripts .agents/skills` for local complexity evidence. Record which Ruff lint checks remain unverified.
- Set up [the harness Python environment](../agents/python-environment.md). From the project root, run `.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -v`.
- For changed behavior, exercise representative success and failure cases in an isolated temporary project. Use existing behavioral tests when they cover those cases; add coverage for uncovered behavior that warrants testing.
- Require the suite and relevant command scenarios to pass. Verify outputs, exit status, and resulting state rather than source structure or exact implementation.

## After changing browser assets or their validation tooling

- Run the applicable checks from the project root. The skill packaging workflow runs all three.

```sh
.agents/skills/javascript-development/scripts/check-complexity.sh '.agents/skills/**/*.{js,mjs,cjs}'
.agents/skills/html-development/scripts/validate-html.sh '.agents/skills/**/*.html'
.agents/skills/css-development/scripts/validate-css.sh '.agents/skills/**/*.css'
```

- Exercise changed browser behavior and layout with representative content, including a narrow and wide viewport when presentation changes.

## Before considering changed scripts validated

- Resolve failures and repeat affected checks; broaden checks when new changes or failures justify it. If a dependency or environment prevents a check, record the specific blocker and unrun check in feature memory instead of claiming success.
- Record the commands, outcomes, and relevant acceptance evidence in the feature worklog without repeating evidence already captured by a requirement transition.
