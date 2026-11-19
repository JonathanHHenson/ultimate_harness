# Design: Local Scratch Space

## F-1: Shared persistent local storage

Ignore the entire project-root `.scratch/` directory with `/.scratch/` in the
root `.gitignore`. Human documents may use the shared root or human-chosen
subdirectories. Agent session work uses the reserved `agent_sessions` subtree.
No helper or lifecycle instruction deletes scratch contents at session end.
The folder is local working material, not a replacement for feature memory.
The ignore rule is shared with other checkouts; session startup recreates empty
directories on demand without tracking placeholder files.

## F-2: Unique per-session directories

Add `.harness/scripts/create_agent_session.py` with Python's standard library.
Resolve an optional `--root` (default current directory), create the reserved
parent, then use `tempfile.mkdtemp` with a UTC timestamp prefix. Exclusive creation
provides collision-safe unique directories even for closely timed sessions.
Print one absolute path on success for the agent to retain as its session
workspace. Invoke once per new session and reuse the returned path throughout
that session. The helper does not infer session identity from undocumented
environment variables or create a persistent global current-session pointer.

## F-3: Discovery, skill guidance, and validation

Add `At the start of every session` to AGENTS.md with one reference to
`.harness/agents/scratch-space.md`. That file owns the creation command,
workspace reuse, artifact placement, and preservation instructions. Put the
reusable authoring contract in the skill's scratch-space reference and link it
conditionally from SKILL.md. Keep human files and other sessions undisturbed;
reading or editing human-supplied material still follows the user's task scope.
Keep feature definitions/design/history in `.harness/features/`, and promote
reusable scripts into `.harness/scripts/` with appropriate behavioral tests.

Route scratch provisioning, helper, and ignore-rule changes from VALIDATE.md to
a specialised scratch-space ruleset. It checks actual ignore semantics and
session creation behavior; use full-suite results when already current instead
of repeating the same tests. Unrelated edits to ignored ad hoc notes do not
activate project scratch-implementation checks.

## NF-1: Non-destructive focused creation

Use mkdir with exist_ok only for the parents and exclusive creation for the
session directory. Never overwrite or clean another directory. Reject a
symlinked scratch or reserved parent so the helper cannot quietly put its
artifacts outside the selected project. Report filesystem errors with a nonzero
exit status and a useful diagnostic. No third-party dependency is needed.
The helper only creates directories; it does not execute ad hoc scripts.

## Verification

Exercise the CLI in isolated temporary project directories. Confirm that each
returned path exists below the reserved parent, repeated invocations differ,
existing human/session files remain intact, explicit project roots work from
another directory, and invalid file/symlink parents fail without overwriting
existing data. In an isolated Git repository using the actual ignore file,
verify both root and nested scratch artifacts are ignored and project sources
remain trackable. Run the full harness suite, instruction-link checker, skill
validator, and semantic lifecycle/trigger reviews before marking the feature
DONE. Create this session's real workspace using the helper after installation.
