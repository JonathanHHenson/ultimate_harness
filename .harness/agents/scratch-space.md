# Scratch Workspace Instructions

## At the start of every session

- From the project root, run `.harness/.venv/bin/python .harness/scripts/create_agent_session.py` once for a new session. Retain the returned absolute path and reuse it throughout that session; if this session already has a known workspace, continue using it.
- Resolve creation errors before using the workspace; do not fall back to another session's directory.

## When creating ad hoc documents or scripts

- Put agent working artifacts in this session's directory under `.scratch/agent_sessions/`. Keep `.scratch/` available for human documents; preserve human files and other session directories unless the user requests changes.
- Keep feature definitions, designs, and worklogs in `.harness/features/`. Put maintained reusable automation in `.harness/scripts/` rather than relying on scratch artifacts.
- Keep `.scratch/` gitignored; do not force-add its contents.

## When ending a session

- Leave local scratch artifacts in place for later use. Do not automatically clear this session, other sessions, or human documents.
