# Harness Guidance Validation

## After changing agent instructions, skill packages, validation rules, or the harness overview

- From the project root, run `.harness/.venv/bin/python .harness/scripts/check_markdown_links.py README.md AGENTS.md docs .harness/agents .harness/references .harness/VALIDATE.md .harness/validation .agents/skills`.
- Review each active `##` heading in `AGENTS.md`, `.harness/agents/`, `VALIDATE.md`, and `.harness/validation/`: require a concrete contextual trigger and relevant, concise instructions. Keep background in linked documentation.
- Walk through a matching situation and an unrelated one. Confirm that the intended rules load, unrelated rules do not, and overlapping situations apply all matching rulesets. Ensure each situational validation file has a route from `VALIDATE.md`.
- Confirm each validation action has the prerequisites, command or review steps, and observable completion criteria needed to run it. Check that its commands and targets exist; remove obsolete rules when their situations disappear.

## After moving or renaming guidance or changing its headings

- Find affected incoming references and links inside the changed files. Resolve each from its stated base and confirm it reaches the intended document and section, including reference-style links, fragments, and plain-text paths. Fix mismatches and repeat the affected checks.

## After adding, moving, removing, or editing a skill package

- From the project root, run `.harness/.venv/bin/python .harness/scripts/check_skill_packages.py`. Require all project skill packages to pass the metadata and instruction checks.
- Review changed discovery descriptions, skill links, and conditional references by walking through when they should be used.

## Before considering changed guidance validated

- Require successful commands and completed semantic reviews above. The reference checker verifies local inline file targets. Review command paths and any unsupported link styles, anchors, or external references affected by the change.
- Fix broken references, ambiguous triggers, or failed checks and repeat affected checks. If a prerequisite or installed validator is unavailable, record the missing check and blocker in the feature worklog; do not report it as passed.
