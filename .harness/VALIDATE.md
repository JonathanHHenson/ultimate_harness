# Project Validation

## Before validating a feature or harness change

- Select every matching situation below; follow its linked ruleset. Run commands from the project root.

## When changing agent instructions, skill packages, validation rules, or the harness overview

- Follow [the harness guidance checks](validation/harness-guidance.md).

## When changing harness scripts, CI check scripts, tests, or runtime dependencies

- Follow [the harness script checks](validation/harness-scripts.md).

## When changing scratch conventions, session creation, or the scratch ignore rule

- Follow [the scratch space checks](validation/scratch-space.md).

## Before choosing session-end reviews

- Identify the changes attributable to the session, or the specified patch for a handoff review. Account for additions, edits, and deletions, including staged, unstaged, and untracked changes.
- Classify the changes by purpose. Code includes executable source, tests, and scripts. Configuration includes dependency manifests and lockfiles, CI, infrastructure, deployment, and runtime settings. A file that supplies settings is configuration even when it uses a programming language.
- Use the first matching row below. Open only the listed review files and run the checks allowed by that row. Apply other validation triggers that match the actual changes.

| Session changes | Session-end reviews |
| --- | --- |
| Code, with or without configuration or documentation | [Code review](validation/code-review.md) and [security review](validation/security-review.md) |
| Configuration without code, with or without documentation | [Security review](validation/security-review.md) only. Run checks specific to the changed settings and the controls they affect. |
| Neither code nor configuration, including prose-only edits or no changes | Skip both reviews and their checks, including application and deployment checks. Validate the changed artifacts where applicable, then finish the handoff. |

## Before marking a feature DONE

- Verify every requirement's definition of done and complete all matching checks above. Resolve failures and blockers before claiming validation passed.
- Record the completion decisions and evidence in tracked documentation. Follow [the feature closeout instructions](agents/feature-memory.md#before-marking-a-feature-done).

## When checking a feature branch for merge

- Run `python3 scripts/check_features_done.py` with Python 3.11 or later. Require a successful exit. Resolve reported feature, requirement, or record problems before merging.
