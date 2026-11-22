# Design Interviews

## Before making or expanding a project change

- Complete the Grill With Docs workflow below before changing any project artifact. Cover code, tests, documentation, configuration, dependencies, data, and the harness itself, including these instructions. Apply it to additions, edits, removals, and changes made by tools or delegated agents.
- Review related edits together, including expected tests, documentation, and feature records. Revisit the interview before acting on a newly discovered decision or expanding the agreed scope. Use read-only inspection and agent session setup or files in the scratch workspace to prepare.

## When using Grill With Docs

1. Invoke [Grill With Docs](../../.agents/skills/grill-with-docs/SKILL.md) explicitly and load [Grilling](../../.agents/skills/grilling/SKILL.md) and [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md). If the runner has no skill invocation tool, open those files directly.
2. Resolve factual questions from the repository and available tools. Compare the proposed change with the project's existing rules, interfaces, and documented decisions. Use the human's explicit instructions and earlier answers as settled decisions. When the scope and effects are settled, carry them into the edits.
3. For each open decision, identify what it affects, its prerequisites, and a recommended answer. Ask every question through [Human Interaction](../../.agents/skills/human-interaction/SKILL.md), with a separate field for each independent decision. Wait for answers and use follow-up pages for choices that depend on them. Use the skill's structured conversation fallback when the local form is unavailable. Confirm that the resulting scope and effects are agreed before applying related edits.
4. Follow the project's glossary and design records. Capture agreed terminology and durable trade-offs in the target's designated docs within the agreed scope.

## When adopting this workflow from a portable package

- Use the bundled copies during planning. Apply the [third-party skill standard](third-party-skills.md) when adopting the workflow into the target. Install the selected Matt Pocock skill directories through the pinned CLI using `mattpocock/skills@d1478fcb140db0b93c0c8df17bcfd311844749d0`. Keep the target project's generated skill lockfile, the installed files, and [the upstream MIT notice](../../docs/licenses/matt-pocock.txt) together. Verify existing locked copies before reusing them.
- Add or merge a required trigger in the target project's active agent entry point before every project change and explicit use of Grill With Docs. Point it to this installed workflow. Check the route for a routine edit, a change to the harness, and a read-only task.
