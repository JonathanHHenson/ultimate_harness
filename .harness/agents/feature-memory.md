# Feature Memory Instructions

## Before starting or resuming feature work

- Read [the feature memory contract](../references/feature-memory.md) for the record format and commands. Paths here are relative to the project root.
- Find the feature's `YYYY-MM-DD-<slug>` directory under `.harness/features/`. Read its `DEFINITION.toml`, `DESIGN.md`, and `WORKLOG.yaml` before continuing; use the worklog to identify decisions, evidence, blockers, and the next action.
- Before implementing a new feature, pass its lowercase kebab-case slug to `.harness/.venv/bin/python .harness/scripts/create_feature.py`. The script adds the UTC date and prints the new path. Never overwrite or merge another feature's memory.

## When researching or designing a feature

- Keep the definition, documentation links, and functional and non-functional requirements current. Give each requirement a detailed description and definition of done.
- Develop `DESIGN.md` to cover every requirement with a technical approach, interfaces, tradeoffs, failure handling, and verification strategy. Make unresolved questions explicit.

## When changing a feature phase or requirement status

- Use `.harness/scripts/set_feature_status.py` or `.harness/scripts/set_requirement_status.py` from the project root. Pass the full dated directory name and an informative reason. Resolve validation failures before continuing.
- Advance feature phases in order; return to an earlier phase when needed. Mark a feature DONE only after TEST, after every requirement is DONE, and after completing the applicable rules in [VALIDATE.md](../VALIDATE.md).
- Move requirements through TODO, WIP, and DONE. Record a detailed blocking reason when entering BLOCKED; resume the recorded prior state when unblocking.
- After an interrupted feature phase or requirement status update, run a feature command for that feature before editing its record by hand. The command recovers the pending definition and worklog. If recovery reports a conflict, preserve the files and reconcile the pending update before continuing.

## Before marking a feature DONE

- Update project documentation under `docs/` for changes to shared behavior, interfaces, or architecture.
- Write or update the feature closeout documentation under `docs/agents/`. Capture decisions and their rationale, the checks that ran and their outcomes, and any unverified scope. Use durable repository references. Keep raw agent session artifacts in the scratch workspace.
- Link the closeout documentation and relevant project docs from the feature definition. Include those docs and the feature record in the same change.

## When progress changes what a future agent needs to know

- Update the affected definition or design and use `.harness/scripts/append_worklog.py` with the full dated directory name to record the outcome, evidence, decisions, blockers, or next action. Status scripts record their supplied reasons automatically.
- Coordinate direct edits to feature records with other writers.
- Add substantive, non-repetitive entries during the work, especially before handoff. Omit entries that add no useful information; preserve the existing history and append corrections when needed.
- Keep feature definitions, designs, and worklogs ready to commit under `.harness/features/`. Keep secrets and checkout-specific artifact references out of these records.
