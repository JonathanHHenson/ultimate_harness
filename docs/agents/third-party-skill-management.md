# Third-party skill management

## Decisions

- Pin Vercel’s CLI to `skills@1.9.0`. Pin Git sources to full commits and archive-only releases to a versioned URL and reviewed digest. Check in the complete imported skill and the generated skill lockfile `skills-lock.json` together. Regular checkouts already contain the reviewed skill. [Third-party skill instructions](../../.harness/agents/third-party-skills.md) · [Pinned CLI documentation](https://github.com/vercel-labs/skills/blob/v1.9.0/docs/commands.md)
- Export the shared procedure with Install Harness. Both routes separate adopting the standard from choosing an external skill. Evolution compares existing files and provenance before offering individual migration or replacement choices. The export catalog defines what travels with the workflow. [Install Harness](../../skills_src/install-harness/SKILL.md) · [Export catalog](../../skills_src/harness-files.toml)

## Verification

- Used the published exact CLI in a disposable repository. A pinned GitHub import created a version-2 lock record with the exact ref, resolved commit, and installed content hash. Codex and GitHub Copilot shared the copied folder. A local Git clone reproduced both committed files without a restore command.
- Editing the imported file caused `list --json` to report `modified`. Frozen restore recovered the reviewed bytes and preserved the lock. Targeted removal deleted the intended import and its lock entry while preserving a separately authored skill. The CLI also imported the published versioned harness archive with its license and bundled files intact and recorded its source URL and content hash.
- Built and extracted both packages and checked their links, metadata, exclusion of fixture files and lock, and the four packaging tests. Walked through a clean project, a project with an existing customized import, and ordinary source work. Import decisions stay separate from adopting the policy, conflicts route to an explicit migration choice, and ordinary source work does not open the import procedure.
