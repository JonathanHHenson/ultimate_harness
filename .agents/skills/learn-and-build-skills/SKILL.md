---
name: learn-and-build-skills
description: Research an unfamiliar repeatable workflow and turn verified findings into an agent skill, or investigate why an existing skill underperforms before revising it. Use for evidence-based skill authoring, including comparing approaches, testing counterexamples, and checking transfer.
---

# Learn and Build Skills

Produce a reusable workflow grounded in sources and observed outcomes. Keep research, prototypes, and evaluation artifacts in the agent session's scratch workspace when available. Otherwise use a separate writable staging directory. Respect the user's requested destination and scope.

## Learn the workflow

1. Define the recurring task, intended runtime, supplied inputs, expected output, and what success looks like. Identify what an existing skill, the local docs, or the agent's default workflow already handles. Keep a realistic variant aside for testing.
2. Use [learn-a-topic](../learn-a-topic/SKILL.md) to investigate the workflow and its alternatives. Carry the supported procedure, prerequisites, failure boundaries, and unresolved questions into skill authoring.

Begin authoring when you can explain the chosen procedure, say when a rival is better, identify its failure boundaries, and support the consequential steps. Narrow unverified scope or report a blocked check when evidence is unavailable.

## Build and verify the skill

1. Read [authoring and evaluation](references/authoring-and-evaluation.md). Reuse or extend an existing skill when it covers the workflow. Preserve the agent's judgment where approaches vary and write explicit steps where an error would have a concrete cost.
2. Package only guidance that changes future behavior. Keep discovery metadata distinct from execution instructions. Link conditional details and isolate stable mechanical work in small helpers only when they add value. Keep raw research and eval results in staging.
3. Check format and links, then test discovery and task outcomes separately. Exercise a normal case, a near miss, and a variant or failure case as appropriate. For claims of improved performance, compare matched runs with and without the skill or against its previous version. Revise from observed failures.
4. Deliver the requested skill and report the evidence supporting it, the checks actually run, and any unresolved limits. Keep unverified instructions scoped to the conditions you can support.

## When authoring a language skill

Follow the [language skill authoring guide](references/language-skills.md) to create, adopt, or update the dedicated skill for a language used by the project.
