---
name: build-harness
description: Build, review, or maintain a programming agent harness. Use for AGENTS.md and contextual instructions, feature memory, scratch workspaces, dynamic validation, isolated harness Python, or repository skills. Verify that changed rules lead agents to the right guidance and actions.
---

# Build and Maintain a Programming Harness

## Establish the scope

- Read the applicable `AGENTS.md`, project validation rules, and affected guidance or scripts. Identify the task or lifecycle event, the intended agent behavior, and the evidence that would show it works. For a maintenance change, trace the existing route from the trigger to the action before editing.
- Use [learn-a-topic](../learn-a-topic/SKILL.md) when unfamiliar behavior, an uncertain assumption, or a consequential choice needs investigation. Start with the repository's current contracts and tooling. Scale the investigation to the decision.
- Load the references for the affected areas. A small edit can proceed once the relevant contract and validation checks are clear.

## Choose the guidance and its home

| Concern | Destination and guidance |
| --- | --- |
| Project instructions and complex contextual rules | Keep clear event or path triggers in `AGENTS.md` and place detailed contextual rules in `.harness/agents/`. Follow the [agent instructions standard](references/agents-md.md). |
| Project facts, architecture, and rationale | Keep them under `docs/` and link from the work that needs them. |
| Reusable workflow | Use `.agents/skills/<name>/SKILL.md`. Use [learn-and-build-skills](../learn-and-build-skills/SKILL.md) to create a skill or materially change its workflow. |
| Feature definitions, designs, and progress | Track the records under `.harness/features/`. Put completion decisions and evidence for agents under `docs/agents/`. Follow the [feature memory contract](../../../.harness/references/feature-memory.md). |
| Project validation | Route matching situations from `.harness/VALIDATE.md` to focused rulesets in `.harness/validation/`. Follow the [dynamic validation standard](references/validation.md) when authoring or changing rules. |
| Local notes and session work | Use ignored `.scratch/` and unique `.scratch/agent_sessions/` workspaces. Follow the [scratch space contract](references/scratch-space.md) for provisioning and preservation. |
| Isolated harness dependencies | Use `.harness/.venv/` and the harness manifest. Follow the [Python environment contract](references/python-environment.md) for setup and harness execution. |
| Repeatable mechanical actions and their tests | Use `.harness/scripts/` for session and maintenance helpers, and `scripts/` for commands invoked by CI. Put harness behavior tests under `.harness/scripts/tests/`. Use [software-design](../software-design/SKILL.md) for script changes and [automated-test-design](../automated-test-design/SKILL.md) when designing tests. |

## Make the change

- Keep one maintained source for each rule or procedure. Give a linked instruction an explicit trigger and a clear action. Keep judgment in concise instructions and automate repeatable mechanical checks with a clear success or failure result.
- Reuse the project's existing components and structure. Add only what's needed for the requested behavior. When guidance moves, update its callers and remove superseded copies. When adding or changing automation, state the working directory, required inputs, expected result, and how to respond to failure.
- Track reusable guidance, scripts, project documentation, and feature records. Keep raw scratch data, temporary feature state, and the harness Python environment local. Follow the project's lifecycle and record substantive evidence in the feature closeout.

## Verify that the change works

- Follow an affected route as an agent would. For a changed trigger, walk through a matching task, a near miss, and an overlap if another rule can also match. Confirm which guidance loads and that all applicable actions can be completed. Check the target agent runtime when the rule depends on its discovery or precedence.
- For moved or renamed guidance, find affected references to and from it. Resolve them from their stated base to the intended document and section, including fragments, reference-style links, and plain-text paths. Check executable instructions from the documented working directory.
- Run every applicable project check. A passing structure or link check establishes only what it verifies. Exercise new or changed scripts through their normal entry points, including relevant failure paths. Distinguish passed, failed, and unrun checks and resolve or record the remaining gaps.
