# Portable harness skills

## Decisions

- The initial release shipped separate entry points for first installation and selective evolution. The current package supports both workflows and keeps evolution's existing-file and record preservation requirements. [Install Harness](../../skills_src/install-harness/SKILL.md)
- Build both generated payloads from a single allowlist of live files. Keep the source project's entry point, validation index, documentation, history, tests, local data, and workflows outside the payload. Move the feature memory contract alongside its commands so feature memory can be adopted with isolated Python alone. Retain the old contract link for historical feature records. [Catalog](../../skills_src/harness-files.toml) · [Feature memory contract](../../.harness/references/feature-memory.md)
- Build and test on GitHub Actions with read-only repository access, pinned actions, and checkout credentials disabled after checkout. Archive each skill to preserve hidden directories and executable modes. [Packaging workflow](../../.github/workflows/build-harness-skills.yml) · [Artifact action](https://github.com/actions/upload-artifact/tree/bbbca2ddaa5d8feaa63e36b76fdaad77386f024f)

## Verification

- All 51 harness tests passed. The builder tests compared bundled files to live source bytes, checked exclusions, verified stale-file removal, and exercised missing and redirected paths. Both built entry points passed package and link validation. Type checking and the language server found zero errors in the two new Python files. [Builder tests](../../.harness/scripts/tests/test_build_harness_skills.py)
- Independent fixture trials exercised a first install and selective evolution. The final install used only feature memory and isolated Python, passed the existing project test and link checks, and created and advanced a dated feature. Dependency downloads were unavailable in the test environment, so the fixture used locally available copies. The evolution trial added a configuration security review to the existing handoff, preserved the project's Python test and record, and traced source-only, config-only, mixed, and prose-only paths.
- The local archive step produced two archives. Each held 38 files, including hidden harness paths and an executable feature merge check. Workflow syntax and read-only permissions were reviewed locally. Hosted execution and artifact publication remain unverified because this checkout has no GitHub remote.
