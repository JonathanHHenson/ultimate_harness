---
applyTo: "**"
excludeAgent: "cloud-agent"
---

# Harness pull request review

## When choosing the review scope

- Review the whole pull request diff, including deletions and mixed changes. Use the project's [review selection table](../../.harness/VALIDATE.md#before-choosing-session-end-reviews). Classify files by what they do. Workflow files, dependency manifests and runtime settings are configuration.
- If the table is unavailable, apply [code review](../../.harness/validation/code-review.md) and [security review](../../.harness/validation/security-review.md) to source or test changes. For configuration-only changes, apply security review to the changed settings and controls. For prose-only changes, check changed guidance, links and inconsistencies relevant to the pull request.

## When reviewing the changes

- For code, trace the changed behavior through callers and affected interfaces. Look for correctness and maintainability regressions and missing tests of observable behavior, including failures and boundaries.
- For code or configuration, trace affected inputs, trust boundaries, permissions and effective settings. Use STRIDE for relevant threats and OWASP guidance for affected web controls. Even if linked context is unavailable, review the visible diff using these prompts and qualify findings that depend on missing context.
- Keep review read-only. Use available test, lint, type-check and security results for the reviewed commit. Distinguish visible evidence from checks whose results you could not verify. Leave author-side setup, feature updates and the full validation run to the coding agent and CI.

## When writing review comments

- Report actionable findings introduced or exposed by this change. Anchor each on the relevant line and explain the triggering condition, impact, and a focused correction. Prioritize material defects and security risks. Qualify evidence gaps that materially limit the review.
