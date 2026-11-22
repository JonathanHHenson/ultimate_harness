# Local Scratch Space Contract

Use this contract when building or maintaining the harness's local ad hoc storage.
Paths below are relative to the project root.

## Shared local storage

Provision `.scratch/` and ignore the entire directory with `/.scratch/` in the
root `.gitignore`. Both the human and agent may use it for ad hoc documents and
scripts that persist on the local machine without normal Git tracking or pushes.
Humans can use the shared root or their own subdirectories; reserve
`.scratch/agent_sessions/` for agents' scratch workspaces.

Keep provisioning instructions and the helper tracked outside `.scratch/` so a
new checkout can recreate the structure. Do not force-add scratch artifacts or
use tracked placeholder files inside the ignored tree. Verify scratch content is
not already tracked; preserve local files if correcting existing Git tracking.

## Scratch workspaces for agent sessions

Use a small script in `.harness/scripts/` to create a unique directory under
`.scratch/agent_sessions/` and print its absolute path. In this project, run:

```sh
.harness/.venv/bin/python .harness/scripts/create_agent_session.py
```

Set up [the harness environment](python-environment.md) first. Run from the
project root or pass `--root PATH`. The helper uses only Python's
standard library. A UTC timestamp prefix makes each session easy to recognise;
exclusive random directory creation prevents collisions. Reject unusable or
symlinked storage with a nonzero exit status rather than writing elsewhere.

Add an `At the start of every session` trigger to `AGENTS.md`, routing to concise
scratch instructions in `.harness/agents/`. Create a workspace once for a new
session, retain the returned path, and reuse it for that session's documents and
ad hoc scripts. If resuming the same session with a known workspace, reuse it;
if no workspace is known, create a fresh unique directory instead of guessing
which previous session's files to overwrite.

## Persistence and placement

Leave files in place when a session ends. Do not automatically purge scratch
storage, human documents, or previous session directories. Edit human-provided
documents or another session's artifacts only when the user's task calls for it.
Scratch files are local to this checkout; Git does not share them with another
machine or recreate their contents.

Use the current agent session's scratch workspace for ad hoc work. Continue to maintain
feature definitions, technical designs, and progress history under
`.harness/features/`. Put maintained reusable scripts under `.harness/scripts/`
with appropriate tests rather than depending on ignored session artifacts.
Promote durable shared documentation into tracked project documentation when
appropriate.

## Validation

Route scratch provisioning, session-helper, and ignore-rule changes through
`.harness/VALIDATE.md` to an appropriate situational ruleset. Check unique usable
directories, explicit project roots, preservation of existing human/session
files, and non-destructive failure on invalid storage. Use isolated Git fixtures
with the actual ignore file to verify both shared-root and nested-session
artifacts are ignored while project sources remain trackable. Keep tests focused
on these behaviors rather than exact directory names or helper implementation.
Ordinary edits to local ad hoc notes do not by themselves change provisioning.
