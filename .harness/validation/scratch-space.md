# Scratch Workspace Validation

## After changing scratch conventions, session creation, or the scratch ignore rule

- From the project root, run `.harness/.venv/bin/python -m unittest discover -s .harness/scripts/tests -p test_agent_sessions.py -v`, or use current passing full-suite results that already include these tests.
- Require a unique usable scratch workspace for each agent session, preservation of existing human and agent artifacts, explicit-root support, and non-destructive rejection of unusable storage. The tests use the actual `.gitignore` in an isolated Git repository to confirm root and nested scratch artifacts are ignored while project files remain trackable.
- Review the agent session startup route, scratch workspace reuse, and instructions for ending the agent session. Require local persistence and separate locations for feature records and maintained automation. Apply these checks to changes to the scratch workspace contract or implementation.

## Before considering scratch provisioning validated

- Resolve failures and repeat affected checks. Record outcomes and any blocked or unrun checks in the feature record.
