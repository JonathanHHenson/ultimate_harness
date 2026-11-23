---
name: install-harness
description: Install or evolve a programming agent harness. Use for a first harness, an upgrade to existing agent instructions or validation, or a merge with incumbent workflows. Research the target, propose full component coverage, and tailor it through separate human decisions.
---

# Install or Evolve a Harness

## Before choosing a route

1. Use the bundled [Learn a Topic skill](assets/harness/.agents/skills/learn-a-topic/SKILL.md) and [adoption guide](assets/harness/.agents/skills/build-harness/references/adoption.md) to research the full export catalog and the target project's technical, team, and delivery practices. Keep the target read-only during research and planning.
2. Choose the route based on the active instructions, validation, tooling, and records you find. Use first installation for a project without an established harness. For an existing harness, trace incumbent triggers, commands, data, and callers before proposing integration.
3. Start from every component in the [export catalog](assets/harness/catalog.toml) on either route.

## Before drafting either adoption plan

1. Invoke the bundled [Grill With Docs skill](assets/harness/.agents/skills/grill-with-docs/SKILL.md) directly on both routes, including when the user requests only a plan. If the skill tool cannot invoke the bundled copies, open that file directly and apply it by opening [Grilling](assets/harness/.agents/skills/grilling/SKILL.md) and [Domain Modeling](assets/harness/.agents/skills/domain-modeling/SKILL.md).
2. Use those skills and the bundled [design interview instructions](assets/harness/.harness/agents/design-interviews.md) to examine the proposed changes against the target's documented decisions and terminology. Resolve factual questions from the evidence and carry the open choices into the initial question set.

## When installing the first harness

- Plan the target-owned entry points and configuration. Include feature memory with dated feature records, the feature merge check, scratch workspaces, isolated harness Python, language skill routing, and situation-based validation.
- For each distinct fit issue, use target evidence to explain the effects of installation, adaptation, leaving the capability inactive, or exclusion where viable. Recommend the most useful coverage and let the human choose.

## When integrating an existing harness

- Compare every portable component with incumbent behavior. Keep verified equivalents, add missing components, and merge overlapping practices when compatible. Preserve active triggers, project guarantees, useful interfaces, and existing records. Keep one owner for each rule.
- When a merge is impractical, propose a targeted replacement. Explain preserved and lost behavior, affected callers, data or configuration migration, cutover, and recovery. Offer retention or deferral with the remaining gap explained. Get explicit agreement on material replacements and data changes.
- Inventory existing skill managers, skill lockfiles, pins, discovery paths, and local modifications. Present each migration as its own decision. Verify candidate files against the approved upstream commit before transferring ownership. For a changed local skill, offer to retain the local customization, use an approved pinned fork, or replace it with the reviewed upstream version.

## When agreeing on either plan

- Propose separate project-specific skills and validation rulesets grounded in the research. Recommend the [third-party skill standard](assets/harness/.harness/agents/third-party-skills.md). Ask separately about each proposed import, including its source, pin, and purpose, and about connecting the feature merge check to CI.
- Use bundled [Human Interaction](assets/harness/.agents/skills/human-interaction/SKILL.md) and the [decision-page instructions](assets/harness/.agents/skills/build-harness/references/adoption.md#before-showing-a-design-decision-page) to prepare separate choices and editable defaults, including known conditional preferences. Ask a follow-up only when an answer exposes a new material decision.
- Keep material choices for availability and activation separate on both routes. Give separate choices for installing and routing the code and security review rulesets, including Copilot instructions and activating hosted review, and including design interview guidance and requiring interviews. Record settled constraints without asking for acknowledgement.
- Before building the page, map each proposed language skill to its own field. Apply this to configuration languages too. If you propose YAML and TOML language guidance, give each language its own skill and yes-or-no decision with concrete effects.
- Review the draft choices for independent effects, including project-specific additions. If the human could accept one proposed check or trigger and decline another, give each its own field on the same page. For example, a regression check after a code change and an acceptance check before an operational action are separate decisions even if they use the same evidence.
- Use Human Interaction's format choice before asking the decisions. For chat, follow the [chat instructions](assets/harness/.agents/skills/human-interaction/SKILL.md#when-the-human-chooses-chat). For a form, require both the schema and answer-option checks before publishing, updating, or revising each page, then use the [form handoff](assets/harness/.agents/skills/human-interaction/SKILL.md#when-the-human-chooses-a-form). Wait for the human's answers and reconcile dependencies and unsettled scope before editing the target.

## When applying and verifying the agreed plan

- Copy approved portable material and write or amend the target's entry points, ignore rules, validation index and rulesets using the [adoption guide](assets/harness/.agents/skills/build-harness/references/adoption.md). On evolution, amend the active files in place where practical. Preserve unrelated files, rules, data, paths, and integrations. Verify proposed migrations and recovery on copies before touching live records.
- When the third-party skill standard is adopted, route to its installed instructions. Use the pinned CLI for approved imports, verify migrations and discovery paths before cutover, and verify that the skill files and generated `skills-lock.json` can be tracked together.
- When the design interview is adopted, add or merge the required pre-change trigger. Follow the [design interview adoption instructions](assets/harness/.harness/agents/design-interviews.md#when-adopting-this-workflow-from-a-portable-package) for the upstream skills, lockfile, pin, and notice. Apply the same pin and notice when adopting the form's clarification dependency on its own.
- Trace startup and matching, unrelated, and overlapping changes through the target's active entry points. Run available checks for installed and retained behavior, and verify links, language skill coverage, feature records, and affected callers where applicable.
- Report what was installed, merged, replaced, kept inactive, or excluded. Include choices, authored additions, verification results, remaining prerequisites, and any approved stages still pending.
