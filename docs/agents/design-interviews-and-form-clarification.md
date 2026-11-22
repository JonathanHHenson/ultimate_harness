# Design interviews and form clarification

## Decisions

- Installed Grill With Docs, Wait What, and the required Grilling and Domain Modeling dependencies from Matt Pocock’s `v1.3.2` commit. The skill lockfile records exact pins and content hashes. The portable packages include the documented dependencies and upstream MIT notice; adopting repositories generate their own skill lockfile. [Skill lock](../../skills-lock.json) · [Upstream release](https://github.com/mattpocock/skills/releases/tag/v1.3.2) · [MIT notice](../licenses/matt-pocock.txt)
- Codebase and harness design route to the same contextual instructions as portable install and evolution. Research answers factual questions. The form collects independent design decisions and adaptations before edits. [Design interviews](../../.harness/agents/design-interviews.md)
- Every question page can ask the waiting agent to re-explain it. The form records optional feedback as a separate clarification request. The agent uses Wait What for the same decision, checks the revision, and sends it back to the same page. The server verifies the revision and the decision fields, and the browser preserves its drafts. [Form workflow](../../.agents/skills/human-interaction/references/form-schema.md#clarification-requests)

## Verification

- Compared all four installed directories with the selected upstream tree and verified their CLI lock entries and license. Built and extracted both packages, checked the linked guidance and metadata, and verified that the source repository’s lock is excluded from the portable payload.
- Exercised both bundled servers with Chromium at 390 px and 1120 px. Each accepted a blank and a written clarification, served two revisions, preserved draft text, radio, checkbox group, range, and checkbox answers, then showed confirmation and exited.
- Keyboard dismissal returned focus to the clarification button. The exercise drove the documented agent-side commands with prepared rewrites.
- Loopback tests cover request and answer ordering, stale revisions, distinct events for submissions and clarification requests, optional feedback, writes through the authorized control endpoint, decision schema enforcement, and hard expiry. Origin, local address, and agent authorization checks apply to the new routes. Feedback stays in the private scratch workspace until resolved. Ruff, JavaScript complexity, HTML and CSS validation, and the full harness suite passed.

## Pre-change routing

- The root trigger applies before every project change, including routine edits, tool-driven changes, and edits to the harness. The agent runs Grill With Docs and reuses settled decisions. Open choices go through Human Interaction before related edits. Read-only work and local session setup can proceed, and expanded scope returns to the interview. The portable skills add or merge this trigger when adopting the workflow. [Root trigger](../../AGENTS.md#before-making-any-project-change-or-using-grill-with-docs) · [Pre-change workflow](../../.harness/agents/design-interviews.md)
- Three fresh Codex sessions exercised a disposable project with the candidate root instructions. The agent opened all three interview skills before making a specified harness heading change. A read-only task opened the project policy without invoking the interview. An unresolved policy change loaded Human Interaction and asked a structured question while keeping the document untouched. The one-shot test used the conversation fallback. File digests confirmed the expected changes in each case.
- Walked through an expanded change that exposed a new decision and traced both portable installation routes to the shared instructions. Both rebuilt archives, package metadata, Markdown links, and the four builder tests passed.
