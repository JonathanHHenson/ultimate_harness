# Session-end code review

## Session route (CR-1)

Add paired lifecycle triggers to AGENTS.md and VALIDATE.md. The validation file points to a single ruleset for sessions where the agent wrote or changed code. Source, tests, and scripts are in scope. The trigger works independently of the feature lifecycle. All other matching validation rules still apply.

## Diagnostics and architecture (CR-2)

Review the session's changes, including added files, and use available read-only diagnostics with the project configuration and interpreter. Prefer existing project commands. If available, use basedpyright as a fallback for harness Python. Record unavailable tool categories and continue the manual passes. Use the existing software-design skill for architecture and behavior and recheck changes made during review.

## Cleanliness and verification (CR-3)

Review control flow, responsibilities within large files, and cohesion across nearby files as distinct signals. Respect existing project limits. Where no limit is set, require a concrete design or readability reason for a change. Verify reachable triggers and use a small type-checker example plus scenarios for branch nesting, unrelated responsibilities, and loose collections of files. Keep research and examples in scratch.
