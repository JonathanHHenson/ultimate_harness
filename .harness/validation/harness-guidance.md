# Harness Guidance Validation

## After changing agent instructions, skills, portable packages, validation rules, or the harness overview

- From the project root, run `.harness/.venv/bin/python .harness/scripts/check_markdown_links.py README.md AGENTS.md docs .harness/agents .harness/references .harness/VALIDATE.md .harness/validation .agents/skills .github/instructions`.
- Review each active `##` heading in `AGENTS.md`, `.harness/agents/`, `VALIDATE.md`, and `.harness/validation/`: require a concrete contextual trigger and relevant, concise instructions. Keep background in linked documentation.
- Walk through a matching situation and an unrelated one. Confirm that the intended rules load, unrelated rules do not, and overlapping situations apply all matching rulesets. Ensure the validation index routes to each situation-specific ruleset.
- Confirm each validation action has the prerequisites, command or review steps, and observable completion criteria needed to run it. Check that its commands and targets exist; remove obsolete rules when their situations disappear.

## After adding or updating skills, harness instructions, or project documentation

1. Read the [project glossary](../../GLOSSARY.md) and create `glossary-review.md` in the current [scratch workspace](../agents/scratch-space.md) before reviewing terminology. List the added and changed first-party prose in scope, including skill metadata and references, instruction headings, and documentation. If a glossary definition changes, include affected uses in existing prose.
2. **Review each skill description as its own field.** Read the complete YAML `description` of every new skill and every changed description, including continuation lines. Before reviewing a skill body, quote each harness term as written in its description. For each quoted term, record the action or object it names, the glossary entry that fits, and a verdict. Keep the quoted wording separate from the interpretation. A correct term in the body cannot resolve an incorrect term in the description. Record a verdict for each description, including those with no glossary terms. For example, the definition, design, and worklog for one feature make up a **feature record**. A **feature store** contains a collection of records.
3. **Check meanings before names.** For each remaining affected passage that uses a harness term, record what the term refers to and which glossary definition supports that role. Compare similar entries even when the written term already appears in the glossary. Then check the names and listed aliases separately. Mark a use as a mismatch when the term or its stated role conflicts with the glossary in context. Keep compatible wording and treat optional clarifications as suggestions. Preserve literal interface names, command output, quotations, and pinned upstream skill text.
4. Complete both passes, correct mismatches, and recheck the revised passages. Report any remaining finding with its location, current term, and intended concept. For a new or redefined concept, settle its meaning through the [design interview instructions](../agents/design-interviews.md) and update the glossary and affected prose together.
5. Before passing the check, reopen the saved note. Verify that it covers the scope and includes the written terms and verdict for every affected description. Include all unresolved mismatches and the note's path in the handoff, even when there are no mismatches. If you cannot save the note, report the glossary check as incomplete.

## After moving or renaming guidance or changing its headings

- Find affected incoming references and links inside the changed files. Resolve each from its stated base and confirm it reaches the intended document and section, including reference-style links, fragments, and plain-text paths. Fix mismatches and repeat the affected checks.

## After adding, moving, removing, or editing a skill

- From the project root, run `.harness/.venv/bin/python .harness/scripts/check_skill_packages.py`. Require all project skills to pass the metadata and instruction checks.
- Review changed discovery descriptions, skill links, and conditional references by walking through when they should be used.

## Before considering changed guidance validated

- Require successful commands and completed semantic reviews above. The reference checker verifies local inline file targets. Review command paths and any unsupported link styles, anchors, or external references affected by the change.
- Fix broken references, ambiguous triggers, or failed checks and repeat affected checks. If a prerequisite or installed validator is unavailable, record the missing check and blocker in the feature worklog; do not report it as passed.
