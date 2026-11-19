# AGENTS.md Authoring Standard

Apply this standard to `AGENTS.md` and contextual instruction files under `.harness/agents/`. The skill itself and informational project documentation may use ordinary section headings.

## When writing an instruction file

- Keep it minimal, clear, and instructional. Use direct verbs; omit narrative, duplicated rules, and purely informational sections.
- Make every `##` heading a clear contextual trigger event. Tie instructions to project or feature lifecycles, relevant project context, styling, or restrictions.
- Use specific headings such as `## At the start of every session`, `## Before modifying files under hello/world/`, or `## When changing the database schema`.
- Replace topic headings such as `## Architecture`, `## Testing`, or `## Style` with the event that makes their instructions relevant.
- State when to read referenced documentation. Keep project descriptions, architecture explanations, and rationale in that documentation rather than copying them into instructions.
- Put generic workflows and reusable ad hoc tasks in skills. Do not encode an expanding catalog of task procedures in `AGENTS.md`.
- Do not use an always-triggered section to load guidance that belongs to a narrower context.

## When contextual guidance becomes complex

- Move that guidance to `.harness/agents/<descriptive-name>.md`.
- Add a short instruction under the relevant `AGENTS.md` trigger that explicitly requires reading the file.
- Keep the extracted file concise and instructional, with contextual `##` headings and links to informational documentation.
- Leave only routing and necessary short instructions in the parent file. Avoid duplicating the extracted rules or loading unrelated files.

## When an instruction requires a repeatable mechanical task

- Implement the task as a small, focused script in `.harness/scripts/`.
- Tell the agent which script to run under the relevant trigger, including its working directory or required arguments and how to respond to failure.
- Keep one clear responsibility per script. Separate independent tasks instead of creating a general-purpose harness runner without a demonstrated need.
- Make success and failure observable through useful output and exit status. Document material side effects where the caller needs to understand them.
- Add tests in `.harness/scripts/tests/` when input handling, failure behavior, or side effects make unit testing useful.
- Test correct behavior through outputs, exit status, and resulting state. Do not assert source layout, private function names, or exact wording unless that wording is part of the required interface.

## When checking the instruction structure

- Verify that each instruction has a concrete trigger and each reference resolves to an existing file.
- State the path base where references could be ambiguous, particularly inside nested `.harness/agents/` files.
- Check an applicable scenario and an unrelated scenario. Only applicable guidance should load.
- Review brevity by removing unnecessary content; do not impose an arbitrary line limit or a prose linter that claims to prove semantic quality.

## When adapting an example to a project

Use only sections that correspond to real project needs. The paths below are illustrative; create and verify their targets before using them in active instructions.

Example root `AGENTS.md`:

```markdown
# Agent Instructions

## At the start of every session

- Read `docs/project.md` for project context. Paths in this file are relative to the repository root.

## Before modifying files under hello/world/

- Read `.harness/agents/hello-world.md` and follow its applicable instructions.

## When changing the database schema

- Read `.harness/agents/database-changes.md` before editing migrations.
```

Example `.harness/agents/hello-world.md`:

```markdown
# Hello World Instructions

## Before modifying files under hello/world/

- Read `docs/hello-world.md` for the component contract and styling conventions. Paths here are relative to the repository root.

## After changing the public interface under hello/world/

- From the repository root, run `.harness/.venv/bin/python .harness/scripts/check_hello_world_contract.py`.
- Resolve reported contract violations before considering the interface change complete.
```
