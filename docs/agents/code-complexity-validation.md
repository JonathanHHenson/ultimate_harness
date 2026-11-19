# Language skills and complexity validation

## Decisions

- Require complexity evidence for each changed executable language. Prefer the project’s configured analyzer and limit. Use the relevant language skill or a documented manual count when the language has no configured analyzer. The default limit is 10. Keep review open if an affected unit lacks evidence or exceeds its limit. [Review requirement](../../.harness/validation/code-complexity.md)
- Give Python, JavaScript, HTML, CSS, and shell separate skills. Route repository work through a short language index. Export the language components independently and keep their reusable helpers in the corresponding skills. [Language guide](../../.harness/agents/languages.md) · [Export catalog](../../skills_src/harness-files.toml)
- Run the installed Python checker and pinned JavaScript, HTML, and CSS tools in the existing packaging workflow. Check shell syntax with the declared interpreter. Keep the Node tools in validation and keep the form runtime on Python and browser APIs. [Local validation](../../.harness/validation/harness-scripts.md) · [Packaging workflow](../../.github/workflows/build-harness-skills.yml) · [ESLint complexity rule](https://eslint.org/docs/latest/rules/complexity)

## Verification

- The Python helper rejected four functions in the earlier form schema and passed 217 functions across 27 maintained Python files. The JavaScript helper rejected six former renderer functions, with scores from 11 to 21, and passed the refactored assets. It also failed when ESLint skipped a file outside the expected root. HTML validation, the CSS lint rules, and shell syntax checks passed. For the changed shell code, a manual count found one branch in the CSS launcher’s error guard and one loop in the CI validation block.
- Chromium matched the original and refactored form markup, Markdown, Mermaid diagrams, desktop and mobile columns, saved submissions, and shutdown behavior. All 64 harness tests passed. Python type and language-server checks reported zero errors in the changed files.
- Replayed the packaging workflow’s local commands. Both extracted packages contained the five skills, resolved their links, and ran the bundled Python, JavaScript, HTML, and CSS validators. Both extracted harness skills ran their local form flows. Hosted execution remains unverified for these changes.

## Language skill authoring and review coverage

Code review checks the full project language inventory and requires a discoverable skill for each language. Learn and Build Skills owns the authoring and verification procedure. Build Harness and the project language inventory route through that skill. Code review includes the authoring component as a portable dependency so projects can resolve missing language coverage. [Review gate](../../.harness/validation/code-review.md#before-running-code-review-diagnostics) · [Authoring guide](../../.agents/skills/learn-and-build-skills/references/language-skills.md)

Walked through an existing language, a mixed-language change, and a newly introduced language without a skill. Review proceeds through the applicable skills for the first two and remains open until the missing skill is supplied for the third. Verified the indirect route and heading locally. Both portable packages resolved the authoring guide when adopting code review on its own and when adding Build Harness. All four builder tests and the package metadata and link checks passed.

## Ruff preference

Ruff is the preferred Python tool for linting, formatting checks, and complexity. The harness and CI use the repository’s Ruff policy with baseline lint rules and C901 at a maximum of 10. CI pins the Ruff action and CLI version. The Python package provides the standard-library complexity checker as a fallback. [Ruff configuration](../../ruff.toml) · [CI step](../../.github/workflows/build-harness-skills.yml) · [C901 rule](https://docs.astral.sh/ruff/rules/complex-structure/)

Ran Ruff 0.17.6 using the CI arguments and confirmed that all 27 maintained Python files were included and passed. The previous form schema failed C901 on both `field_definition` and `field_value`. Both rebuilt packages contained the Ruff guidance and fallback. Package metadata, links, and all four builder tests passed. The updated hosted workflow has yet to run.
