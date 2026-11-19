# Portable harness skills

## SKILLS

Provide separate workflows for a new installation and an existing harness. Both start by reading local instructions and asking the human to choose the components and project conventions that matter. Installation authors the target entry point and validation routing. Evolution maps a selected outcome to the incumbent layout and preserves current commands, rules, and records. Both leave project CI setup to the target project.

## EXPORT

Use a shared TOML catalog with explicit repository-relative files grouped by capability and with dependencies between components. Copy byte-for-byte into each skill's generated assets, including the catalog so the artifact works by itself. Regenerate the payload tree to remove stale files. Refuse missing, nonregular, or redirected inputs before publishing. Leave the target project's entry points, rules index, Docs, ignore rules, and CI vendor configuration to its agent and human. Keep history, caches, local scratch, and source-repository maintenance checks out of the catalog.

## CI

Build both packages on a GitHub-hosted runner without write permission to repository content. Validate the built entrypoints and publish an archive per skill. Archive at the skill directory so executable modes and hidden harness directories survive extraction. Test the build, rebuild, rejection, extracted content, and application to isolated fresh and existing fixtures.
