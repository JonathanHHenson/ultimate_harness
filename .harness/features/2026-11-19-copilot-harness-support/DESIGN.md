# GitHub Copilot review instructions

## REVIEW

Put the PR reviewer entry point in a GitHub path-specific instructions file with a repository-wide glob and cloud-agent exclusion. Reuse .harness/VALIDATE.md for scope and the existing code and security rulesets for details. Carry a concise fallback so a review with limited repository access still focuses on actionable regressions. Treat CI checks for the reviewed commit as evidence, distinguish unverified checks, and avoid author-side state changes. Bundle the guidance as a selectable component that brings the two review rulesets for intact installs. Verify links, package contents, and review routing locally.
