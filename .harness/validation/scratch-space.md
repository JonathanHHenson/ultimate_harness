# Scratch Space Validation

## After changing scratch conventions, session creation, or the scratch ignore rule

- From the project root, run `.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -p test_agent_sessions.py -v`, or use current passing full-suite results that already include these tests.
- Require unique usable session directories, preservation of existing human/session artifacts, explicit-root support, and non-destructive rejection of unusable storage. The tests use the actual `.gitignore` in an isolated Git repository to confirm root and nested scratch artifacts are ignored while project files remain trackable.
- Review the session-start route, workspace reuse, and end-of-session instructions. Require local persistence and separate locations for feature memory and maintained automation; writing an ad hoc scratch note alone does not trigger these implementation checks.

## Before considering scratch provisioning validated

- Resolve failures and repeat affected checks. Record outcomes and any blocked or unrun checks in feature memory; do not report them as passed.
