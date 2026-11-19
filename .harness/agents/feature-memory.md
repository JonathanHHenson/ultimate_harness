# Feature Memory Instructions

## Before starting or resuming feature work

- Read `.agents/skills/build-harness/references/feature-memory.md` for the memory contract and script commands. Paths here are relative to the project root.
- Find the feature's unique directory under `.harness/features/`. Read its `DEFINITION.toml`, `DESIGN.md`, and `WORKLOG.yaml` before continuing; use the worklog to identify decisions, evidence, blockers, and the next action.
- For a new feature, create its record with `.harness/.venv/bin/python .harness/scripts/create_feature.py` before implementation. Never overwrite or merge another feature's memory.

## When researching or designing a feature

- Keep the definition, documentation links, and functional and non-functional requirements current. Give each requirement a detailed description and definition of done.
- Develop `DESIGN.md` to cover every requirement with a technical approach, interfaces, tradeoffs, failure handling, and verification strategy. Make unresolved questions explicit.

## When changing feature or requirement status

- Use `.harness/scripts/set_feature_status.py` or `.harness/scripts/set_requirement_status.py` from the project root; supply an informative reason. Resolve validation failures before continuing.
- Advance feature phases in order; return to an earlier phase when needed. Mark a feature DONE only after TEST, after every requirement is DONE, and after completing the applicable rules in [VALIDATE.md](../VALIDATE.md).
- Move requirements through TODO, WIP, and DONE. Record a detailed blocking reason when entering BLOCKED; resume the recorded prior state when unblocking.
- After an interrupted status update, run a feature command for that feature before editing its records by hand. The command recovers the pending definition and worklog. If recovery reports a conflict, preserve the records and reconcile the pending update before continuing.

## When progress changes what a future agent needs to know

- Update the affected definition or design and use `.harness/scripts/append_worklog.py` to record the outcome, evidence, decisions, blockers, or next action. Status scripts record their supplied reasons automatically.
- Coordinate direct edits to feature records with other writers.
- Add substantive, non-repetitive entries during the work, especially before handoff. Omit entries that add no useful information; preserve the existing history and append corrections when needed.
- Keep `.harness/features/` gitignored. Do not force-add local feature memory; promote durable shared knowledge into tracked project documentation when needed.
