---
name: install-harness
description: Set up a new programming agent harness in a project through a conversation about the team's workflow, validation, and conventions. Use when the project has no established harness and the user wants a tailored first installation.
---

# Install a Harness

## Agree on the first setup

1. Identify the target root, applicable agent instructions, project docs, toolchain, and configured build, lint, and test commands. Read inherited and scoped rules. If a harness already serves the project, explain what you found and ask which parts the user wants to evolve before editing.
2. Describe a small initial setup suited to the team's actual workflow. Ask which recurring events should have instructions, which checks belong at handoff, and whether to add feature memory, scratch workspaces, isolated harness Python, or reusable skills. Ask only about consequential choices the project and user have yet to settle. Use the answers to refine the plan.
3. Confirm the agreed capabilities, target locations, and any effects on existing files or dependencies before applying the plan. Treat explicit choices the user has already made as settled. When a choice is still open, wait for the answer before applying it.

## Assemble the selected components

- Read the [component catalog](assets/harness/catalog.toml) in this built skill. Copy only the agreed components from `assets/harness/` to the project, preserving relative paths or adjusting linked paths for the target runtime. The catalog's `requires` lists apply to copying components intact. If a project-native equivalent meets a dependency, adapt the affected references and behavior. If the catalog is missing, obtain the built skill package before relying on its files.
- Write a short project entry point, usually `AGENTS.md`, with event headings and links to the applicable rules. Keep project facts and detailed explanations in project docs. Link only to installed material or existing project guidance.
- Where validation or feature memory is selected, link an existing project validation entry point or write a focused index with triggers, actual commands, and expected results. When adopting both review rules, route code changes to code and security review, configuration-only changes to security review, and prose-only changes to the relevant document checks. Use the target project's environments and available checks.
- For the scratch component, ignore `/.scratch/`. For harness Python, ignore `/.harness/.venv/`, `/.harness/.venv.lock`, `/.harness/.uv-cache/`, and Python bytecode. For feature memory, track dated feature records and ignore only the feature store's `.locks/`, per-feature `.status-pending.json`, and `.write-*` files. Merge the selected entries into the existing ignore file. Adapt the chosen conventions if the project has different paths.
- Keep harness dependencies isolated from application dependencies. If selected, route session setup to harness Python before helpers that need it. If using feature memory, establish where the project keeps decisions and verification evidence, and link them at feature closeout. Provide the standalone merge check only when selected. Leave CI setup to the project unless the user also asks for it.

## Verify the installed workflow

- Walk through a fresh session and a representative change. Confirm the entry point finds the right rules, paths resolve, documented checks are runnable, and unrelated rules stay out of the flow.
- Exercise installed helpers in a disposable project or using safe test inputs. For feature memory, verify creation and lookup of a dated record and the selected merge check. For scratch, verify reuse and ignore behavior. Use the target project's validation commands for its code and configuration.
- Summarize the choices implemented, files added or adapted, completed checks, and prerequisites or decisions the team still needs to resolve.
