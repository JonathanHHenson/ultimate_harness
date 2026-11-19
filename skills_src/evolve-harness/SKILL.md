---
name: evolve-harness
description: Improve an existing programming agent harness through a conversation about which practices to adopt. Use when the user wants selective changes to agent instructions, validation, feature memory, scratch, or skills while preserving the project's established workflow.
---

# Evolve a Harness

## Agree on one increment

1. Map the target's active instruction entry points, scoped rules, validations, installed skills, and persistent records. Trace the present workflow from trigger to command and outcome. Identify which rules and paths other tools rely on. If the project has no established harness, clarify whether the user wants a first installation.
2. Ask what is failing or taking too much effort and what conventions are important to keep. Describe the smallest useful change and offer a meaningful alternative where one exists. State which entry points, commands, or records it affects and what evidence would show improvement.
3. Confirm the selected change and any necessary integration or migration before editing. Carry forward choices the user already made. If a conflict appears that changes behavior, scope, or stored data, explain the options and wait for the user's decision on that conflict.

## Integrate the chosen practice

- Read the [component catalog](assets/harness/catalog.toml) in this built skill. Inspect only the selected files under `assets/harness/`. Its `requires` lists identify dependencies for intact copies. Reuse an existing capability when it meets the same need and adapt the selected instructions to its established paths and interfaces. If the catalog is missing, obtain the built package before relying on its files.
- Find the existing owner of each rule and amend it in place. Use a new contextual rule only when it gives the existing entry point a useful route. Merge with existing instructions, ignore rules, commands, and validation selection. Keep unrelated rules and integrations intact.
- For existing feature memory or scratch data, preserve history, ownership, and usable paths. Propose a migration only when needed by the chosen increment. Verify it on copies and get agreement on the mapping and recovery plan before changing live records.
- Add a new dependency, environment, or CI check only when the agreed change needs it. Verify its compatibility with the project's current runtime and workflows. Review existing and proposed behavior on overlapping triggers, such as a mixed code and configuration change.

## Verify and review the increment

- Trace a matching case and a nearby case. Confirm the chosen path runs the intended checks and that unaffected paths still produce their established results. Run existing checks and verify how the change coexists with current rules and records.
- Show the human the diff's effect, observed evidence, and any remaining compatibility or migration limits. Stop at the agreed increment and discuss further adoption separately.
