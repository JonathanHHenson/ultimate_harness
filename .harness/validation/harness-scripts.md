# Harness Script Validation

## After changing harness scripts, tests, or runtime dependencies

- Set up [the harness Python environment](../agents/python-environment.md). From the project root, run `.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -v`.
- For changed behavior, exercise representative success and failure cases in an isolated temporary project. Use existing behavioral tests when they cover those cases; add coverage for uncovered behavior that warrants testing.
- Require the suite and relevant command scenarios to pass. Verify outputs, exit status, and resulting state rather than source structure or exact implementation.

## Before considering changed scripts validated

- Resolve failures and repeat affected checks; broaden checks when new changes or failures justify it. If a dependency or environment prevents a check, record the specific blocker and unrun check in feature memory instead of claiming success.
- Record the commands, outcomes, and relevant acceptance evidence in the feature worklog without repeating evidence already captured by a requirement transition.
