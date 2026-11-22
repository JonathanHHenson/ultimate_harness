# Third-party skill management

## Research and decisions

The published Vercel `skills@1.9.0` CLI accepts a full Git commit as the source ref. An isolated installation created `.agents/skills/find-skills/SKILL.md` and a version-2 `skills-lock.json` entry containing the pinned ref, resolved commit, and content hash. Both paths are visible to Git. Codex and GitHub Copilot use the same project skill directory. [Tagged CLI reference](https://github.com/vercel-labs/skills/blob/v1.9.0/docs/commands.md)

Track installed files so ordinary checkouts are self-contained. Use the generated lock for source provenance, content verification, and recovery. Prefer explicit repinning over updating a moving upstream ref. The CLI pin lives in one shared procedure, which avoids adding Node package management or a runtime setup step to every adopting project.

## Requirement coverage

- **POLICY.** Add a contextual procedure that covers provenance, collision checks, project-scoped install and update with the exact CLI and upstream pin, reviewed Git changes, and verification. Keep unmanaged authored skills separate from the CLI's ownership. Make it discoverable from the active harness. Use the published lock restore in disposable checkouts when needed.
- **ADOPTION.** Export the shared procedure as one default catalog component. Both portable skills explicitly recommend the same standard. Installation wires it into the target's contextual instructions. Evolution inventories existing skills, locks and source pins, preserves local edits, and gets agreement on any change of owner or version before migrating. Adopting the standard does not require selecting any third-party skill.

## Verification

Use a disposable repo to exercise pinned installation, tracked file and lock behavior, offline checkout, drift detection, frozen restore, and targeted removal. Use both extracted packages and verify their routes, catalog dependency coverage, and exclusion of source-project or fixture data. Review the instructions against an existing conflicting skill and a repo without imported skills.
